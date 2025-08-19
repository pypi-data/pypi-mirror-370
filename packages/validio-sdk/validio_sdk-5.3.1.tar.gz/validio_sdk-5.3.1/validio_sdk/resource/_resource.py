import dataclasses
import inspect
import re
from abc import abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar, cast

from camel_converter import to_camel, to_snake

# We need validio_sdk in scope due to eval.
# ruff: noqa: F401
import validio_sdk
from validio_sdk._api.api import APIClient, execute_mutation
from validio_sdk.client import Session
from validio_sdk.exception import ValidioError
from validio_sdk.resource._diffable import (
    ApiSecretChangeNestedResource,
    Diffable,
)
from validio_sdk.resource._serde import (
    NODE_TYPE_FIELD_NAME,
    ImportValue,
    _api_create_input_params,
    _api_update_input_params,
    _import_resource_params,
    _import_value_repr,
    without_skipped_internal_fields,
)

if TYPE_CHECKING:
    from validio_sdk.code._import import ImportContext
    from validio_sdk.resource.channels import Channel
    from validio_sdk.resource.credentials import Credential
    from validio_sdk.resource.filters import Filter
    from validio_sdk.resource.notification_rules import NotificationRule
    from validio_sdk.resource.segmentations import Segmentation
    from validio_sdk.resource.sources import Source
    from validio_sdk.resource.tags import Tag
    from validio_sdk.resource.validators import Validator
    from validio_sdk.resource.windows import Window

R = TypeVar("R", bound="Resource")

CREATE_ONLY_RESOURCES = {"tags"}


@dataclass
class DiffContext:
    """
    Caches all objects of a graph to make it easier to
    revisit them at a later point. e.g. to compare two graphs.
    """

    tags: dict[str, "Tag"] = dataclasses.field(default_factory=dict)
    credentials: dict[str, "Credential"] = dataclasses.field(default_factory=dict)
    channels: dict[str, "Channel"] = dataclasses.field(default_factory=dict)
    sources: dict[str, "Source"] = dataclasses.field(default_factory=dict)
    windows: dict[str, "Window"] = dataclasses.field(default_factory=dict)
    filters: dict[str, "Filter"] = dataclasses.field(default_factory=dict)
    segmentations: dict[str, "Segmentation"] = dataclasses.field(default_factory=dict)
    validators: dict[str, "Validator"] = dataclasses.field(default_factory=dict)
    notification_rules: dict[str, "NotificationRule"] = dataclasses.field(
        default_factory=dict
    )

    # Validators objects that are yet to be decoded
    pending_validators_raw: dict[str, tuple[type, dict[str, Any]]] = dataclasses.field(
        default_factory=dict
    )

    @staticmethod
    def fields() -> list[str]:
        return [
            f
            for f in list(inspect.signature(DiffContext).parameters)
            if f != "pending_validators_raw"
        ]

    @staticmethod
    def fields_singular() -> set[str]:
        return {f[: len(f) - 1] for f in DiffContext.fields()}

    @staticmethod
    def fields_topological_order(
        graph_mode: bool = False,
    ) -> list[tuple[str, list[str]]]:
        """
        Returns the fields but with their parent-child dependency encoded.
        If graph_mode is turned off (default), then the returned order is
        a tree datastructure (each node has a single parent) and will be
        visited exactly once.
        """
        fields: list[tuple[str, list[str]]] = [
            # Channels need to come before sources because notification rules
            # have references to sources.
            ("tags", ["sources", "validators"]),
            ("channels", ["notification_rules"]),
            ("credentials", ["sources"]),
            ("sources", ["windows", "segmentations", "filters", "validators"]),
            ("windows", [] if not graph_mode else ["validators"]),
            ("segmentations", [] if not graph_mode else ["validators"]),
            ("filters", [] if not graph_mode else ["segmentations", "validators"]),
            ("validators", []),
            ("notification_rules", []),
        ]
        # Sanity check that this doesn't go out of sync
        parents = {parent for (parent, _) in fields}
        expected = set(DiffContext.fields())

        if parents != expected:
            raise ValidioError(f"DiffContext fields mismatch {parents} != {expected}")

        return fields


class ResourceID:
    """
    ResourceID represents the id of a resource.

    This value is potentially unknown until after the configuration has been fully
    provisioned. So it acts like a future/promise where it starts out as unknown
    and eventually will be resolved with a concrete value.
    """

    _node_type = "_id"

    def __init__(self) -> None:
        self.value: str | None = None
        """Eventually contains the concrete value assigned to the resource"""

        self._node_type = ResourceID._node_type

    @staticmethod
    def _encode() -> None:
        # Resource ID is never populated before we write the graph out.
        # So no need to include the empty object value in the graph output. When we
        # deserialize back from json, each resource will re-initialize its IDs with
        # empty values again.
        return None


@dataclass(order=True)
class ResourceDeprecation:
    """Deprecation information for a resource."""

    resource_type: str
    resource_name: str
    message: str

    def __str__(self) -> str:
        """String implementation."""
        named = f" named '{self.resource_name}'" if self.resource_name else ""

        return f"On '{self.resource_type}'{named}: {self.message}"

    def _encode(self) -> dict[str, str]:
        """Encoder."""
        return self.__dict__


class Resource(Diffable):
    """
    Dataclass representing a resource object.

    All resources are derived from this base. It tracks the dependency
    between resources.
    """

    def __init__(
        self,
        name: str,
        display_name: str | None,
        __internal__: "ResourceGraph",
        ignore_changes: bool,
    ):
        self._id: ResourceID = ResourceID()
        self._namespace: str | None = None
        self._node_type: str = self.__class__.__name__

        self.name = name
        self.display_name = display_name if display_name else name

        # Split by resource type. e.g a Source will have different children sets
        # per resource type (window, segmentation, validators)
        # { "Window": {"w1": {}, "w2": {}}, "Segmentation": {"seg1": {}} }
        self._children = cast(
            dict[str, dict[str, Resource]],
            {
                # This is a type violation as a workaround so that we know
                # how to deserialize the value.
                NODE_TYPE_FIELD_NAME: "_children",
            },
        )

        # The graph must always come from the parent. Except for the root
        # node type (Credential) which will explicitly set a default if none
        # was provided.
        self._resource_graph: ResourceGraph = __internal__

        # Flags whether this resource has been applied (created/deleted/updated)
        # on the server.
        self._applied = False

        # If set to true, changes to the resource will be ignored
        self.ignore_changes = ignore_changes

        # TODO(VR-3875): Fully remove after deprecation warning period.
        if hasattr(self, "_arg_deprecation"):
            self.add_deprecation(getattr(self, "_arg_deprecation"))
            delattr(self, "_arg_deprecation")

    # TODO(VR-3875): Fully remove after deprecation warning period.
    def _check_and_delete_arg_deprecation_on_child(
        self, child: "Diffable | Resource | None"
    ) -> None:
        """Add child object deprecation.

        Some child objects such as thresholds or notification rule conditions
        aren't resources and thus can't add deprecations to themselves. Instead
        when we have deprecation we usually add it to the parent resource where
        used.

        This method on a parent class accepts a child obejct that can contain an
        internal field named `_arg_deprecation` and if it does, a deprecation
        notice will be added referring to the parent class.
        """
        if hasattr(child, "_arg_deprecation"):
            self.add_deprecation(
                f"(Used on '{self.__class__.__name__}' named '{self.name}'): "
                + getattr(child, "_arg_deprecation"),
                child,
            )
            delattr(child, "_arg_deprecation")

    def _mutable_fields(self) -> set[str]:
        return {"display_name"}

    def add_field_deprecation(
        self, current_field: str, suggested_field: str | None = None
    ) -> None:
        """Mark a field as deprecated.

        :param current_field: The field to deprecated
        :param suggested_field: Potentially new field replacing it
        """
        description = f"Field '{current_field}' is deprecated"
        if suggested_field:
            description += f", please use '{suggested_field}' instead"

        self.add_deprecation(description)

    def add_deprecation(
        self,
        description: str,
        diff_object: "Diffable | Resource | None" = None,
    ) -> None:
        """Add a deprecation warning for a resource.

        :param description: Deprecation description
        :param diff_object: If the deprecation is on a `Diffable` used by this
            parent we can pass that to print it to the right resource.
        """
        if diff_object is None:
            resource_type = self.__class__.__name__
            resource_name = self.name
        else:
            resource_type = diff_object.__class__.__name__
            resource_name = (
                diff_object.name if isinstance(diff_object, Resource) else ""
            )

        self._resource_graph.add_deprecation(
            ResourceDeprecation(
                resource_name=resource_name,
                resource_type=resource_type,
                message=description,
            )
        )

    def _must_id(self) -> str:
        if self._id.value is None:
            raise ValidioError(
                f"resource {self.__class__.__name__}(name={self.name}) "
                "has unresolved ID"
            )

        return self._id.value

    def _must_namespace(self) -> str:
        if self._namespace is None:
            raise ValidioError(
                f"resource {self.__class__.__name__}(name={self.name}) "
                "has unresolved namespace"
            )

        return self._namespace

    # Adds the specified resource as a 'child' of the self resource.
    def add(self, resource_name: str, child: "Resource") -> None:
        self._resource_graph.allocate_resource_name(resource_name, child)

        child_type: str = child.resource_class_name()
        if child_type not in self._children:
            self._children[child_type] = {}

        # No need to do a duplicate check here - since a duplicate name
        # will have failed when we allocated the resource name.
        self._children[child_type][resource_name] = child

    def _encode_children(self) -> dict[str, dict[str, object]]:
        children = {
            k: (
                v._encode()  # type:ignore
                if callable(getattr(v, "_encode", None))
                else v
            )
            for k, v in self._children.items()
        }

        # If the node has no children, then skip deserializing the object.
        # This makes the encoded graph smaller - (e.g. validators are the most
        # common elements in the graph with 10s of thousands of them, and they
        # don't have children)
        if list(children.keys()) == [NODE_TYPE_FIELD_NAME]:
            return {}

        return {"_children": children}

    def _nested_objects(self) -> dict[str, Optional["Diffable | list[Diffable]"]]:
        return {}

    def _nested_mutable_parents(self) -> dict[str, str | None]:
        """
        Returns any nested mutable parent resources.
        This has information about any 'nested' fields that
        point to parent resource references. (e.g a validator
        pointing to a reference filter).

        Returned map contains field_name => field_value
        """
        return {}

    def _api_create_response_field_name(self) -> str:
        return to_snake(self.resource_class_name())

    def _api_create_method_name(self) -> str:
        name = self.__class__.__name__
        lc_first = name[0].lower() + name[1:]

        return f"{lc_first}Create"

    def _api_update_method_name(self) -> str:
        name = self.__class__.__name__
        lc_first = name[0].lower() + name[1:]

        return f"{lc_first}Update"

    def _api_create_arguments(self) -> dict[str, str]:
        return {
            "input": f"{self.__class__.__name__}CreateInput!",
        }

    def _api_update_arguments(self) -> dict[str, str]:
        return {"input": f"{self.__class__.__name__}UpdateInput!"}

    def _api_delete_arguments(self) -> dict[str, str]:
        return {"ids": f"[{self.resource_class_name()}Id!]!"}

    async def _api_create(
        self,
        namespace: str,
        ctx: "DiffContext",
        session: Session,
    ) -> str:
        """
        Create the resource, and resolve's the current instance with
        the ID assigned that was assigned by the server.
        """
        if self.has_user_defined_name() and not re.match(
            r"^[a-z0-9_.-]{2,251}$", self.name, re.IGNORECASE
        ):
            raise ValidioError(
                f"invalid resource name '{self.name}': must be 2-253 "
                "characters containing only a-z, A-Z, 0-9, _, - or ."
            )

        create_input = self._api_create_input(namespace, ctx)
        payload = await self._api_create_or_update(
            "create", create_input, session=session
        )

        id_ = payload["id"]
        self._id.value = id_

        return id_

    async def _api_update(
        self,
        namespace: str,
        ctx: "DiffContext",
        session: Session,
    ) -> None:
        """Perform api call to update the resource."""
        update_input = self._api_update_input(namespace, ctx)
        await self._api_create_or_update("update", update_input, session=session)

    async def _api_create_or_update(
        self,
        verb: str,
        api_input: Any | None,
        session: Session,
    ) -> Any:
        if verb == "create":
            method_name = self._api_create_method_name()
            arguments = self._api_create_arguments()
        else:
            method_name = self._api_update_method_name()
            arguments = self._api_update_arguments()

        response_field = self._api_create_response_field_name()

        response = await execute_mutation(
            session,
            method_name,
            arguments,
            api_input,
            response_field,
            returns="id",
        )

        return self._check_graphql_response(
            response=response,
            method_name=method_name,
            response_field=response_field,
        )

    def _check_graphql_response(
        self,
        response: Any,
        method_name: str,
        response_field: str | None,
    ) -> Any:
        errors = response.get("errors")
        if errors:
            raise ValidioError(
                f"operation '{method_name}' failed for "
                f"resource {self.__class__.__name__}(name={self.name}): "
                f"{errors}"
            )

        if response_field is None:
            return None

        if response_field not in response:
            raise Exception(f"Unexpected response: {response}")

        if not response.get(response_field):
            raise ValidioError(
                f"operation '{method_name}' failed for '"
                f"resource {self.__class__.__name__}(name={self.name}): '"
                "missing response body"
            )

        return response[response_field]

    def _api_create_input(self, _namespace: str, _: "DiffContext") -> Any:
        """
        Returns the graphql input(s) to create this resource
        Returned value can either be the <Resource>CreateInput instance or
        if the create api takes in several arguments, then a dict[str, <Input>]
        that will be passed to the api.

        Default behavior (which should be overridden in most resource types) takes
        all fields on the resource, assumes that the field names match 1-1 with the
        corresponding input.

        Only root level objects such as credentials and channels should return
        the namespace, child resources will always inherit this value from its
        parent.
        """
        return _api_create_input_params(self)

    def _api_update_input(self, _namespace: str, _: "DiffContext") -> Any:
        """
        Similar to _api_create_input. Returns the graphql input(s) to
        update this resource.
        """
        return _api_update_input_params(self)

    def _api_delete_input(self) -> Any:
        """
        Returns the graphql input(s) to delete this resource. Most APIs do bulk
        deletes so we pass our own ID as a list but not all resources work this
        way.
        """
        return {"ids": [self._must_id()]}

    def _import_str(
        self,
        indent_level: int,
        import_ctx: "ImportContext",
        inits: list[tuple[str, Any, str | None]] | None = None,
        skip: set[str] | None = None,
    ) -> str:
        skip = set() if skip is None else skip
        params: list[tuple[str, Any, str | None]] = []

        if self.has_user_defined_name():
            params = [("name", repr(self.name), None)]

        if inits:
            params.extend(inits)

        for field, import_value in self._import_params().items():
            if field in skip:
                continue

            params.append(
                (
                    field,
                    _import_value_repr(
                        import_value.value, indent_level + 1, import_ctx
                    ),
                    import_value.comment,
                ),
            )

        return self._write_import_str(indent_level=indent_level, inits=params)

    def _import_params(self) -> dict[str, ImportValue]:
        return _import_resource_params(resource=self)

    def has_user_defined_name(self) -> bool:
        return True

    @abstractmethod
    def resource_class_name(self) -> str:
        """What type of resource this is. (e.g. Window, Segmentation etc)."""

    @abstractmethod
    def _encode(self) -> dict[str, object]:
        """Encode the resource as json."""

    def _api_secret_change_input(self) -> dict[str, Any]:
        nested_objects = {
            to_camel(f): obj._api_input()
            for f, obj in self._nested_secret_objects().items()
        }

        return {
            "input": {
                "id": self._must_id(),
                **{to_camel(f): getattr(self, f) for f in self._secret_fields()},
                **nested_objects,
            }
        }

    def _api_secret_change_response(
        self,
    ) -> dict[str, None | ApiSecretChangeNestedResource]:
        return {
            **{to_camel(secret_field): None for secret_field in self._secret_fields()},
            **self._nested_secret_objects(),
        }

    def _nested_secret_objects(self) -> dict[str, ApiSecretChangeNestedResource]:
        objects = {}
        for f in self._nested_objects():
            obj = getattr(self, f)
            if isinstance(obj, ApiSecretChangeNestedResource):
                objects[f] = obj

        return objects


class ResourceGraph:
    """
    ResourceGraph represents configuration as a graph of resources.

    A node in the graph represents an instance (identified by the resource name)
    of some resource like Window, Validator etc. and connected to that node are
    any child nodes - e.g. a Credential node will have child nodes of type
    Source, while a Source node will have child nodes of type Window,
    Segmentation, Validator.

    The Resource graph is the canonical datastructure that we work with - both
    the configuration as described from the user's code, as well as the configuration
    that exists on the server side at a given point in time, are represented by
    this graph.
    A node in the graph contains not only the configuration for the represented
    resource, but also internal metadata which we use to track dependency
    relationships that maintain the graph, as well as fields that are pending
    resolved values (waiting for concrete value from the API server).
    This enables us to do operations on it like diffing, dependency resolving etc.
    """

    _sub_graph_node_type = "sub_graph"

    def __init__(self) -> None:
        # Root nodes of each subgraph grouped by type. This contains resources
        # like credentials, channels that are at the top of our dependency trees
        self.sub_graphs = cast(
            # { "Credential": { "c1": { DemoCredential }, "c2": { GcpCredential } }
            dict[str, dict[str, Resource]],
            {
                # This is a type violation as a workaround so that we know
                # how to deserialize the value.
                NODE_TYPE_FIELD_NAME: ResourceGraph._sub_graph_node_type
            },
        )

        # Resource names are unique per resource type. This is used to track duplicate
        # names assignments to resources.
        self._resource_names_by_type: dict[str, set[str]] = {}
        self._deprecations: list[ResourceDeprecation] = []

    def add_deprecation(self, deprecation: ResourceDeprecation) -> None:
        """Add a deprecation warning for a resource.

        :param deprecation: Deprecation description
        """
        if self._deprecations is None:
            self._deprecations = []

        self._deprecations.append(deprecation)

    # Remembers that this name is in use for the specified resource type.
    # Throws an error if the specified name has been previously used.
    # the resource type.
    def allocate_resource_name(self, resource_name: str, resource: "Resource") -> None:
        resource_type: str = resource.resource_class_name()
        if resource_type not in self._resource_names_by_type:
            self._resource_names_by_type[resource_type] = set({})

        if resource_name in self._resource_names_by_type[resource_type]:
            raise ValidioError(
                f"duplicate name '{resource_name}' for type '{resource_type}'; resource"
                " names should be unique for the same resource type"
            )

        self._resource_names_by_type[resource_type].add(resource_name)

    def _add_root(self, resource: "Resource") -> None:
        """Adds a node to the root of a subgraph. Essentially creating
        a new subgraph.
        """
        self.allocate_resource_name(resource.name, resource)
        resource_class_name = resource.resource_class_name()
        if resource_class_name not in self.sub_graphs:
            self.sub_graphs[resource_class_name] = {}
        self.sub_graphs[resource_class_name][resource.name] = resource

    def _find_source(self, source_name: str) -> Optional["Source"]:
        from validio_sdk.resource.credentials import Credential
        from validio_sdk.resource.sources import Source

        if Credential.__name__ not in self.sub_graphs:
            return None

        for credential in self.sub_graphs[Credential.__name__].values():
            if Source.__name__ not in credential._children:
                continue
            if source_name not in credential._children[Source.__name__]:
                continue
            return cast(Source, credential._children[Source.__name__][source_name])

        return None

    def _encode(self) -> dict[str, object]:
        return without_skipped_internal_fields(self.__dict__)

    @staticmethod
    def _decode(obj: dict[str, dict[str, Any]]) -> tuple["ResourceGraph", DiffContext]:
        from validio_sdk.resource.channels import Channel
        from validio_sdk.resource.credentials import Credential
        from validio_sdk.resource.tags import Tag
        from validio_sdk.resource.validators import Validator

        # We decode a graph in two passes.
        # The first pass through the input does not decode
        # validators - this bit is where we transition into a non-linear
        # DAG structure because a validator can have several parents (it's
        # target, reference source). So we need to resolve all potential sources
        # before we can resolve validators in the second pass.
        g = ResourceGraph()

        ctx = DiffContext()

        # Pass 1 - decode credentials, channels, etc. which are at the 'root'
        # level and descends onto child resources.
        # Tags are decoded first to allow attaching them on any object.
        ResourceGraph._decode_root(obj, ctx, g, Tag, "tags")

        ResourceGraph._decode_root(obj, ctx, g, Credential, "credentials")

        # We decode the channels graph after the credentials one - since notification
        # rules depend on sources - so that the sources are resolved by the time decode
        # the rules.
        ResourceGraph._decode_root(obj, ctx, g, Channel, "channels")

        # Pass 2 Decode validators.
        Validator._decode_pending(ctx)

        return g, ctx

    @staticmethod
    def _decode_root(
        obj: dict[str, dict[str, Any]],
        ctx: DiffContext,
        g: "ResourceGraph",
        resource_cls: type,
        resource_module_name: str,
    ) -> None:
        if resource_cls.__name__ not in obj["sub_graphs"]:
            return

        sub_graphs = obj["sub_graphs"][resource_cls.__name__]
        for k, v in sub_graphs.items():
            if k == NODE_TYPE_FIELD_NAME:
                continue

            cls = eval(
                f"validio_sdk.resource.{resource_module_name}.{v[NODE_TYPE_FIELD_NAME]}"
            )
            resource = cast(Any, cls)._decode(ctx, cls, v, g)

            resources = getattr(ctx, resource_module_name)
            resources[resource.name] = resource
