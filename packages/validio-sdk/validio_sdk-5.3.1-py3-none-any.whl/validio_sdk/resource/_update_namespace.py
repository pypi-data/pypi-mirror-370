import dataclasses
import inspect
from typing import cast

from validio_sdk._api.api import APIClient
from validio_sdk.exception import ValidioError
from validio_sdk.resource._resource import DiffContext, Resource, ResourceGraph
from validio_sdk.resource._server_resources import load_channels, load_credentials
from validio_sdk.resource.channels import Channel
from validio_sdk.resource.credentials import Credential

_max_recursion_depth = 20


@dataclasses.dataclass
class ResourceNamesToMove:
    credentials: set[str]
    channels: set[str]

    def is_empty(self) -> bool:
        return sum([len(getattr(self, field)) for field in self._fields()]) == 0

    @staticmethod
    def _fields() -> list[str]:
        return list(inspect.signature(ResourceNamesToMove).parameters)


@dataclasses.dataclass
class ResourcesToMove:
    credentials: dict[str, Credential]
    channels: dict[str, Channel]

    def is_empty(self) -> bool:
        return sum([len(getattr(self, field)) for field in self._fields()]) == 0

    def count(self) -> int:
        return sum([len(getattr(self, field)) for field in self._fields()])

    @staticmethod
    def _fields() -> list[str]:
        return list(inspect.signature(ResourceNamesToMove).parameters)


async def get_resources_to_move(
    namespace: str,
    client: APIClient,
    resource_names: ResourceNamesToMove,
) -> ResourcesToMove:
    g = ResourceGraph()
    ctx = DiffContext()

    async with client.client as session:
        await load_credentials(namespace, g, ctx, session)
        await load_channels(namespace, g, ctx, session)

    # If no targeted resources, then look to move all resources from
    # the targeted namespace.
    move_all = resource_names.is_empty()

    credentials = {
        name: c
        for name, c in ctx.credentials.items()
        if move_all or name in resource_names.credentials
    }
    channels = {
        name: ch
        for name, ch in ctx.channels.items()
        if move_all or name in resource_names.channels
    }

    return ResourcesToMove(
        credentials=credentials,
        channels=channels,
    )


async def apply_move(
    namespace: str,
    client: APIClient,
    new_namespace: str,
    resources_to_move: ResourcesToMove,
) -> None:
    entries = [
        (
            "credentialNamespaceUpdate",
            cast(
                dict[str, Resource],
                resources_to_move.credentials,
            ),
        ),
        (
            "channelNamespaceUpdate",
            cast(
                dict[str, Resource],
                resources_to_move.channels,
            ),
        ),
    ]
    for method_name, resources in entries:
        for name, resource in resources.items():
            response = await client.execute_mutation(
                method_name,
                argument_types={"input": "ResourceNamespaceUpdateInput!"},
                variable_values={
                    "input": {
                        "resourceName": name,
                        "namespaceId": namespace,
                        "newNamespaceId": new_namespace,
                    }
                },
                returns=None,
            )

            if response["errors"]:
                raise ValidioError(
                    f"operation '{method_name}' failed for resource "
                    f"{resource.__class__.__name__}(name={resource.name}): "
                    f"{response['errors']}"
                )
