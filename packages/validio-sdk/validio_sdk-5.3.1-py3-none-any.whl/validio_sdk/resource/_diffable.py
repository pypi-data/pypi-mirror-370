import inspect
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Optional

from camel_converter import to_camel

from validio_sdk.resource._serde import (
    IGNORE_CHANGES_FIELD_NAME,
    NODE_TYPE_FIELD_NAME,
    _import_value_repr,
)

if TYPE_CHECKING:
    from validio_sdk.code._import import ImportContext


class Diffable(ABC):
    """
    An abstract class to be implemented by objects that can be diff-ed against the
    server version. All Resource instances implement this by default. And in some
    cases (like filters, thresholds etc.), nested objects of a resource need to be
    diff-ed and require such objects require an implementation of this base.

    NOTE: When adding/removing fields to any resource or object contained
    within a resource be sure to account for how that field should be diffed.
    Every field reachable from a resource, should be returned by exactly one
    of the listed APIs here, with the exception of `_replace_on_type_change_fields`
    which can overlap with `_nested_objects`.
    """

    @abstractmethod
    def _immutable_fields(self) -> set[str]:
        """Returns the fields on the object that do not allow updates."""

    @abstractmethod
    def _mutable_fields(self) -> set[str]:
        """Returns the fields on the object that can be updated."""

    def _secret_fields(self) -> set[str]:
        """Returns the fields that are considered secret and sensitive."""
        return set({})

    @abstractmethod
    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        """Returns any nested objects contained within this object.

        Nested objects will be diff-ed recursively.
        ...
        :returns dict[field, Optional[object]].
        """

    def __iter__(self) -> Iterator[Any]:
        yield from self.__dict__.items()

    def _ignored_fields(self) -> set[str]:
        """Returns any fields on the object that can should not be diffed."""
        return set({})

    def _all_fields(self) -> set[str]:
        """Return all fields of the resource."""
        return {
            *self._immutable_fields(),
            *self._mutable_fields(),
            *self._nested_objects().keys(),
            *self._ignored_fields(),
        }

    def _replace_on_type_change_fields(self) -> set[str]:
        """Returns the fields on the object whose type is not allowed to change."""
        return set({})

    def _import_str(
        self,
        indent_level: int,
        import_ctx: "ImportContext",
        inits: list[tuple[str, Any, str | None]] | None = None,
        skip_fields: set[str] | None = None,
    ) -> str:
        params = list(inits or [])

        for f in list(inspect.signature(self.__class__).parameters):
            # If the field is already provided as an init arg then skip,
            # since that means we have a value already.
            if next((True for p in params if p[0] == f), None) or (
                skip_fields and f in skip_fields
            ):
                continue

            params.append(
                (
                    f,
                    _import_value_repr(
                        value=getattr(self, f),
                        indent_level=indent_level + 1,
                        import_ctx=import_ctx,
                    ),
                    None,
                )
            )

        return self._write_import_str(indent_level=indent_level, inits=params)

    def _write_import_str(
        self, indent_level: int, inits: list[tuple[str, str, str | None]] | None = None
    ) -> str:
        from validio_sdk.resource._resource import DiffContext

        params = list(inits or [])

        # Sort the constructor arguments so that we have a stable order in the output.
        # Parent resource parameters are special, so we list them first - before params
        # of the actual resource.
        parent_resource_name_fields = list(DiffContext.fields_singular())
        parent_resource_name_fields.sort()
        sorted_params = []
        for f in ["name", IGNORE_CHANGES_FIELD_NAME, *parent_resource_name_fields]:
            for i, param in enumerate(params):
                if param[0] == f:
                    sorted_params.append(param)
                    del params[i]
        # Add the remaining in sort order
        params.sort(key=lambda p: p[0])
        for param in params:
            sorted_params.append(param)

        line_indent = "\n" + (" " * self._num_ident_spaces(indent_level + 1))
        import_args = []
        for field, arg, comment in sorted_params:
            comment_str = "" if not comment else f" # {comment}"
            import_args.append(f"{field}={arg},{comment_str}")

        params_str = line_indent.join(import_args)
        closing_indent = " " * self._num_ident_spaces(indent_level)
        cls = self.__class__.__name__
        return f"{cls}({line_indent}{params_str}\n{closing_indent})"

    @staticmethod
    def _num_ident_spaces(indent_level: int) -> int:
        return 4 * indent_level


class ApiSecretChangeNestedResource(Diffable):
    """An interface for nested structure inside a list of secret fields."""

    @abstractmethod
    def _api_variant_name(self) -> str:
        """Returns the oneof graphql property name for the secret."""

    def _fields(self) -> set[str]:
        """Returns the API properties of the object as key value pairs."""
        return {
            *self._immutable_fields(),
            *self._mutable_fields(),
            *self._secret_fields(),
        }

    def _encode(self) -> dict[str, object]:
        data = self.__dict__
        data[NODE_TYPE_FIELD_NAME] = self.__class__.__name__
        return data

    @staticmethod
    def _decode(
        type_: type,
        obj: dict[str, dict[str, object]],
    ) -> "Any":
        return type_(**{k: v for k, v in obj.items() if k != NODE_TYPE_FIELD_NAME})

    def _api_create_input(self) -> dict[str, Any]:
        """Returns the create input of the object."""
        return self._api_input()

    def _api_update_input(self) -> dict[str, Any]:
        """Returns the update input of the object."""
        return self._api_input()

    def _api_input(self) -> dict[str, Any]:
        """Returns the API input of the object."""
        return {
            self._api_variant_name(): {
                to_camel(f): getattr(self, f) for f in self._fields()
            }
        }

    def _api_secret_change_auth_query(self) -> str:
        """Returns the GraphQL query with fragments for the API secret change."""
        fields = "\n".join([to_camel(f) for f in self._secret_fields()])
        return f"""
        ... on {self.__class__.__name__}SecretChangedResult {{
            {fields}
        }}
        """

    def _api_secret_change_auth_response_fields(self) -> dict[str, bool]:
        """Returns a list of expected fields for response of the API secret change."""
        return {to_camel(f): True for f in self._secret_fields()}
