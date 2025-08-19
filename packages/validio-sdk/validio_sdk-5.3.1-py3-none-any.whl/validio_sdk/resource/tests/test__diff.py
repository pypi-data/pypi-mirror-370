import pytest

from validio_sdk.resource._diff import (
    CascadeReplacementReason,
    DiffContext,
    GraphDiff,
    ReplacementContext,
    ResourceUpdate,
    ResourceUpdates,
    _compute_replacements,
    _diff_resource_graph,
)
from validio_sdk.resource._resource import ResourceGraph
from validio_sdk.resource.channels import Channel, SlackChannel, WebhookChannel
from validio_sdk.resource.credentials import AwsCredential, Credential, DemoCredential
from validio_sdk.resource.filters import (
    EnumFilter,
    Filter,
    NullFilter,
    NullFilterOperator,
)
from validio_sdk.resource.notification_rules import (
    Conditions,
    NotificationRule,
    SourceNotificationRuleCondition,
    TagNotificationRuleCondition,
)
from validio_sdk.resource.replacement import ImmutableFieldReplacementReason
from validio_sdk.resource.segmentations import Segmentation
from validio_sdk.resource.sources import DemoSource, Source
from validio_sdk.resource.thresholds import (
    ComparisonOperator,
    DynamicThreshold,
    FixedThreshold,
)
from validio_sdk.resource.validators import (
    NumericDistributionMetric,
    NumericDistributionValidator,
    NumericMetric,
    NumericValidator,
    Reference,
    Validator,
)
from validio_sdk.resource.windows import (
    FixedBatchWindow,
    TumblingWindow,
    Window,
    WindowTimeUnit,
)


def _add_namespace(namespace: str, ctx: DiffContext) -> None:
    for f in DiffContext.fields():
        for r in getattr(ctx, f).values():
            r._namespace = namespace


def create_diff_context(
    credentials: dict[str, Credential] | None = None,
    channels: dict[str, Channel] | None = None,
    sources: dict[str, Source] | None = None,
    windows: dict[str, Window] | None = None,
    filters: dict[str, Filter] | None = None,
    segmentations: dict[str, Segmentation] | None = None,
    validators: dict[str, Validator] | None = None,
    notification_rules: dict[str, NotificationRule] | None = None,
) -> DiffContext:
    return DiffContext(
        credentials=credentials or {},
        channels=channels or {},
        sources=sources or {},
        windows=windows or {},
        filters=filters or {},
        segmentations=segmentations or {},
        validators=validators or {},
        notification_rules=notification_rules or {},
    )


def create_resource_updates(
    credentials: dict[str, ResourceUpdate] | None = None,
    channels: dict[str, ResourceUpdate] | None = None,
    sources: dict[str, ResourceUpdate] | None = None,
    windows: dict[str, ResourceUpdate] | None = None,
    filters: dict[str, ResourceUpdate] | None = None,
    segmentations: dict[str, ResourceUpdate] | None = None,
    validators: dict[str, ResourceUpdate] | None = None,
    notification_rules: dict[str, ResourceUpdate] | None = None,
) -> ResourceUpdates:
    return ResourceUpdates(
        credentials=credentials or {},
        channels=channels or {},
        sources=sources or {},
        windows=windows or {},
        filters=filters or {},
        segmentations=segmentations or {},
        validators=validators or {},
        notification_rules=notification_rules or {},
    )


def create_graph_diff(
    to_create: DiffContext | None = None,
    to_delete: DiffContext | None = None,
    to_update: ResourceUpdates | None = None,
    replacement_ctx: ReplacementContext | None = None,
) -> GraphDiff:
    return GraphDiff(
        to_create=to_create or DiffContext(),
        to_delete=to_delete or DiffContext(),
        to_update=to_update or create_resource_updates(),
        replacement_ctx=replacement_ctx or ReplacementContext(),
    )


# ruff: noqa: PLR0915
def test_diff_should_detect_create_update_delete_operations_on_resources() -> None:
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential(name="c1", __internal__=manifest_g)
    manifest_s1 = DemoSource(name="s1", credential=manifest_c1)
    manifest_s2 = DemoSource(name="s2", credential=manifest_c1)  # To be created
    manifest_w1 = FixedBatchWindow(
        name="w1", source=manifest_s1, data_time_field="d", batch_size=10
    )
    manifest_w2 = FixedBatchWindow(
        name="w2", source=manifest_s1, data_time_field="d", batch_size=20
    )  # To be created
    manifest_w3 = FixedBatchWindow(
        name="w3", source=manifest_s1, data_time_field="d", batch_size=30
    )  # Update
    manifest_f1 = NullFilter(
        name="f1",
        source=manifest_s1,
        field="age",
    )  # No diff
    manifest_f2 = NullFilter(
        name="f2",
        source=manifest_s1,
        field="age",
    )  # To be created
    manifest_f3 = NullFilter(
        name="f3",
        source=manifest_s1,
        field="age",
    )  # To be updated
    manifest_seg1 = Segmentation(
        name="seg1",
        source=manifest_s1,
        fields=["city"],
        filter=manifest_f1,
    )
    manifest_seg2 = Segmentation(
        name="seg2",
        source=manifest_s1,
        fields=["gender"],
        filter=manifest_f1,
    )  # To be created
    manifest_v1 = NumericValidator(
        name="v1",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MAX,
        source_field="a",
        filter=manifest_f1,
    )
    manifest_v2 = NumericValidator(
        name="v2",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MEAN,
        source_field="b",
        filter=manifest_f1,
    )  # To be created
    manifest_ch1 = SlackChannel(
        name="ch1",
        application_link_url="app",
        slack_channel_id="sid",
        token="token",
        app_token="secret",
        __internal__=manifest_g,
    )
    manifest_ch2 = SlackChannel(
        name="ch2",
        application_link_url="app",
        slack_channel_id="sid",
        token="token",
        app_token="secret",
        __internal__=manifest_g,
    )  # To be created
    manifest_ch3 = SlackChannel(
        name="ch3",
        application_link_url="app",
        slack_channel_id="sid",
        token="token",
        app_token="secret",
        __internal__=manifest_g,
    )  # To be updated
    manifest_cond1 = Conditions(
        source_condition=SourceNotificationRuleCondition(sources=[manifest_s1])
    )
    manifest_r1 = NotificationRule(
        name="r1", channel=manifest_ch1, conditions=manifest_cond1
    )
    manifest_r2 = NotificationRule(
        name="r2", channel=manifest_ch1, conditions=manifest_cond1
    )  # To be created
    manifest_r3 = NotificationRule(
        name="r3", channel=manifest_ch1, conditions=manifest_cond1
    )  # To be updated

    server_c1 = DemoCredential(name="c1", __internal__=server_g)
    server_s1 = DemoSource(name="s1", credential=server_c1)
    server_s3 = DemoSource(name="s3", credential=server_c1)  # To be deleted
    server_w1 = FixedBatchWindow(
        name="w1", source=server_s1, data_time_field="d", batch_size=10
    )
    server_w3 = FixedBatchWindow(
        name="w3", source=server_s1, data_time_field="d", batch_size=40
    )
    server_w4 = FixedBatchWindow(
        name="w4", source=server_s1, data_time_field="d", batch_size=50
    )  # To be deleted
    server_f1 = NullFilter(
        name="f1",
        source=server_s1,
        field="age",
    )
    server_f3 = NullFilter(
        name="f3",
        source=server_s1,
        field="age",
        operator=NullFilterOperator.IS_NOT,
    )
    server_f4 = NullFilter(
        name="f4",
        source=server_s1,
        field="age",
    )  # To be deleted
    server_seg1 = Segmentation(
        name="seg1",
        source=server_s1,
        fields=["city"],
        filter=server_f1,
    )
    server_seg3 = Segmentation(
        name="seg3",
        source=server_s1,
        fields=["country"],
        filter=server_f1,
    )  # To be deleted
    server_v1 = NumericValidator(
        name="v1",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericMetric.MAX,
        source_field="a",
        filter=server_f1,
    )
    server_v3 = NumericValidator(
        name="v3",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericMetric.MAX,
        source_field="d",
    )  # Delete
    server_ch1 = SlackChannel(
        name="ch1",
        application_link_url="app",
        slack_channel_id="sid",
        token="token",
        app_token="secret",
        __internal__=server_g,
    )
    server_ch3 = SlackChannel(
        name="ch3",
        application_link_url="app-changed",
        slack_channel_id="sid",
        token="token",
        app_token="secret",
        __internal__=server_g,
    )
    server_ch4 = SlackChannel(
        name="ch4",
        application_link_url="app",
        slack_channel_id="sid",
        token="token",
        app_token="secret",
        __internal__=server_g,
    )  # To be deleted
    server_cond1 = Conditions(
        source_condition=SourceNotificationRuleCondition(sources=[manifest_s1])
    )
    server_r1 = NotificationRule(name="r1", channel=server_ch1, conditions=server_cond1)
    server_r3 = NotificationRule(name="r3", channel=server_ch1)
    server_r4 = NotificationRule(
        name="r4", channel=server_ch1, conditions=server_cond1
    )  # To be deleted

    manifest_ctx = create_diff_context(
        credentials={manifest_c1.name: manifest_c1},
        sources={
            manifest_s1.name: manifest_s1,
            manifest_s2.name: manifest_s2,
        },
        segmentations={
            manifest_seg1.name: manifest_seg1,
            manifest_seg2.name: manifest_seg2,
        },
        windows={
            manifest_w1.name: manifest_w1,
            manifest_w2.name: manifest_w2,
            manifest_w3.name: manifest_w3,
        },
        filters={
            manifest_f1.name: manifest_f1,
            manifest_f2.name: manifest_f2,
            manifest_f3.name: manifest_f3,
        },
        validators={
            manifest_v1.name: manifest_v1,
            manifest_v2.name: manifest_v2,
        },
        channels={
            manifest_ch1.name: manifest_ch1,
            manifest_ch2.name: manifest_ch2,
            manifest_ch3.name: manifest_ch3,
        },
        notification_rules={
            manifest_r1.name: manifest_r1,
            manifest_r2.name: manifest_r2,
            manifest_r3.name: manifest_r3,
        },
    )

    server_ctx = create_diff_context(
        credentials={server_c1.name: server_c1},
        sources={
            server_s1.name: server_s1,
            server_s3.name: server_s3,
        },
        segmentations={
            server_seg1.name: server_seg1,
            server_seg3.name: server_seg3,
        },
        windows={
            server_w1.name: server_w1,
            server_w3.name: server_w3,
            server_w4.name: server_w4,
        },
        filters={
            server_f1.name: server_f1,
            server_f3.name: server_f3,
            server_f4.name: server_f4,
        },
        validators={
            server_v1.name: server_v1,
            server_v3.name: server_v3,
        },
        channels={
            server_ch1.name: server_ch1,
            server_ch3.name: server_ch3,
            server_ch4.name: server_ch4,
        },
        notification_rules={
            server_r1.name: server_r1,
            server_r3.name: server_r3,
            server_r4.name: server_r4,
        },
    )

    expected = create_graph_diff(
        to_create=DiffContext(
            sources={manifest_s2.name: manifest_s2},
            segmentations={manifest_seg2.name: manifest_seg2},
            windows={manifest_w2.name: manifest_w2},
            filters={manifest_f2.name: manifest_f2},
            validators={manifest_v2.name: manifest_v2},
            channels={manifest_ch2.name: manifest_ch2},
            notification_rules={manifest_r2.name: manifest_r2},
        ),
        to_delete=DiffContext(
            sources={server_s3.name: server_s3},
            segmentations={server_seg3.name: server_seg3},
            windows={server_w4.name: server_w4},
            filters={server_f4.name: server_f4},
            validators={server_v3.name: server_v3},
            channels={server_ch4.name: server_ch4},
            notification_rules={server_r4.name: server_r4},
        ),
        to_update=create_resource_updates(
            windows={
                manifest_w3.name: ResourceUpdate(
                    manifest_w3,
                    server_w3,
                )
            },
            filters={
                manifest_f3.name: ResourceUpdate(
                    manifest_f3,
                    server_f3,
                )
            },
            channels={
                manifest_ch3.name: ResourceUpdate(
                    manifest_ch3,
                    server_ch3,
                ),
            },
            notification_rules={
                manifest_r3.name: ResourceUpdate(
                    manifest_r3,
                    server_r3,
                )
            },
        ),
    )

    _add_namespace(namespace, server_ctx)
    assert expected == _diff_resource_graph(namespace, manifest_ctx, server_ctx)


def test_diff_replace_with_cascade() -> None:
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential(name="c1", __internal__=manifest_g)
    manifest_c2 = DemoCredential(name="c2", __internal__=manifest_g)

    # s1 switches from one credential to another => replace.
    manifest_s1 = DemoSource(name="s1", credential=manifest_c2)
    manifest_s2 = DemoSource(name="s2", credential=manifest_c1)
    # w1 belongs to s1, => replace.
    manifest_w1 = TumblingWindow(
        name="w1",
        source=manifest_s1,
        data_time_field="d",
        window_size=1,
        time_unit=WindowTimeUnit.DAY,
    )
    # seg1 belongs to s1 => replace.
    manifest_seg1 = Segmentation(name="seg1", source=manifest_s1, fields=["city"])
    # f1 belongs to s1 => replace.
    manifest_f1 = NullFilter(name="f1", source=manifest_s1, field="age")
    # f2 switches from s1 to s2 => replace.
    manifest_f2 = NullFilter(name="f2", source=manifest_s2, field="age")
    # v1 and v2 belong to s1 => replace.
    manifest_v1 = NumericValidator(
        name="v1",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MAX,
        source_field="a",
    )
    manifest_v2 = NumericValidator(
        name="v2",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MAX,
        source_field="b",
    )

    manifest_ch1 = SlackChannel(
        name="ch1",
        application_link_url="app",
        slack_channel_id="sid",
        token="token",
        app_token="secret",
        __internal__=manifest_g,
    )
    manifest_ch2 = SlackChannel(
        name="ch2",
        application_link_url="app",
        slack_channel_id="sid",
        token="token",
        app_token="secret",
        __internal__=manifest_g,
    )
    # r1 switches from one credential to another => replace.
    manifest_r1 = NotificationRule(name="r1", channel=manifest_ch2)

    server_c1 = DemoCredential(name="c1", __internal__=server_g)
    server_c2 = DemoCredential(name="c2", __internal__=server_g)
    server_s1 = DemoSource(name="s1", credential=server_c1)
    server_s2 = DemoSource(name="s2", credential=server_c1)
    server_w1 = TumblingWindow(
        name="w1",
        source=server_s1,
        data_time_field="d",
        window_size=1,
        time_unit=WindowTimeUnit.DAY,
    )
    server_seg1 = Segmentation(name="seg1", source=server_s1, fields=["city"])
    server_f1 = NullFilter(name="f1", source=server_s1, field="age")
    server_f2 = NullFilter(name="f2", source=server_s1, field="age")
    server_v1 = NumericValidator(
        name="v1",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericMetric.MAX,
        source_field="a",
    )
    server_v2 = NumericValidator(
        name="v2",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericMetric.MAX,
        source_field="b",
    )
    server_ch1 = SlackChannel(
        name="ch1",
        application_link_url="app",
        slack_channel_id="sid",
        token="token",
        app_token="secret",
        __internal__=server_g,
    )
    server_ch2 = SlackChannel(
        name="ch2",
        application_link_url="app",
        slack_channel_id="sid",
        token="token",
        app_token="secret",
        __internal__=server_g,
    )
    server_r1 = NotificationRule(name="r1", channel=server_ch1)

    manifest_ctx = create_diff_context(
        credentials={
            manifest_c1.name: manifest_c1,
            manifest_c2.name: manifest_c2,
        },
        sources={
            manifest_s1.name: manifest_s1,
            manifest_s2.name: manifest_s2,
        },
        segmentations={
            manifest_seg1.name: manifest_seg1,
        },
        windows={
            manifest_w1.name: manifest_w1,
        },
        filters={
            manifest_f1.name: manifest_f1,
            manifest_f2.name: manifest_f2,
        },
        validators={
            manifest_v1.name: manifest_v1,
            manifest_v2.name: manifest_v2,
        },
        channels={
            manifest_ch1.name: manifest_ch1,
            manifest_ch2.name: manifest_ch2,
        },
        notification_rules={
            manifest_r1.name: manifest_r1,
        },
    )

    server_ctx = create_diff_context(
        credentials={
            server_c1.name: server_c1,
            server_c2.name: server_c2,
        },
        sources={
            server_s1.name: server_s1,
            server_s2.name: server_s2,
        },
        segmentations={
            server_seg1.name: server_seg1,
        },
        windows={
            server_w1.name: server_w1,
        },
        filters={
            server_f1.name: server_f1,
            server_f2.name: server_f2,
        },
        validators={
            server_v1.name: server_v1,
            server_v2.name: server_v2,
        },
        channels={
            server_ch1.name: server_ch1,
            server_ch2.name: server_ch2,
        },
        notification_rules={
            server_r1.name: server_r1,
        },
    )

    expected = create_graph_diff(
        to_create=DiffContext(
            sources={manifest_s1.name: manifest_s1},
            segmentations={manifest_seg1.name: manifest_seg1},
            windows={
                manifest_w1.name: manifest_w1,
            },
            filters={
                manifest_f1.name: manifest_f1,
                manifest_f2.name: manifest_f2,
            },
            validators={
                manifest_v1.name: manifest_v1,
                manifest_v2.name: manifest_v2,
            },
            notification_rules={manifest_r1.name: manifest_r1},
        ),
        to_delete=DiffContext(
            sources={server_s1.name: server_s1},
            segmentations={server_seg1.name: server_seg1},
            windows={server_w1.name: server_w1},
            filters={
                server_f1.name: server_f1,
                server_f2.name: server_f2,
            },
            validators={
                server_v1.name: server_v1,
                server_v2.name: server_v2,
            },
            notification_rules={server_r1.name: server_r1},
        ),
        replacement_ctx=ReplacementContext(
            sources={
                manifest_s1.name: ImmutableFieldReplacementReason(
                    field_name="credential_name",
                    resource_update=ResourceUpdate(
                        manifest_s1,
                        server_s1,
                        replacement_field="credential_name",
                    ),
                )
            },
            segmentations={
                manifest_seg1.name: CascadeReplacementReason(
                    parent_resource_cls=DemoSource,
                    parent_resource_name=manifest_s1.name,
                )
            },
            windows={
                manifest_w1.name: CascadeReplacementReason(
                    parent_resource_cls=DemoSource,
                    parent_resource_name=manifest_s1.name,
                )
            },
            filters={
                manifest_f1.name: CascadeReplacementReason(
                    parent_resource_cls=DemoSource,
                    parent_resource_name=manifest_s1.name,
                ),
                manifest_f2.name: ImmutableFieldReplacementReason(
                    field_name="source_name",
                    resource_update=ResourceUpdate(
                        manifest_f2,
                        server_f2,
                        replacement_field="source_name",
                    ),
                ),
            },
            validators={
                manifest_v1.name: CascadeReplacementReason(
                    parent_resource_cls=DemoSource,
                    parent_resource_name=manifest_s1.name,
                ),
                manifest_v2.name: CascadeReplacementReason(
                    parent_resource_cls=DemoSource,
                    parent_resource_name=manifest_s1.name,
                ),
            },
            notification_rules={
                manifest_r1.name: ImmutableFieldReplacementReason(
                    field_name="channel_name",
                    resource_update=ResourceUpdate(
                        manifest_r1,
                        server_r1,
                        replacement_field="channel_name",
                    ),
                ),
            },
        ),
    )

    _add_namespace(namespace, server_ctx)
    actual = _diff_resource_graph(namespace, manifest_ctx, server_ctx)
    _compute_replacements(
        manifest_ctx=manifest_ctx,
        server_ctx=server_ctx,
        graph_diff=actual,
    )
    assert expected == actual


def test_diff_replace_without_cascade() -> None:
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential(name="c1", __internal__=manifest_g)

    manifest_s1 = DemoSource(name="s1", credential=manifest_c1)
    manifest_s2 = DemoSource(name="s2", credential=manifest_c1)
    manifest_w1 = TumblingWindow(
        name="w1",
        source=manifest_s1,
        data_time_field="d",
        window_size=1,
        time_unit=WindowTimeUnit.DAY,
    )
    manifest_w2 = TumblingWindow(
        name="w2",
        source=manifest_s1,
        data_time_field="updated",
        window_size=1,
        time_unit=WindowTimeUnit.DAY,
    )
    manifest_seg1 = Segmentation(name="seg1", source=manifest_s1, fields=["city"])
    manifest_seg2 = Segmentation(name="seg2", source=manifest_s1, fields=["updated"])
    manifest_f1 = NullFilter(name="f1", source=manifest_s1, field="age")
    manifest_v1 = NumericValidator(
        name="v1",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MAX,
        source_field="updated",
        filter=manifest_f1,
    )
    manifest_v2 = NumericValidator(
        name="v2",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MAX,
        source_field="b",
        filter=manifest_f1,
    )
    manifest_v3 = NumericValidator(
        name="v3",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MAX,
        source_field="b",
    )
    manifest_v4 = NumericValidator(
        name="v4",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MAX,
        source_field="b",
    )
    # v6 switches from fixed to dynamic threshold => replace
    manifest_v6 = NumericValidator(
        name="v6",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MAX,
        source_field="a",
        threshold=DynamicThreshold(sensitivity=3),
    )

    server_c1 = DemoCredential(name="c1", __internal__=server_g)
    server_s1 = DemoSource(name="s1", credential=server_c1)
    server_s2 = DemoSource(name="s2", credential=server_c1)
    server_w1 = TumblingWindow(
        name="w1",
        source=server_s1,
        data_time_field="d",
        window_size=1,
        time_unit=WindowTimeUnit.DAY,
    )
    server_w2 = TumblingWindow(
        name="w2",
        source=server_s1,
        data_time_field="d",
        window_size=1,
        time_unit=WindowTimeUnit.DAY,
    )
    server_seg1 = Segmentation(name="seg1", source=server_s1, fields=["city"])
    server_seg2 = Segmentation(name="seg2", source=server_s1, fields=["city"])
    server_f1 = NullFilter(name="f1", source=server_s1, field="age")
    server_v1 = NumericValidator(
        name="v1",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericMetric.MAX,
        source_field="a",
        filter=server_f1,
    )
    server_v2 = NumericValidator(
        name="v2",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericMetric.MAX,
        source_field="b",
        filter=server_f1,
    )
    server_v3 = NumericValidator(
        name="v3",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericMetric.MAX,
        source_field="b",
    )
    server_v5 = NumericValidator(
        name="v5",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericMetric.MAX,
        source_field="b",
    )
    server_v6 = NumericValidator(
        name="v6",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericMetric.MAX,
        source_field="a",
        threshold=FixedThreshold(value=0.1, operator=ComparisonOperator.EQUAL),
    )

    manifest_ctx = create_diff_context(
        credentials={
            manifest_c1.name: manifest_c1,
        },
        sources={
            manifest_s1.name: manifest_s1,
            manifest_s2.name: manifest_s2,
        },
        segmentations={
            manifest_seg1.name: manifest_seg1,
            manifest_seg2.name: manifest_seg2,
        },
        windows={
            manifest_w1.name: manifest_w1,
            manifest_w2.name: manifest_w2,
        },
        filters={
            manifest_f1.name: manifest_f1,
        },
        validators={
            manifest_v1.name: manifest_v1,
            manifest_v2.name: manifest_v2,
            manifest_v3.name: manifest_v3,
            manifest_v4.name: manifest_v4,
            manifest_v6.name: manifest_v6,
        },
    )

    server_ctx = create_diff_context(
        credentials={
            server_c1.name: server_c1,
        },
        sources={
            server_s1.name: server_s1,
            server_s2.name: server_s2,
        },
        segmentations={
            server_seg1.name: server_seg1,
            server_seg2.name: server_seg2,
        },
        windows={
            server_w1.name: server_w1,
            server_w2.name: server_w2,
        },
        filters={
            server_f1.name: server_f1,
        },
        validators={
            server_v1.name: server_v1,
            server_v2.name: server_v2,
            server_v3.name: server_v3,
            server_v5.name: server_v5,
            server_v6.name: server_v6,
        },
    )

    expected = create_graph_diff(
        to_create=DiffContext(
            segmentations={
                manifest_seg2.name: manifest_seg2,
            },
            windows={
                manifest_w2.name: manifest_w2,
            },
            validators={
                manifest_v1.name: manifest_v1,
                manifest_v4.name: manifest_v4,
                manifest_v6.name: manifest_v6,
            },
        ),
        to_delete=DiffContext(
            segmentations={server_seg2.name: server_seg2},
            windows={server_w2.name: server_w2},
            validators={
                server_v1.name: server_v1,
                server_v5.name: server_v5,
                server_v6.name: server_v6,
            },
        ),
        replacement_ctx=ReplacementContext(
            segmentations={
                manifest_seg2.name: ImmutableFieldReplacementReason(
                    field_name="fields",
                    resource_update=ResourceUpdate(
                        manifest_seg2,
                        server_seg2,
                        replacement_field="fields",
                    ),
                )
            },
            windows={
                manifest_w2.name: ImmutableFieldReplacementReason(
                    field_name="data_time_field",
                    resource_update=ResourceUpdate(
                        manifest_w2,
                        server_w2,
                        replacement_field="data_time_field",
                    ),
                )
            },
            validators={
                manifest_v1.name: ImmutableFieldReplacementReason(
                    field_name="source_field",
                    resource_update=ResourceUpdate(
                        manifest_v1,
                        server_v1,
                        replacement_field="source_field",
                    ),
                ),
                manifest_v6.name: ImmutableFieldReplacementReason(
                    field_name="threshold",
                    resource_update=ResourceUpdate(
                        manifest_v6,
                        server_v6,
                        replacement_field="threshold",
                    ),
                ),
            },
        ),
    )

    _add_namespace(namespace, server_ctx)
    actual = _diff_resource_graph(namespace, manifest_ctx, server_ctx)
    _compute_replacements(
        manifest_ctx=manifest_ctx,
        server_ctx=server_ctx,
        graph_diff=actual,
    )
    assert expected == actual


def test_diff_replace_cascade_with_conflicting_ops() -> None:
    """
    Replacing a resource that already has a create/update/delete
    operation ongoing.
    """
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential(name="c1", __internal__=manifest_g)

    manifest_s1 = DemoSource(name="s1", credential=manifest_c1)
    # Updated both mutable and immutable property => replace
    manifest_w1 = TumblingWindow(
        name="w1",
        source=manifest_s1,
        data_time_field="updated",
        window_size=2,
        time_unit=WindowTimeUnit.DAY,
        window_timeout_disabled=True,
    )
    manifest_seg1 = Segmentation(name="seg1", source=manifest_s1, fields=["city"])
    manifest_f1 = NullFilter(name="f1", source=manifest_s1, field="age")
    # Validator to create
    manifest_v1 = NumericValidator(
        name="v1",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MAX,
        source_field="updated",
        filter=manifest_f1,
    )
    # Validator to update
    manifest_v2 = NumericDistributionValidator(
        name="v2",
        window=manifest_w1,
        segmentation=manifest_seg1,
        threshold=DynamicThreshold(sensitivity=2),
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        filter=manifest_f1,
        reference=Reference(
            history=1,
            offset=0,
            filter=manifest_f1,
        ),
    )

    server_c1 = DemoCredential(name="c1", __internal__=server_g)
    server_s1 = DemoSource(name="s1", credential=server_c1)
    server_w1 = TumblingWindow(
        name="w1",
        source=server_s1,
        data_time_field="d",
        window_size=2,
        time_unit=WindowTimeUnit.DAY,
        window_timeout_disabled=False,
    )
    server_seg1 = Segmentation(name="seg1", source=server_s1, fields=["city"])
    server_f1 = NullFilter(name="f1", source=server_s1, field="age")
    server_v2 = NumericDistributionValidator(
        name="v2",
        window=server_w1,
        segmentation=server_seg1,
        threshold=DynamicThreshold(sensitivity=2),
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        filter=server_f1,
        reference=Reference(
            history=10,
            offset=1,
            filter=server_f1,
        ),
    )
    # Validator to delete
    server_v3 = NumericValidator(
        name="v3",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericMetric.MAX,
        source_field="b",
        filter=server_f1,
    )

    manifest_ctx = create_diff_context(
        credentials={
            manifest_c1.name: manifest_c1,
        },
        sources={
            manifest_s1.name: manifest_s1,
        },
        segmentations={
            manifest_seg1.name: manifest_seg1,
        },
        windows={
            manifest_w1.name: manifest_w1,
        },
        filters={
            manifest_f1.name: manifest_f1,
        },
        validators={
            manifest_v1.name: manifest_v1,
            manifest_v2.name: manifest_v2,
        },
    )

    server_ctx = create_diff_context(
        credentials={
            server_c1.name: server_c1,
        },
        sources={
            server_s1.name: server_s1,
        },
        segmentations={
            server_seg1.name: server_seg1,
        },
        windows={
            server_w1.name: server_w1,
        },
        filters={
            server_f1.name: server_f1,
        },
        validators={
            server_v2.name: server_v2,
            server_v3.name: server_v3,
        },
    )

    expected = create_graph_diff(
        to_create=DiffContext(
            windows={
                manifest_w1.name: manifest_w1,
            },
            validators={
                manifest_v1.name: manifest_v1,
                manifest_v2.name: manifest_v2,
            },
        ),
        to_delete=DiffContext(
            windows={server_w1.name: server_w1},
            validators={
                server_v2.name: server_v2,
                server_v3.name: server_v3,
            },
        ),
        replacement_ctx=ReplacementContext(
            windows={
                manifest_w1.name: ImmutableFieldReplacementReason(
                    field_name="data_time_field",
                    resource_update=ResourceUpdate(
                        manifest_w1,
                        server_w1,
                        replacement_field="data_time_field",
                    ),
                )
            },
            validators={
                manifest_v1.name: CascadeReplacementReason(
                    parent_resource_cls=TumblingWindow,
                    parent_resource_name=manifest_w1.name,
                ),
                manifest_v2.name: CascadeReplacementReason(
                    parent_resource_cls=TumblingWindow,
                    parent_resource_name=manifest_w1.name,
                ),
            },
        ),
    )

    _add_namespace(namespace, server_ctx)
    actual = _diff_resource_graph(namespace, manifest_ctx, server_ctx)
    _compute_replacements(
        manifest_ctx=manifest_ctx,
        server_ctx=server_ctx,
        graph_diff=actual,
    )
    assert expected == actual


def test_diff_should_not_cascade_filter_replace() -> None:
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential(name="c1", __internal__=manifest_g)
    manifest_c2 = DemoCredential(name="c2", __internal__=manifest_g)
    manifest_s1 = DemoSource(name="s1", credential=manifest_c1)
    manifest_s2 = DemoSource(name="s2", credential=manifest_c1)
    manifest_w1 = TumblingWindow(
        name="w1",
        source=manifest_s1,
        data_time_field="d",
        window_size=1,
        time_unit=WindowTimeUnit.DAY,
    )
    manifest_seg1 = Segmentation(name="seg1", source=manifest_s1, fields=["city"])

    # f1 switches sources from s1 to s2.
    manifest_f1 = NullFilter(name="f1", source=manifest_s2, field="age")

    # f2 has no diff.
    manifest_f2 = NullFilter(name="f2", source=manifest_s1, field="age")

    # v1 should be updated, not replaced (because filters are mutable)
    manifest_v1 = NumericValidator(
        name="v1",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MAX,
        source_field="a",
        filter=manifest_f1,
    )

    # v2 is being created, the changes it should be
    # unaffected by the cascade from f1.
    manifest_v2 = NumericValidator(
        name="v2",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericMetric.MAX,
        source_field="a",
        filter=manifest_f1,
    )

    # v3 uses a reference filter, it should also be updated.
    manifest_v3 = NumericDistributionValidator(
        name="v3",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        reference=Reference(
            history=10,
            offset=1,
            filter=manifest_f1,
        ),
    )

    # v4 uses a reference filter f2 - which has no diff. So it also
    # has no diff.
    manifest_v4 = NumericDistributionValidator(
        name="v4",
        window=manifest_w1,
        segmentation=manifest_seg1,
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        reference=Reference(
            history=10,
            offset=1,
            filter=manifest_f2,
        ),
    )

    server_c1 = DemoCredential(name="c1", __internal__=server_g)
    server_c2 = DemoCredential(name="c2", __internal__=server_g)
    server_s1 = DemoSource(name="s1", credential=server_c1)
    server_s2 = DemoSource(name="s2", credential=server_c1)
    server_w1 = TumblingWindow(
        name="w1",
        source=server_s1,
        data_time_field="d",
        window_size=1,
        time_unit=WindowTimeUnit.DAY,
    )
    server_seg1 = Segmentation(name="seg1", source=server_s1, fields=["city"])
    server_f1 = NullFilter(name="f1", source=server_s1, field="age")
    server_f2 = NullFilter(name="f2", source=server_s1, field="age")
    server_v1 = NumericValidator(
        name="v1",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericMetric.MAX,
        source_field="a",
        filter=server_f1,
    )
    server_v3 = NumericDistributionValidator(
        name="v3",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        reference=Reference(
            history=10,
            offset=1,
            filter=server_f1,
        ),
    )
    server_v4 = NumericDistributionValidator(
        name="v4",
        window=server_w1,
        segmentation=server_seg1,
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        reference=Reference(
            history=10,
            offset=1,
            filter=server_f2,
        ),
    )

    manifest_ctx = create_diff_context(
        credentials={
            manifest_c1.name: manifest_c1,
            manifest_c2.name: manifest_c2,
        },
        sources={
            manifest_s1.name: manifest_s1,
            manifest_s2.name: manifest_s2,
        },
        segmentations={
            manifest_seg1.name: manifest_seg1,
        },
        windows={
            manifest_w1.name: manifest_w1,
        },
        filters={
            manifest_f1.name: manifest_f1,
            manifest_f2.name: manifest_f2,
        },
        validators={
            manifest_v1.name: manifest_v1,
            manifest_v2.name: manifest_v2,
            manifest_v3.name: manifest_v3,
            manifest_v4.name: manifest_v4,
        },
    )

    server_ctx = create_diff_context(
        credentials={
            server_c1.name: server_c1,
            server_c2.name: server_c2,
        },
        sources={
            server_s1.name: server_s1,
            server_s2.name: server_s2,
        },
        segmentations={
            server_seg1.name: server_seg1,
        },
        windows={
            server_w1.name: server_w1,
        },
        filters={
            server_f1.name: server_f1,
            server_f2.name: server_f2,
        },
        validators={
            server_v1.name: server_v1,
            server_v3.name: server_v3,
            server_v4.name: server_v4,
        },
    )

    expected = create_graph_diff(
        to_create=DiffContext(
            filters={manifest_f1.name: manifest_f1},
            validators={manifest_v2.name: manifest_v2},
        ),
        to_delete=DiffContext(
            filters={server_f1.name: server_f1},
        ),
        to_update=create_resource_updates(
            validators={
                manifest_v1.name: ResourceUpdate(
                    manifest_v1,
                    server_v1,
                    replacement_cascaded_update_parent=(
                        NullFilter,
                        manifest_f1.name,
                    ),
                ),
                manifest_v3.name: ResourceUpdate(
                    manifest_v3,
                    server_v3,
                    replacement_cascaded_update_parent=(
                        NullFilter,
                        manifest_f1.name,
                    ),
                ),
            },
        ),
        replacement_ctx=ReplacementContext(
            filters={
                manifest_f1.name: ImmutableFieldReplacementReason(
                    field_name="source_name",
                    resource_update=ResourceUpdate(
                        manifest_f1,
                        server_f1,
                        replacement_field="source_name",
                    ),
                ),
            },
        ),
    )

    _add_namespace(namespace, server_ctx)
    actual = _diff_resource_graph(namespace, manifest_ctx, server_ctx)
    _compute_replacements(
        manifest_ctx=manifest_ctx,
        server_ctx=server_ctx,
        graph_diff=actual,
    )
    assert expected == actual


@pytest.mark.parametrize(
    ("history", "offset", "expect_update"),
    [
        (10, 20, False),
        (11, 20, True),
        (10, 21, True),
        (10, 10, True),
    ],
)
def test_diff_should_detect_updates_on_nested_objects(
    history: int,
    offset: int,
    expect_update: bool,
) -> None:
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential(name="c1", __internal__=manifest_g)
    manifest_s1 = DemoSource(name="s1", credential=manifest_c1)
    manifest_seg1 = Segmentation(name="seg1", source=manifest_s1, fields=["city"])
    manifest_w1 = TumblingWindow(
        name="w1",
        source=manifest_s1,
        data_time_field="d",
        window_size=1,
        time_unit=WindowTimeUnit.DAY,
    )
    manifest_f1 = NullFilter(name="f1", source=manifest_s1, field="a")

    manifest_v = NumericDistributionValidator(
        name="v1",
        window=manifest_w1,
        segmentation=manifest_seg1,
        threshold=DynamicThreshold(sensitivity=2),
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        filter=manifest_f1,
        reference=Reference(
            history=history,
            offset=offset,
            filter=manifest_f1,
        ),
    )

    manifest_ch1 = WebhookChannel(
        name="ch1",
        application_link_url="link",
        webhook_url="url",
        auth_header="header",
        __internal__=manifest_g,
    )

    manifest_nr1 = NotificationRule(
        name="nr1",
        channel=manifest_ch1,
        conditions=Conditions(
            tag_conditions=[TagNotificationRuleCondition(tags={"label": "a"})]
        ),
    )

    manifest_nr2 = NotificationRule(
        name="nr2",
        channel=manifest_ch1,
        conditions=Conditions(
            tag_conditions=[
                TagNotificationRuleCondition(tags={"label": "a"}),
                TagNotificationRuleCondition(tags={"another_label": "a"}),
            ]
        ),
    )

    server_c1 = DemoCredential(name="c1", __internal__=server_g)
    server_s1 = DemoSource(name="s1", credential=server_c1)
    server_seg1 = Segmentation(name="seg1", source=server_s1, fields=["city"])
    server_w1 = TumblingWindow(
        name="w1",
        source=server_s1,
        data_time_field="d",
        window_size=1,
        time_unit=WindowTimeUnit.DAY,
    )
    server_f1 = NullFilter(name="f1", source=server_s1, field="a")
    server_v = NumericDistributionValidator(
        name="v1",
        window=server_w1,
        segmentation=server_seg1,
        threshold=DynamicThreshold(sensitivity=2),
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        filter=server_f1,
        reference=Reference(10, 20, filter=server_f1),
    )

    server_ch1 = WebhookChannel(
        name="ch1",
        application_link_url="link",
        webhook_url="url",
        auth_header="header",
        __internal__=server_g,
    )

    server_nr1 = NotificationRule(
        name="nr1",
        channel=server_ch1,
        conditions=Conditions(
            tag_conditions=[TagNotificationRuleCondition(tags={"label": "b"})]
        ),
    )

    server_nr2 = NotificationRule(
        name="nr2",
        channel=server_ch1,
        conditions=Conditions(
            tag_conditions=[
                TagNotificationRuleCondition(tags={"label": "b"}),
                TagNotificationRuleCondition(tags={"another_label": "b"}),
            ]
        ),
    )

    manifest_ctx = create_diff_context(
        credentials={manifest_c1.name: manifest_c1},
        sources={manifest_s1.name: manifest_s1},
        segmentations={manifest_seg1.name: manifest_seg1},
        windows={manifest_w1.name: manifest_w1},
        filters={
            manifest_f1.name: manifest_f1,
        },
        validators={manifest_v.name: manifest_v},
        notification_rules={
            manifest_nr1.name: manifest_nr1,
            manifest_nr2.name: manifest_nr2,
        },
    )
    server_ctx = create_diff_context(
        credentials={server_c1.name: server_c1},
        sources={server_s1.name: server_s1},
        segmentations={server_seg1.name: server_seg1},
        windows={server_w1.name: server_w1},
        filters={
            server_f1.name: server_f1,
        },
        validators={server_v.name: server_v},
        notification_rules={server_nr1.name: server_nr1, server_nr2.name: server_nr2},
    )

    expected = create_graph_diff(
        to_update=create_resource_updates(
            validators=(
                {
                    manifest_v.name: ResourceUpdate(
                        manifest_v,
                        server_v,
                    ),
                }
                if expect_update
                else {}
            ),
            notification_rules=(
                {
                    manifest_nr1.name: ResourceUpdate(manifest_nr1, server_nr1),
                    manifest_nr2.name: ResourceUpdate(manifest_nr2, server_nr2),
                }
            ),
        )
    )

    _add_namespace(namespace, server_ctx)
    assert expected == _diff_resource_graph(namespace, manifest_ctx, server_ctx)


def test_diff_should_ignore_update_on_ignore_changes() -> None:
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    # c1 has diff, but ignored changes
    manifest_c1 = AwsCredential(
        name="c1",
        access_key="ak1",
        secret_key="sk1",
        ignore_changes=True,
        __internal__=manifest_g,
    )
    # c2 has diff, and doesn't ignore changes
    manifest_c2 = AwsCredential(
        name="c2",
        access_key="ak2",
        secret_key="sk2",
        ignore_changes=False,
        __internal__=manifest_g,
    )
    # c3 is new, and ignores changes.
    manifest_c3 = AwsCredential(
        name="c3",
        access_key="ak3",
        secret_key="sk3",
        ignore_changes=True,
        __internal__=manifest_g,
    )

    server_c1 = AwsCredential(
        name="c1",
        access_key="ak1old",
        secret_key="sk1old",
        ignore_changes=True,
        __internal__=server_g,
    )
    server_c2 = AwsCredential(
        name="c2",
        access_key="ak2old",
        secret_key="sk2old",
        ignore_changes=False,
        __internal__=server_g,
    )
    # c4 is being deleted and ignores changes.
    server_c4 = AwsCredential(
        name="c4",
        access_key="ak4",
        secret_key="sk4",
        ignore_changes=True,
        __internal__=server_g,
    )

    manifest_ctx = create_diff_context(
        credentials={
            manifest_c1.name: manifest_c1,
            manifest_c2.name: manifest_c2,
            manifest_c3.name: manifest_c3,
        },
    )
    server_ctx = create_diff_context(
        credentials={
            server_c1.name: server_c1,
            server_c2.name: server_c2,
            server_c4.name: server_c4,
        },
    )

    expected = create_graph_diff(
        to_create=DiffContext(
            credentials={manifest_c3.name: manifest_c3},
        ),
        to_delete=DiffContext(
            credentials={server_c4.name: server_c4},
        ),
        to_update=create_resource_updates(
            credentials={manifest_c2.name: ResourceUpdate(manifest_c2, server_c2)},
        ),
    )

    _add_namespace(namespace, server_ctx)
    assert expected == _diff_resource_graph(namespace, manifest_ctx, server_ctx)


def test_enum_filter_values_should_ignore_order() -> None:
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential(
        name="c1",
        __internal__=manifest_g,
    )
    manifest_s1 = DemoSource(
        name="s1",
        credential=manifest_c1,
    )
    manifest_seg1 = Segmentation(
        name="seg1",
        source=manifest_s1,
    )
    manifest_w1 = FixedBatchWindow(
        name="w1",
        source=manifest_s1,
        data_time_field="a",
        batch_size=10,
    )
    manifest_f1 = EnumFilter(
        name="f1",
        source=manifest_s1,
        field="Gender",
        values=["a", "b"],
    )
    manifest_f2 = EnumFilter(
        name="f2",
        source=manifest_s1,
        field="Gender",
        values=["b", "c"],
    )
    # v1 has enum values of the same list but different ordering.
    manifest_v1 = NumericValidator(
        name="v1",
        window=manifest_w1,
        segmentation=manifest_seg1,
        source_field="a",
        metric=NumericMetric.MAX,
        filter=manifest_f1,
    )
    # v2 has enum values of different lists.
    manifest_v2 = NumericValidator(
        name="v2",
        window=manifest_w1,
        segmentation=manifest_seg1,
        source_field="a",
        metric=NumericMetric.MAX,
        filter=manifest_f2,
    )

    server_c1 = DemoCredential(
        name="c1",
        __internal__=server_g,
    )
    server_s1 = DemoSource(
        name="s1",
        credential=server_c1,
    )
    server_seg1 = Segmentation(
        name="seg1",
        source=server_s1,
    )
    server_w1 = FixedBatchWindow(
        name="w1",
        source=server_s1,
        data_time_field="a",
        batch_size=10,
    )
    server_f1 = EnumFilter(
        name="f1",
        source=server_s1,
        field="Gender",
        values=["b", "a"],
    )
    server_f2 = EnumFilter(
        name="f2",
        source=server_s1,
        field="Gender",
        values=["b"],
    )
    server_v1 = NumericValidator(
        name="v1",
        window=server_w1,
        segmentation=server_seg1,
        source_field="a",
        metric=NumericMetric.MAX,
        filter=server_f1,
    )
    server_v2 = NumericValidator(
        name="v2",
        window=server_w1,
        segmentation=server_seg1,
        source_field="a",
        metric=NumericMetric.MAX,
        filter=server_f2,
    )

    manifest_ctx = create_diff_context(
        credentials={manifest_c1.name: manifest_c1},
        sources={
            manifest_s1.name: manifest_s1,
        },
        segmentations={
            manifest_seg1.name: manifest_seg1,
        },
        windows={
            manifest_w1.name: manifest_w1,
        },
        filters={
            manifest_f1.name: manifest_f1,
            manifest_f2.name: manifest_f2,
        },
        validators={
            manifest_v1.name: manifest_v1,
            manifest_v2.name: manifest_v2,
        },
    )

    server_ctx = create_diff_context(
        credentials={server_c1.name: server_c1},
        sources={
            server_s1.name: server_s1,
        },
        segmentations={
            server_seg1.name: server_seg1,
        },
        windows={
            server_w1.name: server_w1,
        },
        filters={
            server_f1.name: server_f1,
            server_f2.name: server_f2,
        },
        validators={
            server_v1.name: server_v1,
            server_v2.name: server_v2,
        },
    )

    expected = create_graph_diff(
        to_update=create_resource_updates(
            filters={
                manifest_f2.name: ResourceUpdate(
                    manifest_f2,
                    server_f2,
                )
            },
        ),
    )

    _add_namespace(namespace, server_ctx)
    assert expected == _diff_resource_graph(namespace, manifest_ctx, server_ctx)


def test_filter_backwards_compatibility() -> None:
    namespace = "my_namespace"
    manifest_g = ResourceGraph()
    server_g = ResourceGraph()

    manifest_c1 = DemoCredential(
        name="c1",
        __internal__=manifest_g,
    )
    manifest_s1 = DemoSource(
        name="s1",
        credential=manifest_c1,
    )
    filter_f1 = NullFilter(name="f1", source=manifest_s1, field="a")
    manifest_seg1 = Segmentation(
        name="seg1",
        source=manifest_s1,
    )
    manifest_w1 = FixedBatchWindow(
        name="w1",
        source=manifest_s1,
        data_time_field="a",
        batch_size=10,
    )
    # v1 has old filter type
    manifest_v1 = NumericValidator(
        name="v1",
        window=manifest_w1,
        segmentation=manifest_seg1,
        source_field="a",
        metric=NumericMetric.MAX,
        filter=filter_f1,
    )
    # v2 has old reference filter type.
    manifest_v2 = NumericDistributionValidator(
        name="v2",
        window=manifest_w1,
        segmentation=manifest_seg1,
        threshold=DynamicThreshold(sensitivity=2),
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        reference=Reference(
            history=10,
            offset=20,
            filter=filter_f1,
        ),
    )

    server_c1 = DemoCredential(
        name="c1",
        __internal__=server_g,
    )
    server_s1 = DemoSource(
        name="s1",
        credential=server_c1,
    )
    server_seg1 = Segmentation(
        name="seg1",
        source=server_s1,
    )
    server_w1 = FixedBatchWindow(
        name="w1",
        source=server_s1,
        data_time_field="a",
        batch_size=10,
    )
    server_f1 = NullFilter(
        name="f1",
        source=server_s1,
        field="a",
    )
    # Legit unused filter to be deleted
    server_f2 = NullFilter(
        name="f2",
        source=server_s1,
        field="a",
    )
    server_v1 = NumericValidator(
        name="v1",
        window=server_w1,
        segmentation=server_seg1,
        source_field="a",
        metric=NumericMetric.MAX,
        filter=server_f1,
    )
    server_v2 = NumericDistributionValidator(
        name="v2",
        window=server_w1,
        segmentation=server_seg1,
        threshold=DynamicThreshold(sensitivity=2),
        metric=NumericDistributionMetric.MAXIMUM_RATIO,
        source_field="a",
        reference_source_field="b",
        reference=Reference(
            history=10,
            offset=20,
            filter=server_f1,
        ),
    )

    manifest_ctx = create_diff_context(
        credentials={manifest_c1.name: manifest_c1},
        sources={
            manifest_s1.name: manifest_s1,
        },
        segmentations={
            manifest_seg1.name: manifest_seg1,
        },
        windows={
            manifest_w1.name: manifest_w1,
        },
        validators={
            manifest_v1.name: manifest_v1,
            manifest_v2.name: manifest_v2,
        },
    )

    server_ctx = create_diff_context(
        credentials={server_c1.name: server_c1},
        sources={
            server_s1.name: server_s1,
        },
        segmentations={
            server_seg1.name: server_seg1,
        },
        windows={
            server_w1.name: server_w1,
        },
        filters={
            server_f1.name: server_f1,
            server_f2.name: server_f2,
        },
        validators={
            server_v1.name: server_v1,
            server_v2.name: server_v2,
        },
    )

    expected = create_graph_diff(
        to_delete=create_diff_context(
            filters={
                server_f2.name: server_f2,
            }
        )
    )

    _add_namespace(namespace, server_ctx)
    assert expected == _diff_resource_graph(namespace, manifest_ctx, server_ctx)
