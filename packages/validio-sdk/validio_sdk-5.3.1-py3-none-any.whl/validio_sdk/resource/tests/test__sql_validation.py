import asyncio
from typing import Any, cast
from unittest import mock
from unittest.mock import AsyncMock, Mock

from validio_sdk.resource import (
    credentials,
    filters,
    segmentations,
    sources,
    validators,
    windows,
)
from validio_sdk.resource._diff import DiffContext
from validio_sdk.resource._server_resources import _maybe_validate_queries


@mock.patch("validio_sdk._api.api.validate_sql_validator_query")
def test__should_invoke_sql_validation_request(
    mocked_fn: AsyncMock,
) -> None:
    c1 = credentials.PostgreSqlCredential(
        name="c1",
        host="host",
        port=1234,
        user="user",
        password="password",
        default_database="db",
    )
    c1._id.value = "c1"
    s1 = sources.PostgreSqlSource(
        name="s1",
        credential=c1,
        database="db",
        schema="schema",
        table="table",
        lookback_days=41,
        schedule=None,
    )
    s1._id.value = "s1"
    w1 = windows.GlobalWindow(name="w1", source=s1)
    w1._id.value = "w1"
    seg1 = segmentations.Segmentation(name="seg1", source=s1, fields=[])
    seg1._id.value = "seg1"
    query = "SELECT * FROM my_table"
    v1 = validators.SqlValidator(
        name="v1",
        window=cast(Any, w1),
        segmentation=seg1,
        query=query,
    )
    ctx = DiffContext(
        credentials={"c1": c1},
        channels={},
        sources={"s1": s1},
        windows={"w1": w1},
        filters={},
        segmentations={"seg1": seg1},
        validators={"v1": v1},
        notification_rules={},
    )
    session_mock = Mock()
    asyncio.run(_maybe_validate_queries([v1], ctx, session_mock, True))
    mocked_fn.assert_called_with(session_mock, query, "v1", "s1", "seg1", "w1")


@mock.patch("validio_sdk._api.api.validate_sql_validator_query")
def test__should_skip_invoking_sql_validation_request_for_azure(
    mocked_fn: AsyncMock,
) -> None:
    c2 = credentials.AzureSynapseEntraIdCredential(
        name="c2",
        host="host",
        port=1234,
        backend_type=credentials.AzureSynapseBackendType.SERVERLESS_SQL_POOL,
        client_id="client_id",
        client_secret="client_secret",
    )
    c2._id.value = "c2"
    s2 = sources.AzureSynapseSource(
        name="s2",
        credential=c2,
        database="db",
        schema="schema",
        table="table",
        lookback_days=42,
        schedule=None,
    )
    s2._id.value = "s2"
    w2 = windows.GlobalWindow(name="w2", source=s2)
    w2._id.value = "w2"
    seg2 = segmentations.Segmentation(name="seg2", source=s2, fields=[])
    seg2._id.value = "seg2"
    v2 = validators.SqlValidator(
        name="v2",
        window=cast(Any, w2),
        segmentation=seg2,
        query="SELECT * FROM my_table",
    )
    ctx = DiffContext(
        credentials={"c2": c2},
        channels={},
        sources={"s2": s2},
        windows={"w2": w2},
        filters={},
        segmentations={"seg2": seg2},
        validators={"v2": v2},
        notification_rules={},
    )
    session_mock = Mock()
    asyncio.run(_maybe_validate_queries([v2], ctx, session_mock, True))
    mocked_fn.assert_not_called()


@mock.patch("validio_sdk._api.api.validate_sql_filter_query")
def test__should_invoke_filter_sql_validation_request(
    mocked_fn: AsyncMock,
) -> None:
    c3 = credentials.PostgreSqlCredential(
        name="c3",
        host="host",
        port=1234,
        user="user",
        password="password",
        default_database="db",
    )
    c3._id.value = "c3"
    s3 = sources.PostgreSqlSource(
        name="s3",
        credential=c3,
        database="db",
        table="table",
        lookback_days=41,
        schema="schema",
        schedule=None,
    )
    s3._id.value = "s3"
    query = "id = '123'"
    f1 = filters.SqlFilter(name="f1", query=query, source=s3)
    ctx = DiffContext(
        credentials={"c3": c3},
        channels={},
        sources={"s3": s3},
        windows={},
        filters={"f1": f1},
        segmentations={},
        validators={},
        notification_rules={},
    )
    session_mock = Mock()
    asyncio.run(_maybe_validate_queries([f1], ctx, session_mock, True))
    mocked_fn.assert_called_with(session_mock, query, "f1", "s3")


@mock.patch("validio_sdk._api.api.validate_sql_filter_query")
def test__should_skip_invoking_filter_sql_validation_request_for_azure(
    mocked_fn: AsyncMock,
) -> None:
    c4 = credentials.AzureSynapseEntraIdCredential(
        name="c4",
        host="host",
        port=1234,
        backend_type=credentials.AzureSynapseBackendType.SERVERLESS_SQL_POOL,
        client_id="client_id",
        client_secret="client_secret",
    )
    c4._id.value = "c4"
    s4 = sources.AzureSynapseSource(
        name="s4",
        credential=c4,
        database="db",
        schema="schema",
        table="table",
        lookback_days=42,
        schedule=None,
    )
    s4._id.value = "s4"
    f2 = filters.SqlFilter(name="f2", query="SELECT * FROM my_table", source=s4)
    ctx = DiffContext(
        credentials={"c4": c4},
        channels={},
        sources={"s4": s4},
        windows={},
        filters={"f2": f2},
        segmentations={},
        validators={},
        notification_rules={},
    )
    session_mock = Mock()
    asyncio.run(_maybe_validate_queries([f2], ctx, session_mock, True))
    mocked_fn.assert_not_called()
