"""Utils for computing replacement diffs on resources."""

import dataclasses
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from validio_sdk.resource._diff import ResourceUpdate


class ReplacementReason:
    """Contains info around why a resource is being replaced."""

    @abstractmethod
    def _reason(self) -> str:
        """Returns a string explaining the replacement reason."""


@dataclass
class ReplacementContext:
    """Contains info around why a resource is being replaced. Grouped by type."""

    credentials: dict[str, ReplacementReason] = dataclasses.field(default_factory=dict)
    channels: dict[str, ReplacementReason] = dataclasses.field(default_factory=dict)
    sources: dict[str, ReplacementReason] = dataclasses.field(default_factory=dict)
    windows: dict[str, ReplacementReason] = dataclasses.field(default_factory=dict)
    filters: dict[str, ReplacementReason] = dataclasses.field(default_factory=dict)
    segmentations: dict[str, ReplacementReason] = dataclasses.field(
        default_factory=dict
    )
    validators: dict[str, ReplacementReason] = dataclasses.field(default_factory=dict)
    notification_rules: dict[str, ReplacementReason] = dataclasses.field(
        default_factory=dict
    )

    # Tags are just here to allow us to resolve the name from the type but it
    # will never be set since we only create tags from IaC. Rather than doing
    # code branches whenever we rely on `DiffContext.fields()` we ensure
    # `ReplacementContext` conforms to the same signature.
    tags: dict[str, ReplacementReason] = dataclasses.field(default_factory=dict)


class CascadeReplacementReason(ReplacementReason):
    """
    Represents a replacement occurring on a child resource, due to the
    parent resource being replaced.
    """

    def __init__(
        self,
        parent_resource_cls: type,
        parent_resource_name: str,
    ):
        """
        :param parent_resource_cls: The Class object of the parent resource.
        :param parent_resource_name: The parent resource name.
        """
        self.parent_resource_cls = parent_resource_cls
        self.parent_resource_name = parent_resource_name

    def _reason(self) -> str:
        return (
            f"cascading replacement from "
            f"{self.parent_resource_cls.__name__}"
            f'(name="{self.parent_resource_name}")'
        )

    def __eq__(self, other: object) -> bool:
        """Overrides eq."""
        if not isinstance(other, self.__class__):
            return False
        return (
            self.parent_resource_cls == other.parent_resource_cls
            and self.parent_resource_name == other.parent_resource_name
        )


class ImmutableFieldReplacementReason(ReplacementReason):
    """
    Represents a replacement occurring on a resource, due to an update
    to an immutable field on the resource.
    """

    def __init__(
        self,
        field_name: str,
        resource_update: "ResourceUpdate",
    ):
        """
        :param field_name: The immutable field that triggered the replacement.
        :param resource_update: The resource diff.
        """
        self.field_name = field_name
        self.resource_update = resource_update

    def _reason(self) -> str:
        return f"immutable field '{self.field_name}' was updated"

    def __eq__(self, other: object) -> bool:
        """Overrides eq."""
        if not isinstance(other, self.__class__):
            return False
        return (
            self.field_name == other.field_name
            and self.resource_update == other.resource_update
        )
