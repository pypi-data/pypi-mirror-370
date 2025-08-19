"""Tags configuration."""

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from validio_sdk.resource._resource import Resource, ResourceGraph
from validio_sdk.resource._resource_graph import RESOURCE_GRAPH
from validio_sdk.resource._serde import (
    IGNORE_CHANGES_FIELD_NAME,
    _encode_resource,
    get_config_node,
    with_resource_graph_info,
)

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext

UNIQUE_NAME_DELIMITER = ":"


class Tag(Resource):
    """
    A tag can only be added as a resource but not yet updated or deleted.
    Reason being that tags are global and not bound to your namespace but you
    should still be able to use them in your project.

    https://docs.validio.io/docs/managing-tags
    """

    def __init__(
        self,
        key: str,
        value: str | None = None,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param key: The key for the tag
        :param value: Optional value for the tag
        """
        super().__init__(
            name=Tag._unique_name(key, value),
            display_name=None,
            ignore_changes=False,
            __internal__=__internal__ or RESOURCE_GRAPH,
        )

        self.key = key
        self.value = value

        self._resource_graph._add_root(self)

    def __iter__(self) -> Iterator[Any]:
        """Custom iterator.

        Since tags are not real resources we impalement our own custom iterator.
        By doing this we can show a better diff to the user without traditional
        fields such as `name`, `ignore_changes` etc.
        """
        yield from {"key": self.key, "value": self.value}.items()

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "Tag"

    @staticmethod
    def _unique_name(key: str, value: str | None) -> str:
        """
        Return a unique name for the key-value pair. It's safe to join on `:` as
        a separator since we don't allow keys or values to contain `:` so
        there's no risk that `key:` + `value` would be the same as `key` +
        `:value`.

        :retunrs: A unique string
        """
        if value is None:
            return key

        return f"{key}:{value}"

    @staticmethod
    def _key_and_value_from_unique_name(unique_name: str) -> tuple[str, str | None]:
        if UNIQUE_NAME_DELIMITER not in unique_name:
            return (unique_name, None)

        key, value = unique_name.split(UNIQUE_NAME_DELIMITER, maxsplit=1)

        # We first do the split then always return a tuple to make the type
        # checker happy.
        return (key, value)

    def _immutable_fields(self) -> set[str]:
        return set()

    def _mutable_fields(self) -> set[str]:
        return {"key", "value"}

    def _api_create_input(self, _namespace: str, _: "DiffContext") -> Any:
        return {
            "input": {
                "key": self.key,
                "value": self.value,
            }
        }

    def _encode(self) -> dict[str, object]:
        return _encode_resource(self, skip_fields={"display_name", "name"})

    def has_user_defined_name(self) -> bool:
        """Returns if a resource has a user defined name."""
        return False

    @staticmethod
    def _decode(
        _ctx: "DiffContext",
        _cls: type,
        obj: dict[str, dict[str, object]],
        g: ResourceGraph,
    ) -> "Tag":
        config = get_config_node(obj)
        args = with_resource_graph_info(config, g)
        del args[IGNORE_CHANGES_FIELD_NAME]

        return Tag(**args)  # type: ignore
