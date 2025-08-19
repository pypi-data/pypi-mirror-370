from typing import TypeVar

from validio_sdk.exception import ValidioError
from validio_sdk.resource._resource import DiffContext, Resource
from validio_sdk.resource.channels import Channel
from validio_sdk.resource.credentials import Credential
from validio_sdk.resource.filters import Filter
from validio_sdk.resource.segmentations import Segmentation
from validio_sdk.resource.sources import Source
from validio_sdk.resource.tags import Tag
from validio_sdk.resource.windows import Window

R = TypeVar("R", bound=Resource)


def must_find_credential(ctx: DiffContext, name: str) -> Credential:
    return must_find_resource("Credential", ctx.credentials, name)


def must_find_source(ctx: DiffContext, name: str) -> Source:
    return must_find_resource("Source", ctx.sources, name)


def must_find_window(ctx: DiffContext, name: str) -> Window:
    return must_find_resource("Window", ctx.windows, name)


def must_find_segmentation(ctx: DiffContext, name: str) -> Segmentation:
    return must_find_resource("Segmentation", ctx.segmentations, name)


def must_find_filter(ctx: DiffContext, name: str) -> Filter:
    return must_find_resource("Filter", ctx.filters, name)


def must_find_channel(ctx: DiffContext, name: str) -> Channel:
    return must_find_resource("Channel", ctx.channels, name)


def must_find_tag(ctx: DiffContext, name: str) -> Tag:
    return must_find_resource("Tag", ctx.tags, name)


def must_find_resource(resource_type: str, resources: dict[str, R], name: str) -> R:
    if name not in resources:
        raise ValidioError(
            f"could not find {resource_type} '{name}' in server resource list"
        )

    return resources[name]
