from pathlib import Path

import deepdiff

from validio_sdk import dbt, util


def test_trim_dbt_manifest_json() -> None:
    manifest = util.read_json_file(
        Path(Path(__file__).parent, "assets", "example_manifest.json")
    )

    assert isinstance(manifest, dict)

    trimmed_manifest = dbt.trim_manifest_json(manifest)

    expected_trimmed_manifest = util.read_json_file(
        Path(Path(__file__).parent, "assets", "expected_trimmed_manifest.json")
    )

    assert not deepdiff.DeepDiff(trimmed_manifest, expected_trimmed_manifest).pretty()
