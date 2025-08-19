import asyncio

from validio_sdk.code._import import _import
from validio_sdk.resource._resource import DiffContext
from validio_sdk.resource.channels import WebhookChannel
from validio_sdk.resource.credentials import DemoCredential, PostgreSqlCredential
from validio_sdk.resource.notification_rules import (
    Conditions,
    NotificationRule,
    SegmentCondition,
    SegmentNotificationRuleCondition,
    SourceNotificationRuleCondition,
    TagNotificationRuleCondition,
)
from validio_sdk.resource.segmentations import Segmentation, SegmentUsage
from validio_sdk.resource.sources import DemoSource, PostgreSqlSource, SqlSource
from validio_sdk.resource.tags import Tag
from validio_sdk.resource.validators import SqlValidator
from validio_sdk.resource.windows import (
    Duration,
    DurationTimeUnit,
    TumblingWindow,
    WindowTimeUnit,
)


# We mostly test import of all resource types in the IaC e2e tests but this is
# here to speed up implementations of changes to import such as new resource
# types and makes TDD faster and easier.
# This test is not meant to be exhaustive.
def test_import_resources() -> None:
    t0 = Tag(key="t0", value="v0")
    t1 = Tag(key="t1", value="v1")
    t2 = Tag(key="t2", value="v2")

    c = DemoCredential(name="my-credential")

    s1 = DemoSource(name="my-source", credential=c, tags=[t0, t1])
    s2 = DemoSource(name="my-source-2", credential=c, tags=[t2])

    ch = WebhookChannel(
        name="my-channel",
        application_link_url="https://link.url",
        webhook_url="https://webhook.url",
        auth_header=None,
    )

    nr = NotificationRule(
        name="my-nr",
        channel=ch,
        conditions=Conditions(
            segment_conditions=[
                SegmentNotificationRuleCondition(
                    segments=[SegmentCondition(field="foo", value="bar")],
                ),
                SegmentNotificationRuleCondition(
                    segments=[SegmentCondition(field="bar", value="baz")],
                ),
            ],
            source_condition=SourceNotificationRuleCondition(sources=[s1, s2]),
            tag_conditions=[
                TagNotificationRuleCondition(
                    tags=[t1, t2],
                ),
            ],
        ),
    )

    ctx = DiffContext(
        credentials={c.name: c},
        sources={s1.name: s1},
        channels={ch.name: ch},
        notification_rules={nr.name: nr},
    )

    tags_ctx = DiffContext(
        tags={
            t0.name: t0,
            t1.name: t1,
            t2.name: t2,
        },
    )

    expected = """
from validio_sdk import *
from validio_sdk.resource.thresholds import *
from validio_sdk.resource.channels import *
from validio_sdk.resource.credentials import *
from validio_sdk.resource.filters import *
from validio_sdk.resource.notification_rules import *
from validio_sdk.resource.segmentations import *
from validio_sdk.resource.sources import *
from validio_sdk.resource.tags import *
from validio_sdk.resource.validators import *
from validio_sdk.resource.windows import *


source_1 = 'my-source-2'  # FIXME: manually change to actual resource reference


tag_0 = Tag(
    key='t0',
    value='v0',
)
tag_1 = Tag(
    key='t1',
    value='v1',
)
tag_2 = Tag(
    key='t2',
    value='v2',
)
credential_0 = DemoCredential(
    name='my-credential',
    ignore_changes=True,
    display_name='my-credential',
)
channel_0 = WebhookChannel(
    name='my-channel',
    ignore_changes=True,
    application_link_url='https://link.url',
    auth_header='UNSET', # FIXME: Add secret value
    display_name='my-channel',
    webhook_url='UNSET', # FIXME: Add secret value
)
source_0 = DemoSource(
    name='my-source',
    credential=credential_0,
    description=None,
    display_name='my-source',
    tags=[tag_0, tag_1],
)
notificationrule_0 = NotificationRule(
    name='my-nr',
    channel=channel_0,
    conditions=Conditions(
        owner_condition=None,
        segment_conditions=[
            SegmentNotificationRuleCondition(
                segments=[SegmentCondition(field='bar', value='baz')],
            ),
            SegmentNotificationRuleCondition(
                segments=[SegmentCondition(field='foo', value='bar')],
            ),
        ],
        severity_condition=None,
        source_condition=SourceNotificationRuleCondition(
            sources=[source_0, source_1],
        ),
        tag_conditions=[
            TagNotificationRuleCondition(
                tags=[tag_1, tag_2],
            ),
        ],
        type_condition=None,
    ),
    display_name='my-nr',
)
"""
    doc = asyncio.run(_import(ctx, tags_ctx))

    assert doc.strip() == expected.strip()


def test_import_sql_source() -> None:
    credential = PostgreSqlCredential(
        name="postgres",
        host="127.0.0.1",
        port=5431,
        user="user",
        password="password",
        default_database="postgres",
    )

    source = SqlSource(
        name="sql-source-postgres",
        credential=credential,
        schedule="* * * * *",
        sql_query="""
            select 1 as value
            union all
            select 2 as value
        """,
        jtd_schema={
            "nullable": False,
            "optionalProperties": {},
            "properties": {
                "value": {"type": "int32"},
            },
        },
    )

    expected = """
from validio_sdk import *
from validio_sdk.resource.thresholds import *
from validio_sdk.resource.channels import *
from validio_sdk.resource.credentials import *
from validio_sdk.resource.filters import *
from validio_sdk.resource.notification_rules import *
from validio_sdk.resource.segmentations import *
from validio_sdk.resource.sources import *
from validio_sdk.resource.tags import *
from validio_sdk.resource.validators import *
from validio_sdk.resource.windows import *


credential_0 = PostgreSqlCredential(
    name='postgres',
    ignore_changes=True,
    default_database='postgres',
    display_name='postgres',
    enable_catalog=False,
    host='127.0.0.1',
    password='UNSET', # FIXME: Add secret value
    port=5431,
    user='user',
)
source_0 = SqlSource(
    name='sql-source-postgres',
    credential=credential_0,
    description=None,
    display_name='sql-source-postgres',
    schedule='* * * * *',
    sql_query='''
            select 1 as value
            union all
            select 2 as value
        ''',
    tags=[],
)
"""
    ctx = DiffContext(
        credentials={credential.name: credential},
        sources={source.name: source},
    )

    doc = asyncio.run(_import(ctx, DiffContext()))

    assert doc.strip() == expected.strip()


def test_import_multiline_string_parameters_resources() -> None:
    credential = PostgreSqlCredential(
        name="pg_cred",
        host="validio.io",
        port=1337,
        user="root",
        password="sudo-su",
        default_database="database",
    )

    source = PostgreSqlSource(
        name="pg_source",
        credential=credential,
        database="database",
        schema="schema",
        table="table",
        schedule=None,
    )

    window = TumblingWindow(
        name="window",
        source=source,
        data_time_field="created_at",
        window_size=1,
        time_unit=WindowTimeUnit.DAY,
        lookback=Duration(
            length=42,
            unit=DurationTimeUnit.DAY,
        ),
    )

    segmentation = Segmentation(
        name="segmentation",
        source=source,
        fields=[],
        segment_usage=SegmentUsage.MINIMAL,
    )

    # This validator doesn't contain any newlines so we will use `repr()` and
    # get a single line: 'SELECT 1'
    validator_0 = SqlValidator(
        name="sql_validator_0",
        segmentation=segmentation,
        window=window,
        query="""SELECT 1""",
    )

    # This validator contains multiple lines but not ''' so we'll use triple
    # quote multi line syntax `'''`
    validator_1 = SqlValidator(
        name="sql_validator_1",
        segmentation=segmentation,
        window=window,
        query="""SELECT
COUNT(*) AS "validio_metric",
    {{ validio_window_id("created_at") }} AS "validio_window_id"
FROM
    "public"."a"
WHERE
    {{ validio_window_filter("created_at") }}
GROUP BY
    {{ validio_window_id("created_at") }}""",
    )

    # This validator contains multiple lines and also a triple single quote
    # section so we'll use triple quote multi line syntax `"""`
    validator_2 = SqlValidator(
        name="sql_validator_2",
        segmentation=segmentation,
        window=window,
        query="""SELECT
COUNT(*) AS '''validio_metric''',
    {{ validio_window_id("created_at") }} AS "validio_window_id"
FROM
    "public"."a"
WHERE
    {{ validio_window_filter("created_at") }}
GROUP BY
    {{ validio_window_id("created_at") }}""",
    )

    # This validator contains multiple lines and both triple single quote and
    # triple double quotes section. This means we can't use `'''` or `"""` as is
    # without ending up with something nasty like below. We fallback to `repr()`
    # and print the actual escape characters like raw `\n`
    validator_3 = SqlValidator(
        name="sql_validator_3",
        segmentation=segmentation,
        window=window,
        query=(
            """SELECT
    COUNT(*) AS '''validio_metric''',
"""
            '    {{ validio_window_id("created_at") }} AS """validio_window_id"""'
            """
FROM
    "public"."a"
WHERE
    {{ validio_window_filter("created_at") }}
GROUP BY
    {{ validio_window_id("created_at") }}"""
        ),
    )

    ctx = DiffContext(
        credentials={credential.name: credential},
        sources={source.name: source},
        windows={window.name: window},
        segmentations={segmentation.name: segmentation},
        validators={
            validator_0.name: validator_0,
            validator_1.name: validator_1,
            validator_2.name: validator_2,
            validator_3.name: validator_3,
        },
    )

    # ruff: noqa: E501: Allow long lines for the test to match exactly
    expected = """
from validio_sdk import *
from validio_sdk.resource.thresholds import *
from validio_sdk.resource.channels import *
from validio_sdk.resource.credentials import *
from validio_sdk.resource.filters import *
from validio_sdk.resource.notification_rules import *
from validio_sdk.resource.segmentations import *
from validio_sdk.resource.sources import *
from validio_sdk.resource.tags import *
from validio_sdk.resource.validators import *
from validio_sdk.resource.windows import *


credential_0 = PostgreSqlCredential(
    name='pg_cred',
    ignore_changes=True,
    default_database='database',
    display_name='pg_cred',
    enable_catalog=False,
    host='validio.io',
    password='UNSET', # FIXME: Add secret value
    port=1337,
    user='root',
)
source_0 = PostgreSqlSource(
    name='pg_source',
    credential=credential_0,
    cursor_field=None,
    database='database',
    description=None,
    display_name='pg_source',
    lookback_days=None,
    schedule=None,
    schema='schema',
    table='table',
    tags=[],
)
window_0 = TumblingWindow(
    name='window',
    source=source_0,
    data_time_field='created_at',
    display_name='window',
    lookback=Duration(
        length=42,
        unit=DurationTimeUnit.DAY,
    ),
    partition_filter=None,
    segment_retention_period_days=None,
    time_unit=WindowTimeUnit.DAY,
    window_size=1,
    window_timeout_disabled=False,
)
segmentation_0 = Segmentation(
    name='segmentation',
    source=source_0,
    display_name='segmentation',
    fields=[],
    segment_usage=SegmentUsage.MINIMAL,
)
validator_0 = SqlValidator(
    name='sql_validator_0',
    segmentation=segmentation_0,
    window=window_0,
    description=None,
    display_name='sql_validator_0',
    initialize_with_backfill=False,
    query='SELECT 1',
    tags=[],
    threshold=DynamicThreshold(
        adaption_rate=AdaptionRate.FAST,
        algorithm=DynamicThresholdAlgorithm.V1,
        decision_bounds_type=DecisionBoundsType.UPPER_AND_LOWER,
        sensitivity=3.0,
    ),
)
validator_1 = SqlValidator(
    name='sql_validator_1',
    segmentation=segmentation_0,
    window=window_0,
    description=None,
    display_name='sql_validator_1',
    initialize_with_backfill=False,
    query='''SELECT
COUNT(*) AS "validio_metric",
    {{ validio_window_id("created_at") }} AS "validio_window_id"
FROM
    "public"."a"
WHERE
    {{ validio_window_filter("created_at") }}
GROUP BY
    {{ validio_window_id("created_at") }}''',
    tags=[],
    threshold=DynamicThreshold(
        adaption_rate=AdaptionRate.FAST,
        algorithm=DynamicThresholdAlgorithm.V1,
        decision_bounds_type=DecisionBoundsType.UPPER_AND_LOWER,
        sensitivity=3.0,
    ),
)
validator_2 = SqlValidator(
    name='sql_validator_2',
    segmentation=segmentation_0,
    window=window_0,
    description=None,
    display_name='sql_validator_2',
    initialize_with_backfill=False,
    query=\"""SELECT
COUNT(*) AS '''validio_metric''',
    {{ validio_window_id("created_at") }} AS "validio_window_id"
FROM
    "public"."a"
WHERE
    {{ validio_window_filter("created_at") }}
GROUP BY
    {{ validio_window_id("created_at") }}\""",
    tags=[],
    threshold=DynamicThreshold(
        adaption_rate=AdaptionRate.FAST,
        algorithm=DynamicThresholdAlgorithm.V1,
        decision_bounds_type=DecisionBoundsType.UPPER_AND_LOWER,
        sensitivity=3.0,
    ),
)
validator_3 = SqlValidator(
    name='sql_validator_3',
    segmentation=segmentation_0,
    window=window_0,
    description=None,
    display_name='sql_validator_3',
    initialize_with_backfill=False,
    query='SELECT\\n    COUNT(*) AS \\'\\'\\'validio_metric\\'\\'\\',\\n    {{ validio_window_id("created_at") }} AS \"""validio_window_id\"""\\nFROM\\n    "public"."a"\\nWHERE\\n    {{ validio_window_filter("created_at") }}\\nGROUP BY\\n    {{ validio_window_id("created_at") }}',
    tags=[],
    threshold=DynamicThreshold(
        adaption_rate=AdaptionRate.FAST,
        algorithm=DynamicThresholdAlgorithm.V1,
        decision_bounds_type=DecisionBoundsType.UPPER_AND_LOWER,
        sensitivity=3.0,
    ),
)
"""
    doc = asyncio.run(_import(ctx, DiffContext()))

    assert doc.strip() == expected.strip()
