"""Utilities for Validio."""

import dataclasses
import json
import pathlib
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Union

from validio_sdk.exception import ValidioError
from validio_sdk.resource._errors import ManifestConfigurationError
from validio_sdk.scalars import JsonTypeDefinition

JsonType = Union[dict[str, "JsonType"], list["JsonType"], str, int, float, bool, None]


def load_jtd_schema(filepath: pathlib.Path) -> JsonTypeDefinition:
    """
    Reads a jtd schema from a file on disk.

    :param filepath: Path to the file containing the schema contents.
    """
    with pathlib.Path.open(filepath) as f:
        jtd_schema = json.load(f)
        if jtd_schema == {}:
            raise ManifestConfigurationError(
                f"invalid jtd_schema in file {filepath.absolute()}: "
                "schema cannot be empty"
            )

        # TODO: https://linear.app/validio/issue/VR-2073 Fix licence issue with jtd lib
        # try:
        #     jtd.Schema.from_dict(jtd_schema).validate()
        # except Exception as e:
        #     raise ManifestConfigurationError(
        #         f"invalid jtd_schema in file {filepath.absolute()}: {e}"
        #     )

        return jtd_schema


class ClassJSONEncoder(json.JSONEncoder):
    """Encoder for classes."""

    # ruff: noqa: PLR0911
    def default(self, o: Any) -> JsonType:
        """
        Default encoder implementation.

        :param o: The dataclass object

        :returns: JSON encoded data
        """
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)  # type: ignore[arg-type]

        if isinstance(o, Enum):
            return o.value

        if isinstance(o, datetime | date):
            return o.isoformat()

        if hasattr(o, "asdict"):
            return o.asdict()

        if hasattr(o, "__dict__"):
            return o.__dict__

        try:
            return super().default(o)
        except TypeError:
            return str(o)


def read_json_file(filepath: Path) -> JsonType:
    """
    Reads a JSON file and returns a JSON object.

    :param filepath: Path to the JSON file.
    """
    try:
        return json.loads(filepath.read_text())
    except FileNotFoundError:
        raise ValidioError(f"file '{filepath}' not found")
    except json.JSONDecodeError:
        raise ValidioError(f"file '{filepath}' does not contain valid JSON")
