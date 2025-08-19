import asyncio
import dataclasses
import typing
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    TypeVar,
)

from camel_converter import to_snake
from gql.transport.exceptions import TransportQueryError

from validio_sdk._api.api import secrets_changed_by_field, split_to_n_chunks
from validio_sdk.client import Session
from validio_sdk.exception import ValidioBugError, ValidioError
from validio_sdk.resource._diffable import (
    ApiSecretChangeNestedResource,
    Diffable,
)
from validio_sdk.resource._errors import (
    ManifestConfigurationError,
    max_resource_depth_exceeded,
    updated_resource_type_mismatch_exception,
)
from validio_sdk.resource._resource import CREATE_ONLY_RESOURCES, DiffContext, Resource
from validio_sdk.resource._util import SourceSchemaReinference, _sanitize_error
from validio_sdk.resource.replacement import (
    CascadeReplacementReason,
    ImmutableFieldReplacementReason,
    ReplacementContext,
    ReplacementReason,
)
from validio_sdk.resource.segmentations import Segmentation
from validio_sdk.resource.sources import Source
from validio_sdk.resource.tags import Tag
from validio_sdk.resource.windows import TumblingWindow

if TYPE_CHECKING:
    from validio_sdk.code.plan import ResourceNames

# We want to control how the schema inference requests scale, since it is an operation
# that interacts with external systems (not only the validio backend), therefore
# it shouldn't scale together with the other requests
NUM_CONCURRENT_INFERENCE_TASKS = 1

R = TypeVar("R", bound=Resource)

"""
When we descend into nested objects, we set a limit on how deep we go.
Otherwise, in a bad manifest configuration or due to a bug in our code, we
could enter a cycle.
"""
MAX_RESOURCE_DEPTH = 15


@dataclass
class ResourceUpdate:
    """
    Represents a resource that has an update. It contains the concrete class
    of the resource (e.g. TumblingWindow), followed by a representation of the
    manifest and server's version of the resource respectively.
    """

    manifest: Resource
    server: Resource
    # If there was an update to an immutable field on the resource,
    # consequently flagging the resource to be replaced, this field
    # contains the updated field.
    replacement_field: Optional[str] = None
    # If a 'mutable' parent of this resource is being replaced, triggering
    # a cascade (update) on this resource, this field contains the
    # parent type and resource name.
    # (e.g. where the current resource is a Validator, and its parent
    # filter is being replaced)
    replacement_cascaded_update_parent: Optional[tuple[type, str]] = None
    # Indicate which secret fields have changed
    secret_fields_changed: Optional[dict[str, bool]] = None


@dataclass
class ResourceUpdates:
    """Resources to update. Grouped by type."""

    credentials: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    channels: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    sources: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    windows: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    filters: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    segmentations: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    validators: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)
    notification_rules: dict[str, ResourceUpdate] = dataclasses.field(
        default_factory=dict
    )

    # Tags are just here to allow us to resolve the name from the type but it
    # will never be set since we only create tags from IaC. Rather than doing
    # code branches whenever we rely on `DiffContext.fields()` we ensure
    # `ResourceUpdates` conforms to the same signature.
    tags: dict[str, ResourceUpdate] = dataclasses.field(default_factory=dict)


@dataclass
class GraphDiff:
    to_create: DiffContext
    to_delete: DiffContext
    to_update: ResourceUpdates

    replacement_ctx: ReplacementContext

    def retain(self, targets: "ResourceNames") -> None:
        """Retain resources.

        If a set of targets is specified, we only keep the resources that
        matches. If no targets are specified all will be targeted as usual.

        :param targets: `ResourceNames` with targets to preserve, ignoring the
            rest
        """
        if targets.size() == 0:
            return

        resource_types = DiffContext.fields()

        for resource_type in resource_types:
            resource_targets = getattr(targets, resource_type)
            to_create = getattr(self.to_create, resource_type)
            to_delete = getattr(self.to_delete, resource_type)
            to_update = getattr(self.to_update, resource_type)

            self._retain_targets(resource_targets, to_create)
            self._retain_targets(resource_targets, to_delete)
            self._retain_targets(resource_targets, to_update)

    @staticmethod
    def _retain_targets(targets: set[str], resources: dict[str, Any]) -> None:
        if len(resources) == 0:
            return

        to_remove = {r for r in resources if r not in targets}

        for resource_name in to_remove:
            del resources[resource_name]

    def num_creates(self) -> int:
        return self.size(self.to_create)

    def num_deletes(self) -> int:
        return self.size(self.to_delete)

    def num_updates(self) -> int:
        return self.size(self.to_update)

    def num_operations(self) -> int:
        return self.num_creates() + self.num_deletes() + self.num_updates()

    @staticmethod
    def size(obj: Any) -> int:
        count = 0
        for f in DiffContext.fields():
            count += len(getattr(obj, f))
        return count


async def diff_resource_graph(
    namespace: str,
    session: Session,
    schema_reinference: SourceSchemaReinference,
    show_secrets: bool,
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    import_mode: bool = False,
) -> GraphDiff:
    graph_diff = _diff_resource_graph(
        namespace=namespace,
        manifest_ctx=manifest_ctx,
        server_ctx=server_ctx,
        import_mode=import_mode,
    )

    await enrich_resource_graph(
        manifest_ctx=manifest_ctx,
        server_ctx=server_ctx,
        graph=graph_diff,
        session=session,
        schema_reinference=schema_reinference,
        show_secrets=show_secrets,
    )

    _compute_replacements(
        manifest_ctx=manifest_ctx,
        server_ctx=server_ctx,
        graph_diff=graph_diff,
    )

    return graph_diff


def _compute_replacements(
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    graph_diff: GraphDiff,
) -> None:
    resource_topo_order = DiffContext.fields_topological_order(
        graph_mode=True,
    )

    for parent_resource_type, _ in resource_topo_order:
        to_update: dict[str, ResourceUpdate] = getattr(
            graph_diff.to_update, parent_resource_type
        )
        replacement_ctx: dict[str, ReplacementReason] = getattr(
            graph_diff.replacement_ctx, parent_resource_type
        )

        to_replace = {
            name: (resource_update, resource_update.replacement_field)
            for name, resource_update in to_update.items()
            if resource_update.replacement_field
        }

        for name, (resource_update, replacement_field) in to_replace.items():
            replacement_ctx[name] = ImmutableFieldReplacementReason(
                field_name=replacement_field, resource_update=resource_update
            )
            _visit_resource_to_replace(
                manifest_ctx=manifest_ctx,
                server_ctx=server_ctx,
                graph_diff=graph_diff,
                resource_type=parent_resource_type,
                resource_name=name,
                curr_depth=1,
            )


def _visit_resource_to_replace(
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    graph_diff: GraphDiff,
    resource_type: str,
    resource_name: str,
    curr_depth: int,
) -> None:
    if curr_depth > MAX_RESOURCE_DEPTH:
        raise ManifestConfigurationError(
            "BUG: max recursion depth exceeded while computing replacements"
        )

    to_update: dict[str, ResourceUpdate] = getattr(graph_diff.to_update, resource_type)
    to_create: dict[str, Resource] = getattr(graph_diff.to_create, resource_type)
    to_delete: dict[str, Resource] = getattr(graph_diff.to_delete, resource_type)

    # Remove the resource from the update list.
    to_update.pop(resource_name, None)

    # Flag the resource to be created.
    manifest_resources: dict[str, Resource] = getattr(manifest_ctx, resource_type)
    manifest_obj = manifest_resources[resource_name]
    to_create[manifest_obj.name] = manifest_obj

    # If the resource exists on the server, flag it resource to be deleted.
    server_resources: dict[str, Resource] = getattr(server_ctx, resource_type)
    if resource_name in server_resources:
        server_obj = server_resources[resource_name]
        to_delete[server_obj.name] = server_obj

    # Check for cascading child resources to replace or update.
    # We only need to look at what's in the manifest (resources
    # not in the manifest are already being flagged for deletion).
    resource_topo_order = DiffContext.fields_topological_order(graph_mode=True)
    # Get all children resources for the resource and flag them to be moved as well.
    children_types = next(
        (
            children_types
            for (parent_type, children_types) in resource_topo_order
            if parent_type == resource_type
        ),
        None,
    )
    if not children_types:
        return

    parent_field_name = f"{manifest_obj.resource_class_name().lower()}_name"
    for child_resource_type in children_types:
        child_resources: dict[str, Resource] = getattr(
            manifest_ctx, child_resource_type
        )
        replacement_ctx: dict[str, ReplacementReason] = getattr(
            graph_diff.replacement_ctx, child_resource_type
        )

        for child_resource_name, child_resource in child_resources.items():
            is_child = (
                (resource_name == getattr(child_resource, parent_field_name))
                or
                # e.g. reference filter on a validator.
                (
                    resource_name
                    == child_resource._nested_mutable_parents().get(parent_field_name)
                )
            )
            if not is_child:
                continue

            # A child resource should only be cascade-deleted if the parent
            # resource is an immutable property. Notable example is the filter
            # resources which is mutable on child resources. If a mutable parent
            # is being replaced, then the child resource only needs to be updated
            # so that it gets the new 'id' of its parent.
            parent_is_mutable = parent_field_name in child_resource._mutable_fields()
            if parent_is_mutable:
                _visit_resource_to_cascade_update(
                    manifest_ctx=manifest_ctx,
                    server_ctx=server_ctx,
                    graph_diff=graph_diff,
                    parent_resource_cls=manifest_obj.__class__,
                    parent_resource_name=resource_name,
                    resource_type=child_resource_type,
                    resource_name=child_resource_name,
                )
            else:
                replacement_ctx[child_resource_name] = CascadeReplacementReason(
                    parent_resource_cls=manifest_obj.__class__,
                    parent_resource_name=resource_name,
                )
                _visit_resource_to_replace(
                    manifest_ctx=manifest_ctx,
                    server_ctx=server_ctx,
                    graph_diff=graph_diff,
                    resource_type=child_resource_type,
                    resource_name=child_resource_name,
                    curr_depth=curr_depth + 1,
                )


def _visit_resource_to_cascade_update(
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    graph_diff: GraphDiff,
    parent_resource_cls: type,
    parent_resource_name: str,
    resource_type: str,
    resource_name: str,
) -> None:
    to_update: dict[str, ResourceUpdate] = getattr(graph_diff.to_update, resource_type)
    to_create: dict[str, Resource] = getattr(graph_diff.to_create, resource_type)
    to_delete: dict[str, Resource] = getattr(graph_diff.to_delete, resource_type)

    # If the resource is already being created or deleted, then
    # there's nothing to do. The cascading 'update' is secondary to
    # those operations.
    # Similarly, if the resource is already being updated, there is
    # nothing to do either.
    for resources in typing.cast(dict[str, object], [to_create, to_delete, to_update]):
        if resource_name in resources:
            return

    manifest_resources: dict[str, Resource] = getattr(manifest_ctx, resource_type)
    server_resources: dict[str, Resource] = getattr(server_ctx, resource_type)
    if resource_name not in manifest_resources or resource_name not in server_resources:
        # We expect both manifest and server object, since we've
        # checked for create/delete operation on this resource.
        raise ValidioBugError(
            f"unable to cascade update {resource_type} '{resource_name}': "
            f"missing manifest or server object"
        )

    to_update[resource_name] = ResourceUpdate(
        manifest=manifest_resources[resource_name],
        server=server_resources[resource_name],
        replacement_cascaded_update_parent=(
            parent_resource_cls,
            parent_resource_name,
        ),
    )


def _diff_resource_graph(
    namespace: str,
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    import_mode: bool = False,
) -> GraphDiff:
    # Backwards compatibility: Here we note the filters that
    # are in-use by validators.
    # See usage site for more info.
    # Note: we do this before diff, since we lose some info (when we
    # force a validator into filter-expression mode) during diff.
    server_filter_references = _collect_filter_references(server_ctx)

    fns = [
        (compute_creates, DiffContext),
        (compute_deletes, DiffContext),
        (compute_updates, ResourceUpdates),
    ]
    diffs = []
    fields = DiffContext.fields()
    for diff_fn, cls in fns:
        diff_by_resource = {}
        for field in fields:
            if field in CREATE_ONLY_RESOURCES:
                continue
            diff_by_resource[field] = diff_fn(
                namespace, getattr(manifest_ctx, field), getattr(server_ctx, field)
            )
        diffs.append(cls(**diff_by_resource))

    for field in CREATE_ONLY_RESOURCES:
        setattr(
            diffs[0],
            field,
            compute_creates(
                namespace,
                getattr(manifest_ctx, field),
                getattr(server_ctx, field),
            ),
        )

    g = GraphDiff(
        to_create=diffs[0],
        to_delete=diffs[1],
        to_update=diffs[2],
        replacement_ctx=ReplacementContext(),
    )

    if not import_mode:
        _retain_auto_generated_filter_resources(g, server_filter_references)

    return g


def _collect_filter_references(
    server_ctx: DiffContext,
) -> set[tuple[str, str]]:
    live_filters = set({})
    for v in server_ctx.validators.values():
        if v.filter_name:
            live_filters.add((v.name, v.filter_name))
        if v.reference and v.reference.filter_name:
            live_filters.add((v.name, v.reference.filter_name))

    return live_filters


def _retain_auto_generated_filter_resources(
    g: GraphDiff,
    server_filter_references: set[tuple[str, str]],
) -> None:
    """
    Backwards compatibility while we transition to Filter resources.

    On the API side we only deal with Filter resources. While iac
    side, we support JSONFilterExpression during the transition - on the
    backend, the filter expression is represented by an actual Filter
    resource that we auto generate.
    But this behavior can is inconsistent from a diff pov since there's
    no representation of the auto-generated filter resource in the iac
    manifest. So that diff will flag the auto-generated resource to be
    deleted, which is undesirable.

    To avoid this behavior, we just check for this condition. If we flagged
    to delete a Filter that is still in use by some validator, then basically
    un-flag that filter for delete.
    """
    if len(g.to_delete.filters) == 0:
        return

    for validator_name, filter_name in list(server_filter_references):
        # If a validator is being deleted, then we don't count references
        # towards its filters.
        if (
            validator_name in g.to_delete.validators
            and validator_name not in g.to_create.validators
        ):
            server_filter_references.remove((validator_name, filter_name))

    live_filters = {filter_name for _, filter_name in server_filter_references}

    for filter_name in set(g.to_delete.filters.keys()):
        # If we were already going to re-create the filter
        # after deleting, then nothing to do.
        if filter_name not in g.to_create.filters and filter_name in live_filters:
            del g.to_delete.filters[filter_name]


def compute_creates(
    namespace: str, manifest_resources: dict[str, R], server_resources: dict[str, R]
) -> dict[str, R]:
    creates = {}
    for name, resource in manifest_resources.items():
        if name in server_resources:
            _check_namespace(namespace, server_resources[name])
            continue
        creates[name] = resource
    return creates


def compute_deletes(
    namespace: str, manifest_resources: dict[str, R], server_resources: dict[str, R]
) -> dict[str, R]:
    deletes = {}
    for name, resource in server_resources.items():
        if namespace != resource._must_namespace():
            # Only work on resources in the configured namespace.
            continue

        if name not in manifest_resources:
            deletes[name] = resource

    return deletes


def compute_updates(
    namespace: str, manifest_resources: dict[str, R], server_resources: dict[str, R]
) -> dict[str, ResourceUpdate]:
    diffs = {}

    for name, manifest in manifest_resources.items():
        if name not in server_resources:
            continue

        server = server_resources[name]
        _check_namespace(namespace, server)

        d = diff(manifest, server, 0, manifest, server)
        if d:
            diffs[name] = d

    return diffs


# ruff: noqa: PLR0911,PLR0912
def diff(
    manifest_object: Diffable,
    server_object: Diffable,
    curr_depth: int,
    manifest_resource: Resource,
    server_resource: Resource,
) -> ResourceUpdate | None:
    """
    Compares the current (manifest) resource against a provided server version
    of that resource. None is returned if there are no changes between the two
    resources. If there is at least one change, then a diff is returned which
    contains a representation of the full manifest and server side resource.
    """
    if curr_depth > MAX_RESOURCE_DEPTH:
        raise max_resource_depth_exceeded(manifest_resource.name)

    # If the server resource has a different type, this is an invalid update.
    # e.g. we can't switch a window from tumbling to fixed batch. The window
    # needs to be re-created if that's the desired outcome. This only applies
    # for resources, nested objects like filters can still change type.
    if not isinstance(server_object, manifest_object.__class__):
        if isinstance(server_object, Resource):
            raise updated_resource_type_mismatch_exception(
                manifest_resource.name, manifest_object, server_object
            )
        return ResourceUpdate(manifest_resource, server_resource)

    # If we've been requested explicitly flagged to not diff the resource,
    # then no changes to report.
    if isinstance(manifest_object, Resource) and manifest_object.ignore_changes:
        return None

    if isinstance(server_resource, Segmentation) and isinstance(
        manifest_resource, Segmentation
    ):
        # Segment usage was introduced as an optional property to not
        # break existing clients but it should ideally be a required
        # immutable property.
        # All existing segmentations have been migrated to have this
        # property serverside but existing manifests will not have it.
        # To handle that we will during a deprecation period use the
        # servers value if no value was set in the manifest.
        manifest = getattr(manifest_object, "segment_usage")
        server = getattr(server_object, "segment_usage")
        if manifest is None:
            manifest_resource.segment_usage = server

    if (
        isinstance(manifest_resource, TumblingWindow)
        and isinstance(server_object, TumblingWindow)
        and isinstance(manifest_object, TumblingWindow)
    ):
        # Lookback was introduced as an optional property to not
        # break existing clients but it should ideally be a required
        # property. (for warehouse sources)
        # All existing tumbling windows have been migrated to have this
        # property serverside but existing manifests will not have it.
        # To handle that we will during a deprecation period use the
        # servers value if no value was set in the manifest.
        manifest = getattr(manifest_object, "lookback")
        server = getattr(server_object, "lookback")
        if manifest is None:
            manifest_resource.lookback = server

    # Ignored fields aren't diffed. But they're normally still part of the
    # object, so we need to avoid the situation where we end up showing a diff
    # on an ignored field (the object has a legit diff on another field in this
    # for such a scenario to occur) because there's a mismatch between the manifest
    # and server.
    # To avoid this, we just ensure both manifest and server have the same value.
    # Ensure we don't produce any diff for ignored fields by always setting the
    # manifest value to whatever is on the server.
    for field in manifest_object._ignored_fields():
        setattr(manifest_object, field, getattr(server_object, field))

    # Check for updates to immutable fields. If we detect such changes,
    # we flag the resource to be recreated.
    for field in manifest_object._immutable_fields():
        manifest = getattr(manifest_object, field)
        server = getattr(server_object, field)
        if manifest != server:
            return ResourceUpdate(
                manifest_resource, server_resource, replacement_field=field
            )

    # If any valid field changes, then mark the resource as having a diff.
    for field in manifest_object._mutable_fields():
        manifest = getattr(manifest_object, field)
        server = getattr(server_object, field)

        if manifest != server:
            # Whenever we find there's a change to make, grab all fields on both
            # resource versions so that we can present them as a diff.
            # Regardless of at what depth we find a change, the diff we present
            # will always start from the root resource itself. We pass those objects
            # around for this purpose.
            return ResourceUpdate(
                manifest_resource,
                server_resource,
            )

    # Some fields require the resource to be re-created if the type changes
    # e.g. going from a dynamic to a fixed threshold is not allowed.
    # If we detect that then we flag the resource to be re-created.
    for field in manifest_object._replace_on_type_change_fields():
        manifest = getattr(manifest_object, field)
        server = getattr(server_object, field)
        if server.__class__ != manifest.__class__:
            return ResourceUpdate(
                manifest_resource, server_resource, replacement_field=field
            )

    # No changes yet. Next, descend into the nested fields. If we find any
    # changes, then mark _this_ resource as changed.
    server_nested_objects = server_object._nested_objects()
    for field, manifest in manifest_object._nested_objects().items():
        server = server_nested_objects[field]

        # No possible change if both are unset.
        if manifest is None and server is None:
            continue

        # If exactly one of them is None, then we definitely have a change.
        if manifest is None or server is None:
            return ResourceUpdate(manifest_resource, server_resource)

        if isinstance(server, list) != isinstance(manifest, list):
            return ResourceUpdate(manifest_resource, server_resource)

        if isinstance(server, list) and isinstance(manifest, list):
            if len(server) != len(manifest):
                return ResourceUpdate(manifest_resource, server_resource)

            for i in range(len(server)):
                # Descend into both objects to diff.
                collected_diff = diff(
                    manifest[i],
                    server[i],
                    curr_depth + 1,
                    manifest_resource,
                    server_resource,
                )

                if collected_diff:
                    # The returned diff is that of the full resource (not
                    # just the nested object that had a change). So we can
                    # exit with it.
                    return collected_diff

            continue

        # Descend into both objects to diff.
        collected_diff = diff(
            manifest, server, curr_depth + 1, manifest_resource, server_resource
        )
        if collected_diff:
            # The returned diff is that of the full resource (not
            # just the nested object that had a change). So we can
            # exit with it.
            return collected_diff

    # No update to make
    return None


async def enrich_resource_graph(
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    graph: GraphDiff,
    session: Session,
    schema_reinference: SourceSchemaReinference,
    show_secrets: bool,
) -> None:
    """
    Now that we have a graph and done a diff, some values are unknown and need to
    be resolved before we can get a full picture of changes and start making api
    requests to create/update things. This function fetches missing info from the
    server and updates resources in the graph as needed.
    """
    # For the resources we update, resolve the ids in the manifest objects. We have
    # the info in the equivalent server object.
    for f in DiffContext.fields():
        manifest_resources = getattr(manifest_ctx, f)
        server_resources = getattr(server_ctx, f)
        for name, server_resource in server_resources.items():
            if name in manifest_resources:
                manifest_resource = manifest_resources[name]
                manifest_resource._id.value = server_resource._must_id()

    # Since source jtd schemas can be managed automatically, we do not include
    # them in the actual diff process since they are not necessarily known yet.
    # Instead, here we explicitly check for any updates.
    await check_for_source_schema_changes(
        manifest_ctx, server_ctx, graph, session, schema_reinference
    )

    # Check if any secrets has changed and add them to the diff.
    # They're excluded by default.
    await check_for_secret_changes(
        manifest_ctx=manifest_ctx,
        server_ctx=server_ctx,
        session=session,
        show_secrets=show_secrets,
        graph=graph,
    )


async def check_for_source_schema_changes(
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    graph: GraphDiff,
    session: Session,
    schema_reinference: SourceSchemaReinference,
) -> None:
    # For sources that are to be created and don't have a schema, we
    # need to infer a schema for them to use in the create request.
    sources_to_infer = [
        source
        for name, source in graph.to_create.sources.items()
        if source.jtd_schema is None
    ]

    # For sources that are to be updated, if there is no schema specified
    # in the manifest, then assign it the schema of the server version.
    # Or if we were asked to re-infer the schema, then do that instead.
    for name, r in graph.to_update.sources.items():
        assert isinstance(r.manifest, Source)
        assert isinstance(r.server, Source)

        manifest_source = r.manifest
        reinfer = schema_reinference.should_reinfer_schema_for_source(name)

        if manifest_source.jtd_schema is None:
            if reinfer:
                sources_to_infer.append(manifest_source)
            else:
                manifest_source.jtd_schema = r.server.jtd_schema
        elif not reinfer:
            # Unless we specify to update schemas we let the server schema be
            # source of truth. This is to not end up mutating or changing
            # anything schema related when we only wanted to update something
            # unrelated, e.g. a description.
            # Only if the source is specified to update its schema do we use the
            # manifest as source of truth.
            manifest_source.jtd_schema = r.server.jtd_schema

    # For unchanged sources, check if there is a schema diff now that all schemas
    # have been resolved. If we find a diff, flag the source as updated.
    unchanged_sources = {
        name: s
        for name, s in manifest_ctx.sources.items()
        if s.name not in graph.to_create.sources
        and s.name not in graph.to_update.sources
        and s.name not in graph.to_delete.sources
    }

    # include schemas for unchanged sources that need to be re-inferred.
    sources_to_infer.extend(
        [
            unchanged_sources[name]
            for name, source in server_ctx.sources.items()
            if name in unchanged_sources
            and unchanged_sources[name].jtd_schema is None
            and schema_reinference.should_reinfer_schema_for_source(name)
        ]
    )
    await infer_schemas(
        manifest_ctx=manifest_ctx,
        sources=sources_to_infer,
        session=session,
    )

    for name, server_source in server_ctx.sources.items():
        if name not in unchanged_sources:
            continue

        manifest_source = unchanged_sources[name]

        # Unless we are actively looking to update the schema, force the server
        # manifest to be whatever is specified in the manifest,  if in manual
        # schema mode.
        if (
            manifest_source.jtd_schema is not None
            and not schema_reinference.should_reinfer_schema_for_source(name)
        ):
            manifest_source.jtd_schema = server_source.jtd_schema

        if (
            manifest_source.jtd_schema is not None
            and manifest_source.jtd_schema != server_source.jtd_schema
        ):
            # The 'manifest' and 'server' version of the resource can be the same
            # here since there is no difference between the two (only change is
            # the secret).
            graph.to_update.sources[name] = ResourceUpdate(
                manifest_source, server_source
            )

        # Ensure the source has a schema in case we need it later on.
        if manifest_source.jtd_schema is None:
            manifest_source.jtd_schema = server_source.jtd_schema


async def infer_schemas(
    manifest_ctx: DiffContext,
    session: Session,
    sources: list[Source],
) -> None:
    await asyncio.gather(
        *[
            infer_schema_for_sources(
                manifest_ctx=manifest_ctx,
                sources=chunk,
                session=session,
            )
            for chunk in split_to_n_chunks(sources, NUM_CONCURRENT_INFERENCE_TASKS)
        ]
    )


async def infer_schema_for_sources(
    manifest_ctx: DiffContext,
    sources: list[Source],
    session: Session,
) -> None:
    for source in sources:
        await infer_schema_for_source(manifest_ctx, source, session)


async def infer_schema_for_source(
    manifest_ctx: DiffContext,
    source: Source,
    session: Session,
) -> None:
    credential = manifest_ctx.credentials[source.credential_name]
    # If we don't yet have an ID (credential has not yet been created),
    # we can't do schema inference. So schema will be unknown in the diff.
    if credential._id.value is None:
        return
    await source._api_infer_schema(credential, session)


async def check_for_secret_changes(
    manifest_ctx: DiffContext,
    server_ctx: DiffContext,
    session: Session,
    show_secrets: bool,
    graph: GraphDiff,
) -> None:
    """
    To be able to always compute if we have any diff for resources containing secret
    fields we want to call the API to figure this out otherwise we wouldn't show a
    change in the secret if other fields were changed.
    """
    for field in DiffContext.fields():
        manifest_resources = getattr(manifest_ctx, field)
        server_resources = getattr(server_ctx, field)

        # If it's a delete it won't exist in `manifest_ctx` so it will be skipped.
        for name, manifest_object in manifest_resources.items():
            # If it's an add it won't exist in `server_ctx` so it will be skipped.
            server_object = server_resources.get(name)
            if not server_object:
                continue

            if not _has_secret_fields(manifest_object, curr_depth=1):
                continue

            secret_fields_changed = await _check_secret_change(
                session, show_secrets, manifest_object
            )

            secrets_changed = any(
                secret_fields_changed[field] for field in secret_fields_changed
            )

            if not secrets_changed:
                continue

            # Flag that the secrets for the resource has changed so we can show it in
            # the diff.
            to_update = getattr(graph.to_update, field)
            to_update[name] = ResourceUpdate(
                manifest=manifest_object,
                server=server_object,
                secret_fields_changed=secret_fields_changed,
            )


# Checks if the Diffable object or any of its sub objects
# defines any secret fields.
def _has_secret_fields(obj: Diffable, curr_depth: int) -> bool:
    if curr_depth > MAX_RESOURCE_DEPTH:
        raise ValidioError(
            "BUG: max recursion depth exceeded while looking for secrets"
        )

    if hasattr(obj, "_secret_fields") and obj._secret_fields():
        return True

    for nested in obj._nested_objects().values():
        if isinstance(nested, list):
            for n in nested:
                if _has_secret_fields(n, curr_depth=curr_depth + 1):
                    return True
        elif nested and _has_secret_fields(nested, curr_depth + 1):
            return True

    return False


async def _check_secret_change(
    session: Session,
    show_secrets: bool,
    resource: Resource,
) -> dict[str, Any]:
    """
    Checks whether secrets have changed.

    :param session: Session to use.
    :param show_secrets: Whether to show secrets.
    :param resource: Resource to check secrets for.
    :return: Dictiondary indicating which fields have changed.
    """
    if resource.ignore_changes:
        return {}

    response = resource._api_secret_change_response()

    # serialize response to build response fields
    query_response_fields = ""
    response_fields: dict[str, bool | dict[str, bool]] = {}
    for key, value in response.items():
        query_response_fields += f" {key}"
        if isinstance(value, ApiSecretChangeNestedResource):
            query_response_fields += (
                " { __typename " + value._api_secret_change_auth_query() + " }"
            )
            response_fields[key] = value._api_secret_change_auth_response_fields()
        else:
            response_fields[key] = True

    try:
        response = await secrets_changed_by_field(
            session,
            resource.__class__.__name__,
            query_response_fields=query_response_fields,
            variable_values=resource._api_secret_change_input(),
        )
    except TransportQueryError as e:
        raise _sanitize_error(e, show_secrets)

    if response["errors"]:
        raise ValidioError(
            f"failed to check for changed secrets for resource {resource.name}: "
            f"{response['errors']}"
        )

    # map response values to secret fields changed
    def fetch_response_fields(
        source: dict[str, Any], template: dict[str, Any]
    ) -> dict[str, Any]:
        result = {}
        for key, value in template.items():
            if key in source:
                if isinstance(value, dict) and isinstance(source[key], dict):
                    changed_fields = fetch_response_fields(source[key], value)
                    if changed_fields:  # filter out nested fields without changes
                        result[to_snake(key)] = changed_fields
                elif source[key]:  # filter out fields without changes
                    result[to_snake(key)] = source[key]
        return result

    return fetch_response_fields(response, response_fields)


def _check_namespace(namespace: str, server_resource: Resource) -> None:
    # Tags are global so nothing to check
    if isinstance(server_resource, Tag):
        return

    server_namespace = server_resource._must_namespace()
    if namespace != server_namespace:
        raise ManifestConfigurationError(
            f"resource {server_resource.__class__.__name__} '{server_resource.name}' "
            "does not belong to the current namespace; "
            f"resource namespace = {server_namespace}; current namespace = {namespace}"
        )
