"""Plan command implementation."""

import json
import os
import pathlib
import subprocess
import sys
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any

from validio_sdk._api.api import APIClient
from validio_sdk.code import scaffold
from validio_sdk.code._progress import ProgressBar
from validio_sdk.code.settings import dump_graph_var, graph_preamble_var
from validio_sdk.exception import ValidioBugError, ValidioError
from validio_sdk.resource._diff import GraphDiff, diff_resource_graph
from validio_sdk.resource._diffable import Diffable
from validio_sdk.resource._resource import (
    DiffContext,
    Resource,
    ResourceDeprecation,
    ResourceGraph,
)
from validio_sdk.resource._server_resources import load_resources
from validio_sdk.resource._util import SourceSchemaReinference
from validio_sdk.resource.channels import WebhookChannel
from validio_sdk.resource.tags import Tag


@dataclass
class PlanResult:
    """Result from a `plan` operation."""

    graph_diff: GraphDiff
    diff_context: DiffContext
    tags_context: DiffContext
    deprecations: list[ResourceDeprecation]


@dataclass
class ResourceNames:
    """Holds names for resource types, can be used for retaining."""

    tags: set[str] = field(default_factory=set)
    credentials: set[str] = field(default_factory=set)
    channels: set[str] = field(default_factory=set)
    sources: set[str] = field(default_factory=set)
    windows: set[str] = field(default_factory=set)
    filters: set[str] = field(default_factory=set)
    segmentations: set[str] = field(default_factory=set)
    validators: set[str] = field(default_factory=set)
    notification_rules: set[str] = field(default_factory=set)

    def size(self) -> int:
        """Get the size of resources.

        Return the total number of items in all sets.
        """
        all_field_names = [k.name for k in fields(self)]
        all_fields = [len(getattr(self, field)) for field in all_field_names]

        return sum(all_fields)


async def plan(
    namespace: str,
    client: APIClient,
    directory: pathlib.Path,
    schema_reinference: SourceSchemaReinference,
    destroy: bool,
    no_capture: bool,
    show_secrets: bool,
    targets: ResourceNames = ResourceNames(),
    import_mode: bool = False,
    show_progress: bool = True,
) -> PlanResult:
    """Computes a diff between the manifest program and the live server resources."""
    progress_bar = ProgressBar(
        description="Loading project",
        # The step count includes 1 step for each resource type that we load, as
        # well as two additional steps for loading the manifest and computing the diff.
        total=len(DiffContext.fields()) + 2,
        show_progress=show_progress,
    )
    with progress_bar:
        async with client.client as session:
            if not destroy:
                manifest_ctx, deprecations = _get_manifest_graph(directory, no_capture)
            else:
                manifest_ctx, deprecations = DiffContext(), []
            progress_bar.update(advance=1)

            server_ctx = await load_resources(namespace, session, progress_bar)

            progress_bar.update(description="Computing diff")
            diff = await diff_resource_graph(
                namespace=namespace,
                session=session,
                schema_reinference=schema_reinference,
                show_secrets=show_secrets,
                manifest_ctx=manifest_ctx,
                server_ctx=server_ctx,
                import_mode=import_mode,
            )
            diff.retain(targets)
            progress_bar.update(advance=1)

    tags_ctx = _get_tags_context(diff.to_delete, manifest_ctx)

    return PlanResult(diff, manifest_ctx, tags_ctx, deprecations)


def _get_tags_context(delete_ctx: DiffContext, manifest: DiffContext) -> DiffContext:
    # Tags are never deleted or updated and this will never appear in the diff's
    # `to_delete` or `to_update`. This information is needed e.g. when doing
    # import and a resource is referencing a tag.
    #
    # Since we can't from the `to_delete` context which tags are already in the
    # manifest (if any) or not we create this specific tags context that only
    # contains tags. This will be that tags that exist in the manifest and is
    # used on a resource that only exist on the server (i.e. a resource found in
    # `to_delete`.
    tags_ctx = DiffContext()

    for resource_field in delete_ctx.fields():
        resource_type = getattr(delete_ctx, resource_field)

        for _, resource in resource_type.items():
            if not hasattr(resource, "tag_names"):
                continue

            for name in resource.tag_names:
                # The tag already exist in the existing manifest resources.
                if name in manifest.tags:
                    continue

                # The tag has already been seen on a different resource.
                if name in tags_ctx.tags:
                    continue

                key, value = Tag._key_and_value_from_unique_name(name)

                # The tag isn't relevant to its position in the graph when doing
                # import, we know at this point that some resource references a
                # tag that's not in the existing manifest so we must create it.
                tags_ctx.tags[name] = Tag(
                    key=key,
                    value=value,
                    __internal__=ResourceGraph(),
                )

    return tags_ctx


def _get_manifest_graph(
    directory: pathlib.Path, no_capture: bool
) -> tuple[DiffContext, list[ResourceDeprecation]]:
    """Runs the manifest program and captures its output into a ResourceGraph."""
    process_env = os.environ.copy()
    process_env[dump_graph_var] = "1"
    child = subprocess.run(
        [sys.executable, directory / scaffold.main_file_name],
        cwd=directory,
        env=process_env,
        capture_output=True,
        text=True,
        check=False,
    )

    if child.returncode != 0:
        raise ValidioError(
            f"{child.stderr}\n"
            f"{scaffold.main_file_name} terminated with a non-zero exit code: "
            f"{child.returncode}"
        )

    raw_output: str = child.stdout
    graph, ctx, captured_output = _extract_resource_graph(raw_output, child)
    if no_capture and captured_output:
        print(captured_output)

    return ctx, graph._deprecations


# Parse the graph from the child program's output. Returns also any captured stdout
# of the child program.
def _extract_resource_graph(
    raw_output: str,
    child: subprocess.CompletedProcess,
) -> tuple[ResourceGraph, DiffContext, str]:
    preamble_start_idx: int = raw_output.find(graph_preamble_var)
    if preamble_start_idx < 0:
        return ResourceGraph(), DiffContext(), ""

    std_output = raw_output[:preamble_start_idx]

    graph_str = raw_output[preamble_start_idx + len(graph_preamble_var) :].strip()
    if len(graph_str) == 0:
        raise ValidioBugError(
            f"Missing resource graph from manifest program:\n{child.stderr}"
        )

    try:
        graph_json = json.loads(graph_str)
    except json.decoder.JSONDecodeError as e:
        # We wrap the error here, because otherwise the exception thrown by
        # JSON parser can be cryptic if it lands in the terminal on its own.
        raise ValidioError(f"failed to decode resource graph: {e.msg}")
    except Exception as e:
        # Fallback to just print the whole stack trace
        raise ValidioError(f"failed to load resource graph output JSON: {e}")

    graph, ctx = ResourceGraph._decode(graph_json)

    # Some deprecations are only possible to detect when building the resource
    # graph such as type deprecations. Instead of relying on the resources to
    # properly register the deprecations again, we set them to what got
    # generated in the resource graph.
    graph._deprecations = [
        ResourceDeprecation(**x) for x in graph_json.get("_deprecations", [])
    ]

    return graph, ctx, std_output


# ruff: noqa: PLR0912
def _create_resource_diff_object(
    r: Resource | Diffable | dict,
    show_secrets: bool,
    rewrites: dict[str, Any] | None = None,
    secret_fields_changed: dict[str, Any] | None = None,
    is_manifest: bool = False,
) -> dict[str, object]:
    if rewrites is None:
        rewrites = {}

    if secret_fields_changed is None:
        secret_fields_changed = {}

    data = dict(r) if not isinstance(r, dict) else r

    diff_object = {}
    for k, v in data.items():
        if k.startswith("_"):
            continue

        if k in rewrites:
            diff_object[k] = rewrites[k]
        elif isinstance(v, Resource | Diffable | dict):
            ch = secret_fields_changed.get(k)
            diff_object[k] = _create_resource_diff_object(
                v,
                show_secrets,
                secret_fields_changed=ch if not isinstance(ch, bool) else {},
                is_manifest=is_manifest,
            )
        elif hasattr(v, "__dict__") and not isinstance(v, Enum):
            ch = secret_fields_changed.get(k)
            diff_object[k] = _create_resource_diff_object(
                v.__dict__,
                show_secrets,
                secret_fields_changed=ch if not isinstance(ch, bool) else {},
                is_manifest=is_manifest,
            )
        elif isinstance(v, list):
            if len(v) == 0 or not isinstance(v[0], Diffable):
                diff_object[k] = v
                continue

            items = []
            for item in v:
                items.append(
                    _create_resource_diff_object(
                        item.__dict__,
                        show_secrets,
                        is_manifest=is_manifest,
                    )
                )

            diff_object[k] = items
        else:
            diff_object[k] = v

    # Mask any sensitive info if requested.
    if not show_secrets and hasattr(r, "_secret_fields"):
        secret_fields = r._secret_fields()

        if secret_fields:
            for field in secret_fields:
                # We want to avoid overriding webhook_url if it is None already
                # which may give a misleading impression that it is set to a value.
                #
                # For any channel that is not the WebhookChannel, we will always
                # flag it as changed if any secrets have changed, which is consistent
                # with existing behavior.
                #
                # This workaround until webhook URL is deprecated fully from some
                # channels (VR-4047).
                flag_webhook_url_as_changed = False
                if not isinstance(r, WebhookChannel) and field == "webhook_url":
                    if hasattr(r, "webhook_url") and not r.webhook_url:
                        continue
                    if any(
                        secret_fields_changed[secret_field]
                        for secret_field in secret_fields_changed
                    ):
                        flag_webhook_url_as_changed = True

                if (
                    # Special case handling for webhook URL
                    flag_webhook_url_as_changed
                    or
                    # If the field does not exist in the secrets changed dict then
                    # don't flag it as changed
                    secret_fields_changed.get(field)
                ) and not is_manifest:
                    diff_object[field] = "REDACTED-PREVIOUS"
                else:
                    diff_object[field] = "REDACTED"

    return diff_object
