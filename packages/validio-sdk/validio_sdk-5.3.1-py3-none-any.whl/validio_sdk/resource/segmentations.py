"""Segmentation configuration."""

import typing
from enum import Enum
from typing import TYPE_CHECKING, Any

from validio_sdk import ValidioError
from validio_sdk.resource._resource import Resource
from validio_sdk.resource._serde import (
    _api_create_input_params,
    _api_update_input_params,
    _encode_resource,
    get_config_node,
)
from validio_sdk.resource.filters import Filter
from validio_sdk.resource.sources import Source

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext


class SegmentUsage(str, Enum):
    """
    Segment usage maps to an expected (maximum) number of segments.
    Values go from fewest (minimal) to most (maximal) expected segments for
    the segmentation. The higher the value, the shorter the retention period
    will be.

    See docmentation for exact numbers:
    https://docs.validio.io/docs/segmentation-configuration#segment-usage-options
    """

    MINIMAL = "MINIMAL"
    LIGHT = "LIGHT"
    MEDIUM = "MEDIUM"
    HEAVY = "HEAVY"
    EXTREME = "EXTREME"
    MAXIMAL = "MAXIMAL"


class Segmentation(Resource):
    """A segmentation resource.

    https://docs.validio.io/docs/segmentation
    """

    def __init__(
        self,
        *,
        name: str,
        source: Source,
        fields: list[str] | None = None,
        filter: Filter | None = None,
        segment_usage: SegmentUsage | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the segmentation.
        :param source: The source to attach the segmentation to.
        :param fields: Fields to segment on.
        :param filter: Optional filter in data to be processed by validators
            that will be attached to this segmentation.
        :param segment_usage: Represents the expected segment usage for this
          segmentation.
        :param display_name: Human-readable name for the segmentation. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=source._resource_graph,
        )
        self.source_name: str = source.name
        self.fields: list[str] = fields if fields else []
        self.filter_name = filter.name if filter else None

        self.segment_usage = (
            # When we decode, enums are passed in as strings
            segment_usage
            if isinstance(segment_usage, (type(None), SegmentUsage))
            else SegmentUsage(segment_usage)
        )

        if self.segment_usage is None:
            self.add_deprecation(
                "Segment usage is a new required parameter. For the moment the "
                "server value will be used if not specified in the manifest but "
                "this will change in a future release."
            )

        source.add(self.name, self)

    def _immutable_fields(self) -> set[str]:
        return {"source_name", "fields", "segment_usage"}

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            "filter_name",
        }

    def resource_class_name(self) -> str:
        """Returns the class name."""
        return "Segmentation"

    def _encode(self) -> dict[str, object]:
        # Drop fields here that are not part of the constructor for when
        # we deserialize back. They will be reinitialized by the constructor.
        return _encode_resource(self, skip_fields={"source_name"})

    @staticmethod
    def _decode(
        ctx: "DiffContext",
        obj: dict[str, Any],
        source: Source,
    ) -> "Segmentation":
        args = get_config_node(obj)

        filter_name = typing.cast(str, args["filter_name"])
        # Drop filter_name since it is not part of the constructor.
        # It will be reinitialized by the constructor.
        del args["filter_name"]

        if filter_name and filter_name not in ctx.filters:
            raise ValidioError(f"invalid configuration: no such filter {filter_name}")
        filter_ = ctx.filters.get(filter_name) if filter_name else None

        return Segmentation(
            **{
                **args,
                "source": source,
                "filter": filter_,
            }  # type:ignore
        )

    def _api_create_input(self, _namespace: str, ctx: "DiffContext") -> Any:
        return _api_create_input_params(
            self,
            overrides={
                "sourceId": ctx.sources[self.source_name]._must_id(),
                **self._filter_api_input(ctx),
            },
        )

    def _api_update_input(self, _namespace: str, ctx: "DiffContext") -> Any:
        return _api_update_input_params(self, overrides=self._filter_api_input(ctx))

    def _filter_api_input(self, ctx: "DiffContext") -> dict[str, str | None]:
        return {
            "filterId": (
                ctx.filters[self.filter_name]._must_id() if self.filter_name else None
            )
        }
