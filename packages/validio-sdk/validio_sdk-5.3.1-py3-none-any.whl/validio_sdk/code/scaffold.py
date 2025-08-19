"""Init command implementation."""

import json
import os
import pathlib
from dataclasses import dataclass

from validio_sdk.exception import ValidioError

settings_file_name: str = "validio.json"
main_file_name: str = "main.py"


@dataclass
class ProjectSettings:
    """Represents the settings for a project."""

    namespace: str


def _new_project(namespace: str, directory: pathlib.Path, force: bool) -> None:
    _ensure_directory(directory, force)
    _ensure_project_settings_file(directory, namespace)
    _gen_main_py_file(directory)


def _ensure_directory(p: pathlib.Path, force: bool) -> None:
    if not p.exists():
        pathlib.Path.mkdir(p)

    if not p.is_dir():
        raise ValidioError(f"{p} is not a directory; rerun specifying a directory")

    if not force and len(os.listdir(p)):
        raise ValidioError(
            f"{p} is not empty; rerun in an empty directory, or use --force"
        )


def _ensure_project_settings_file(p: pathlib.Path, namespace: str) -> None:
    with pathlib.Path.open(_project_settings_file_path(p), "w") as f:
        print(
            json.dumps(ProjectSettings(namespace=namespace).__dict__, indent=2), file=f
        )


def _read_project_settings(p: pathlib.Path) -> ProjectSettings:
    with pathlib.Path.open(_project_settings_file_path(p)) as f:
        return ProjectSettings(**json.load(f))


def _project_settings_file_path(p: pathlib.Path) -> pathlib.Path:
    return p / settings_file_name


def _gen_main_py_file(p: pathlib.Path) -> None:
    with pathlib.Path.open(p / main_file_name, "w") as f:
        print("from validio_sdk.resource import credentials", file=f)
