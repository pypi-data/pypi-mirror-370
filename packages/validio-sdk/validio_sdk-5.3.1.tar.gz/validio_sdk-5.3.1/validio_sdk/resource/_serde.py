import typing
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable

from camel_converter import to_camel

from validio_sdk.exception import ValidioError

if TYPE_CHECKING:
    from validio_sdk.code._import import ImportContext
    from validio_sdk.resource._diffable import Diffable
    from validio_sdk.resource._resource import Resource

"""
These are fields in a node of the graph that contains links to the resource graph
itself or other internal fields that we don't need to serialise. We ignore these
during encoding.
"""
SKIPPED_INTERNAL_FIELD_NAMES = {
    "_resource_names_by_type",
    "_resource_graph",
    "_id",
    "_applied",
    "_namespace",
}

"""
Contains the type (unique hardcoded name) of the current node.
Allows us know how to decode that node.
"""
NODE_TYPE_FIELD_NAME = "_node_type"

"""Contains the child nodes for the current node in the graph."""
CHILDREN_FIELD_NAME = "_children"

"""Contains the config values of a resource when we encode that resource."""
CONFIG_FIELD_NAME = "config_field"

"""
Field name used to flag ignore_changes on resources.
"""
IGNORE_CHANGES_FIELD_NAME = "ignore_changes"

"""
These are fields in a node of the graph, that contain metadata as opposed to
actual configuration values. While we work with the graph (e.g. when
encoding/decoding, diffing etc.), we need special handling for them
whenever they show up.
"""
INTERNAL_FIELD_NAMES: set[str] = {
    NODE_TYPE_FIELD_NAME,
    CHILDREN_FIELD_NAME,
    IGNORE_CHANGES_FIELD_NAME,
}.union(SKIPPED_INTERNAL_FIELD_NAMES)


def custom_resource_graph_encoder(obj: Any) -> None:
    if callable(getattr(obj, "_encode", None)):
        return obj._encode()
    raise ValidioError(f"failed to encode graph: missing encoder for {obj}")


def _encode_resource(
    obj: "Resource", skip_fields: set[str] | None = None
) -> dict[str, object]:
    """
    Helper method to encode a node in the graph that corresponds to a Resource instance.

    :param obj: the node to be encoded
    :param skip_fields: These fields will ignored during encoding
    ...
    :returns: JSON compatible encoded value
    """
    # For the encoding, we group all actual config fields in it's dedicated section.
    # The config fields correspond to parameters that go into the Resource's constructor
    # so this lets us automatically decode the value back into the Resource using its
    # constructor.
    config_fields = {}
    # Internal fields are everything else that isn't config field. These are encoded
    # as is unless they have a custom encoder.
    internal_fields = {}

    skip_fields = (skip_fields or set({})).union(
        {
            # We will recursively encode the children so skip the field.
            CHILDREN_FIELD_NAME,
        }
    )
    for field, value in obj.__dict__.items():
        if field in skip_fields:
            continue

        if field in INTERNAL_FIELD_NAMES:
            internal_fields[field] = value
        else:
            config_fields[field] = (
                value._encode() if callable(getattr(value, "_encode", None)) else value
            )

    return without_skipped_internal_fields(
        {
            **internal_fields,
            CONFIG_FIELD_NAME: config_fields,
            **obj._encode_children(),
        }
    )


def decode_nested_objects(
    obj: dict[str, Any], cls_eval: typing.Callable[[str], type]
) -> None:
    """Autodetect and decode any nested fields in input json object."""
    for field, nested_obj in obj.items():
        if not isinstance(nested_obj, dict):
            continue

        nested_obj_cls_name = nested_obj.pop(NODE_TYPE_FIELD_NAME, None)
        if not nested_obj_cls_name:
            continue

        nested_obj_cls = cls_eval(nested_obj_cls_name)
        obj[field] = typing.cast(Any, nested_obj_cls)._decode(
            nested_obj_cls, nested_obj
        )


def get_children_node(obj: dict[str, dict[str, object]]) -> dict[str, object]:
    if CHILDREN_FIELD_NAME in obj:
        return obj[CHILDREN_FIELD_NAME]
    return {}


def get_config_node(obj: dict[str, dict[str, object]]) -> dict[str, object]:
    if CONFIG_FIELD_NAME in obj:
        config_node = dict(obj[CONFIG_FIELD_NAME])
        config_node[IGNORE_CHANGES_FIELD_NAME] = get_ignore_changes(obj)
        return config_node
    return {}


def get_ignore_changes(obj: dict[str, dict[str, object]]) -> bool:
    if IGNORE_CHANGES_FIELD_NAME in obj:
        return bool(obj[IGNORE_CHANGES_FIELD_NAME])
    return False


def without_skipped_internal_fields(
    obj: dict[str, dict[str, object]],
) -> dict[str, object]:
    """Remove the resource graph info from the object we want to serialize."""
    return {k: v for k, v in obj.items() if k not in SKIPPED_INTERNAL_FIELD_NAMES}


def with_resource_graph_info(obj: dict[str, object], g: object) -> dict[str, object]:
    """Adds back the resource graph info to the object we're deserializing."""
    return {**obj, "__internal__": g}


def _api_input(
    resource: "Resource",
    overrides: dict[str, Any] | None = None,
    skip_fields: set[str] | None = None,
    root_key_name: str = "input",
    skip_fn: Callable | None = None,
) -> dict[str, Any]:
    from validio_sdk.resource._resource import DiffContext

    overrides = overrides if overrides else {}
    skip_fields = set() if skip_fields is None else skip_fields

    # Resources that doesn't have a display name, e.g. windows, needs to
    # avoid sending `name` to the API so they explicitly pass it as a skipped
    # field.
    display_name = {"name": resource.display_name} if "name" not in skip_fields else {}

    name_fields = {f"{r}_name" for r in DiffContext.fields_singular()}

    skip_fields = {
        *set(overrides.keys()),
        *set(resource._nested_objects().keys()),
        *skip_fields,
        "name",
        "resourceName",
        "displayName",
        "resourceNamespace",  # deprecated in favor of namespace_id
        "namespaceId",
    }

    api_input = {}

    for field in resource._all_fields():
        if skip_fn is not None and skip_fn(field):
            continue

        if field in name_fields:
            continue

        camel_field = to_camel(field)
        if camel_field in skip_fields or field in skip_fields:
            continue

        value = getattr(resource, field)
        if isinstance(value, Enum):
            value = value.value

        api_input[camel_field] = value

    return {
        root_key_name: {
            **api_input,
            **overrides,
            **display_name,
        }
    }


def _api_create_input_params(
    resource: "Resource",
    overrides: dict[str, Any] | None = None,
    skip_fields: set[str] | None = None,
    root_key_name: str = "input",
) -> dict[str, Any]:
    overrides = {
        **(overrides if overrides is not None else {}),
        "resourceName": resource.name,
    }

    return _api_input(resource, overrides, skip_fields, root_key_name)


def _api_update_input_params(
    resource: "Resource",
    overrides: dict[str, Any] | None = None,
    skip_fields: set[str] | None = None,
    root_key_name: str = "input",
) -> dict[str, Any]:
    def skip_fn(value: str) -> bool:
        return value not in resource._mutable_fields().union(resource._secret_fields())

    overrides = {
        **(overrides if overrides is not None else {}),
        "name": resource.display_name,
        "id": resource._must_id(),
    }

    skip_fields = {
        *(skip_fields if skip_fields is not None else set()),
        "resourceName",
    }

    return _api_input(
        resource,
        overrides,
        skip_fields,
        root_key_name,
        skip_fn,
    )


@dataclass
class ImportValue:
    value: Any
    comment: str | None = None


def _import_resource_params(
    resource: "Diffable",
    skip_fields: set[str] | None = None,
) -> dict[str, ImportValue]:
    from validio_sdk.resource._resource import DiffContext

    secret_fields = {
        field: ImportValue(value="UNSET", comment="FIXME: Add secret value")
        for field in resource._secret_fields()
    }
    skip_fields = skip_fields or set({})
    parent_resource_name_fields = {
        f"{f[: len(f) - 1]}_name" for f in DiffContext.fields()
    }
    skip_fields = {*skip_fields, *parent_resource_name_fields}

    fields = {
        field: ImportValue(getattr(resource, field))
        for field in resource._all_fields()
        if field not in skip_fields and field not in secret_fields
    }

    return {
        **fields,
        **secret_fields,
    }


def _import_value_repr(
    value: Any,
    indent_level: int,
    import_ctx: "ImportContext",
) -> str:
    from validio_sdk.resource._diffable import Diffable

    if isinstance(value, Diffable):
        value_repr = value._import_str(indent_level=indent_level, import_ctx=import_ctx)
    elif isinstance(value, Enum):
        value_repr = value.__str__()
    elif isinstance(value, list):
        # This code will basically just change how more complex types that
        # something simple than a list of strings is represented. Where this
        # works fine for strings:
        #
        # Obj(
        #     some_key=['foo','bar','baz'],
        # )
        #
        # It doesn't really look well when we do this for `Diffable` objects. It
        # would by default end up like this.
        #
        # Obj(
        #     complex=[AnotherObj(
        #         foo="bar",
        #     ),AnotherObj(
        #         foo="baz",
        #     )],
        # )
        #
        # This code will change that to look like this. That's all it does!
        #
        # Obj(
        #     complex=[
        #         AnotherObj(
        #             foo="bar",
        #         ),
        #         AnotherObj(
        #             foo="baz",
        #         ),
        #    ],
        # )
        if len(value) > 0 and isinstance(value[0], Diffable):
            base_indent = " " * Diffable._num_ident_spaces(indent_level)
            next_indent = " " * Diffable._num_ident_spaces(indent_level + 1)
            values = f",\n{next_indent}".join(
                [v._import_str(indent_level + 1, import_ctx) for v in value]
            )

            value_repr = f"[\n{next_indent}{values},\n{base_indent}]"
        else:
            values = ",".join(
                [_import_value_repr(v, indent_level, import_ctx) for v in value]
            )

            value_repr = f"[{values}]"
    elif isinstance(value, str):
        # If the value is a string we try to use convenient representation in
        # triple single or double quotes where possible. Initially we try to use
        # triple single quotes since `repr()` will result in single quotes. If
        # the multi line string contains `'''` we try `"""`. If the string
        # contains that sequence as well we'll fall back to `repr()`.
        #
        # This is used to preserve the syntax used by the user, primarily for
        # longer more complex SQL validators that we don't want to import on a
        # single long line.
        if "\n" not in value:
            value_repr = repr(value)
        elif "'''" not in value:
            value_repr = f"'''{value}'''"
        elif '"""' not in value:
            value_repr = f'"""{value}"""'
        else:
            value_repr = repr(value)
    else:
        value_repr = repr(value)

    return value_repr
