"""Utilities for dbt."""

import json
import math
from typing import Optional

from validio_sdk._api.api import (
    APIClient,
    dbt_artifact_multipart_upload_append_part,
    dbt_artifact_multipart_upload_complete,
    dbt_artifact_multipart_upload_create,
)
from validio_sdk.client.client import Client

_DBT_MULTIPART_UPLOAD_CHUNK_SIZE_BYTES = 2 * 1000 * 1000  # 2MB


def trim_manifest_json(manifest: dict) -> dict:
    """
    Takes a dbt manifest json and discards all the fields that are not relevant
    used by the validio platform.

    :param manifest: The manifest object
    """
    nodes, relevant_sources = _extract_models_and_tests(manifest)
    sources = _extract_sources(manifest, relevant_sources)
    return {
        "metadata": _extract_metadata(manifest),
        "nodes": nodes,
        "sources": sources,
    }


def _extract_metadata(manifest: dict) -> dict:
    if "metadata" not in manifest:
        return {}

    m = manifest["metadata"]
    trimmed = {}
    for f in [
        "dbt_schema_version",
        "dbt_version",
        "generated_at",
        "invocation_id",
        "project_name",
        "project_id",
        "user_id",
        "adapter_type",
    ]:
        if f in m:
            trimmed[f] = m[f]
    return trimmed


def _trim_model_column(column: dict) -> dict:
    trimmed = {}
    for f in ["name", "description"]:
        if f in column:
            trimmed[f] = column[f]
    return trimmed


def _extract_models_and_tests(manifest: dict) -> tuple[dict, set]:
    if "nodes" not in manifest:
        return {}, set({})

    relevant_sources = set({})
    models = {}
    for k, m in manifest["nodes"].items():
        if m["resource_type"] != "model" and m["resource_type"] != "test":
            continue
        if m["language"] != "sql":
            continue

        verbatim_fields = [
            "package_name",
            "database",
            "schema",
            "name",
            "description",
            "created_at",
            "relation_name",
            "compiled_code",
            "resource_type",
            "depends_on",
            "original_file_path",
            "unique_id",
            "config",
            "tags",
            "raw_code",
            "config",
            "column_name",
            "attached_node",
            "test_metadata",
        ]
        trimmed = {}
        for f in verbatim_fields:
            if f in m and not (isinstance("str", type(m[f])) and not m[f]):
                trimmed[f] = m[f]

        if "columns" in m:
            trimmed_columns = _get_trimmed_columns(m)
            if len(trimmed_columns) > 0:
                trimmed["columns"] = trimmed_columns

        if (
            "depends_on" in m
            and "nodes" in m["depends_on"]
            and len(m["depends_on"]["nodes"]) > 0
        ):
            depends_on_nodes = m["depends_on"]["nodes"]
            for node_id in depends_on_nodes:
                if node_id.startswith("source"):
                    relevant_sources.add(node_id)

            trimmed["depends_on"] = {"nodes": depends_on_nodes}

        models[k] = trimmed

    return models, relevant_sources


def _get_trimmed_columns(manifest: dict) -> dict:
    trimmed_columns = {}
    for column_name, column_obj in manifest["columns"].items():
        trimmed_column = _trim_model_column(column_obj)
        if len(trimmed_column) > 0:
            trimmed_columns[column_name] = trimmed_column
    return trimmed_columns


def _extract_sources(manifest: dict, relevant_sources: set) -> dict:
    if "sources" not in manifest:
        return {}

    sources = {}
    for k, s in manifest["sources"].items():
        if k not in relevant_sources:
            continue

        fields = [
            "database",
            "schema",
            "name",
            "description",
            "created_at",
            "relation_name",
            "resource_type",
            "original_file_path",
            "package_name",
            "unique_id",
            "tags",
        ]
        trimmed = {}
        for f in fields:
            if f in s:
                if isinstance("str", type(s[f])) and not s[f]:
                    continue
                trimmed[f] = s[f]

        if len(trimmed) > 0:
            sources[k] = trimmed

    return sources


async def upload_artifacts(
    client: APIClient | Client,
    credential_id: str,
    job_name: str,
    manifest: dict,
    run_results: Optional[dict],
) -> None:
    """
    Helper function to upload dbt artifacts.
    The artifacts are additionally trimmed before uploading.

    :param client: Client to use for the artifacts upload.
    :param credential_id: DBTCore credential id to upload artifacts on behalf of.
    :param job_name:  Job associated with the artifacts.
    :param manifest: manifest.json payload
    :param run_results: run_results.json payload
    """
    client = client if isinstance(client, Client) else client.client

    async with client as session:
        upload_id = await dbt_artifact_multipart_upload_create(
            session,
            credential_id=credential_id,
            job_name=job_name,
        )

        payload = _generate_artifact_upload_payload(manifest, run_results)

        chunk_size = _DBT_MULTIPART_UPLOAD_CHUNK_SIZE_BYTES
        num_chunks = math.ceil(len(payload) / chunk_size)
        for i in range(num_chunks):
            part = (
                payload[i * chunk_size :]
                if i == num_chunks - 1
                else payload[i * chunk_size : (i + 1) * chunk_size]
            )
            await dbt_artifact_multipart_upload_append_part(
                session,
                upload_id=upload_id,
                part=part,
            )

        await dbt_artifact_multipart_upload_complete(session, upload_id=upload_id)


def _generate_artifact_upload_payload(
    manifest: dict, run_results: Optional[dict]
) -> str:
    return json.dumps(
        {
            "manifest": trim_manifest_json(manifest),
            "run_result": run_results,
        }
    )
