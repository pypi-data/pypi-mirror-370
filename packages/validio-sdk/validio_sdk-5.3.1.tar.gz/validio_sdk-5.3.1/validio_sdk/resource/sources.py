"""Sources."""

import inspect
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, cast, get_args

# We need validio_sdk in scope due to eval.
# ruff: noqa: F401
import validio_sdk
from validio_sdk._api.api import infer_schema, sql_source_preview
from validio_sdk.client import Session
from validio_sdk.resource._diffable import Diffable
from validio_sdk.resource._errors import ManifestConfigurationError
from validio_sdk.resource._resource import Resource
from validio_sdk.resource._serde import (
    NODE_TYPE_FIELD_NAME,
    ImportValue,
    _api_create_input_params,
    _api_update_input_params,
    _encode_resource,
    _import_resource_params,
    get_children_node,
    get_config_node,
)
from validio_sdk.resource.credentials import (
    AwsAthenaCredential,
    AwsCredential,
    AwsRedshiftCredential,
    AzureSynapseCredential,
    ClickHouseCredential,
    Credential,
    DatabricksCredential,
    DemoCredential,
    GcpCredential,
    KafkaCredential,
    MsSqlServerCredential,
    OracleCredential,
    PostgreSqlCredential,
    SnowflakeCredential,
    WarehouseCredential,
)
from validio_sdk.resource.tags import Tag
from validio_sdk.scalars import JsonTypeDefinition

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext


class StreamingSourceMessageFormat(str, Enum):
    """Message format for streaming data."""

    AVRO = "AVRO"
    JSON = "JSON"
    PROTOBUF = "PROTOBUF"


class Source(Resource):
    """A source configuration.

    https://docs.validio.io/docs/sources
    """

    def __init__(
        self,
        name: str,
        credential: Credential,
        display_name: str | None,
        ignore_changes: bool = False,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the source
        :param credential: The credential to attach the source to
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param jtd_schema: The schema to associate the source with. If None is
            provided (default), then the schema will be automatically inferred.
            https://docs.validio.io/docs/source-configuration#4-schema
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            display_name=display_name,
            __internal__=credential._resource_graph,
            ignore_changes=ignore_changes,
        )

        self.description = description
        self.credential_name: str = credential.name
        self.jtd_schema = jtd_schema
        self.tag_names = [t.name for t in tags] if tags is not None else []

        # Ensure always sorted
        self.tag_names.sort()

        _sanitize_jtd_schema(self.jtd_schema)

        credential.add(self.name, self)

    def _immutable_fields(self) -> set[str]:
        return {"credential_name"}

    def _mutable_fields(self) -> set[str]:
        # Note: jtd_schema is a mutable field but is handled specially in the diff
        # process - since schemas can be managed automatically. So it's not listed
        # here
        return {
            *super()._mutable_fields(),
            *{"description", "tag_names"},
        }

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "Source"

    def _api_create_input(self, _namespace: str, ctx: "DiffContext") -> Any:
        return _api_create_input_params(
            self,
            skip_fields={"tagNames"},
            overrides={
                **self._api_input_overrides(),
                "credentialId": ctx.credentials[self.credential_name]._must_id(),
                "tagIds": [ctx.tags[name]._must_id() for name in self.tag_names],
            },
        )

    def _api_update_input(self, _namespace: str, ctx: "DiffContext") -> Any:
        return _api_update_input_params(
            self,
            skip_fields={"tagNames"},
            overrides={
                **self._api_input_overrides(),
                "tagIds": [ctx.tags[name]._must_id() for name in self.tag_names],
            },
        )

    def _api_input_overrides(self) -> dict[str, Any]:
        # We can't have `jtd_schema` as a mutable field because we diff it
        # before we resolve it so instead we just override it on the API input
        # when we know if it's from the manifest or resolved via API.
        return {"jtdSchema": self.jtd_schema}

    def _encode(self) -> dict[str, object]:
        # Drop a couple fields here since they are not part of the constructor
        # for when we deserialize back.
        return _encode_resource(self, skip_fields={"credential_name"})

    @staticmethod
    def _decode(
        ctx: "DiffContext",
        cls: type,
        obj: dict[str, dict[str, object]],
        credential: Credential,
    ) -> "Source":
        args = get_config_node(obj)

        names = cast(list[str], args["tag_names"])
        tags = [ctx.tags[name] for name in names]
        del args["tag_names"]

        source = cls(
            **cast(
                dict[str, object],
                {
                    **args,
                    "credential": credential,
                    "tags": tags,
                },
            )
        )

        children_obj = cast(dict[str, dict[str, object]], get_children_node(obj))
        Source._decode_filters(ctx, source, children_obj)
        Source._decode_segmentations(ctx, source, children_obj)
        Source._decode_windows(ctx, source, children_obj)
        Source._register_validators_to_decode(ctx, children_obj)

        return source

    @staticmethod
    def _decode_segmentations(
        ctx: "DiffContext", source: "Source", children_obj: dict[str, dict[str, object]]
    ) -> None:
        from validio_sdk.resource.segmentations import Segmentation

        segmentations_obj = cast(
            dict[str, dict[str, object]],
            children_obj.get(Segmentation.__name__, {}),
        )
        segmentations = {}
        for segmentation_name, value in segmentations_obj.items():
            segmentation = Segmentation._decode(ctx, value, source)
            segmentations[segmentation_name] = segmentation
            ctx.segmentations[segmentation_name] = segmentation

        if len(segmentations) > 0:
            source._children[Segmentation.__name__] = cast(
                dict[str, Resource], segmentations
            )

    @staticmethod
    def _decode_windows(
        ctx: "DiffContext", source: "Source", children_obj: dict[str, dict[str, object]]
    ) -> None:
        from validio_sdk.resource.windows import Window

        windows_obj = cast(
            dict[str, dict[str, object]],
            children_obj.get(Window.__name__, {}),
        )

        windows = {}
        for window_name, value in windows_obj.items():
            window = Window._decode(value, source)
            windows[window_name] = window
            ctx.windows[window_name] = window

        if len(windows) > 0:
            source._children[Window.__name__] = cast(dict[str, Resource], windows)

    @staticmethod
    def _decode_filters(
        ctx: "DiffContext", source: "Source", children_obj: dict[str, dict[str, object]]
    ) -> None:
        from validio_sdk.resource.filters import Filter

        filters_obj = cast(
            dict[str, dict[str, object]],
            children_obj.get(Filter.__name__, {}),
        )

        filters = {}
        for filter_name, value in filters_obj.items():
            filter_ = Filter._decode(value, source)
            filters[filter_name] = filter_
            ctx.filters[filter_name] = filter_

        if len(filters) > 0:
            source._children[Filter.__name__] = cast(dict[str, Resource], filters)

    @staticmethod
    def _register_validators_to_decode(
        ctx: "DiffContext", children_obj: dict[str, dict[str, Any]]
    ) -> None:
        """
        While we decode the graph, we can't resolve validators until all its
        dependencies have been resolved - potential dependencies of a validator
        are (reference sources). So the idea is that, we keep track of
        validators here. After we've done the pass through all other resources,
        we resolve validators separately.
        """
        from validio_sdk.resource.validators import Validator

        validators_obj = children_obj.get(Validator.__name__, {})
        for name, value in validators_obj.items():
            ctx.pending_validators_raw[name] = (
                eval(f"validio_sdk.resource.validators.{value[NODE_TYPE_FIELD_NAME]}"),
                value,
            )

    def _import_params(self) -> dict[str, ImportValue]:
        return _import_resource_params(
            resource=self,
            skip_fields={"jtd_schema"},
        )

    async def _api_infer_schema(
        self,
        credential: Credential,
        session: Session,
    ) -> None:
        class_name = self.__class__.__name__[: -len("Source")]
        api_input = self._api_infer_schema_input()
        response = await infer_schema(
            class_name=class_name,
            variable_values={
                **(api_input or {}),
                "credentialId": credential._must_id(),
            },
            no_args=isinstance(self, DemoSource),
            session=session,
        )

        self.jtd_schema = response
        _sanitize_jtd_schema(self.jtd_schema)

    @abstractmethod
    def _api_infer_schema_input(self) -> dict[str, object] | None:
        """
        Return the fields (as defined in the graphql ...InferSchemaInput as well
        as their values. The credential id is provided by the caller so that's
        ignored here. If None is returned (Demo), then the inference method is
        assumed to take no parameters (not even a credential id).
        """


def _sanitize_jtd_schema(jtd_schema: JsonTypeDefinition | None) -> None:
    # TODO VR-2073:
    # The jtd python lib for some reason wants this property to be a string
    # even though the spec and all other language libraries say it's a bool.
    if jtd_schema and "additionalProperties" in jtd_schema:
        del jtd_schema["additionalProperties"]


class DemoSource(Source):
    """A Demo source configuration."""

    def __init__(
        self,
        *,
        name: str,
        credential: DemoCredential,
        display_name: str | None = None,
        ignore_changes: bool = False,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return None

    def _api_update_input(self, namespace: str, ctx: "DiffContext") -> Any:
        input = super()._api_update_input(namespace, ctx)

        # The `DemoSource` is special in that it doesn't accept an update to the
        # JTD schema so we remove it from the update input.
        del input["input"]["jtdSchema"]

        return input


class WarehouseSource(Source):
    """Base class for warehouse sources."""


class DbtSource(WarehouseSource):
    """A base class source."""

    def __init__(
        self,
        *,
        name: str,
        credential: GcpCredential,
        project_name: str,
        job_name: str,
        schedule: str | None = "0/15 * * * *",
        display_name: str | None = None,
        ignore_changes: bool = False,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param project_name: The name of the dbt project.
        :param job_name: The name of the dbt job.
        :param schedule: A 5-digit cron expression specifying how when the source
            polls for new data. Example: '0 0 * * *' to poll daily at midnight.
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

        self.project_name = project_name
        self.job_name = job_name
        self.schedule = schedule

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "project_name",
                "job_name",
            },
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return None


class DbtModelRunSource(DbtSource):
    """A source for dbt model run results."""


class DbtTestResultSource(DbtSource):
    """A source for dbt test results."""


class GcpBigQuerySource(WarehouseSource):
    """A BigQuery source configuration.

    https://docs.validio.io/docs/bigquery
    """

    def __init__(
        self,
        *,
        name: str,
        credential: GcpCredential,
        project: str,
        dataset: str,
        table: str,
        schedule: str | None,
        lookback_days: int | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        cursor_field: str | None = None,
        description: str | None = None,
        jtd_schema: JsonTypeDefinition | None = None,
        billing_project: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param project: GCP project where the BigQuery instance resides.
        :param dataset: Dataset containing the configured table.
        :param table: Name of table to monitor.
        :param schedule: A 5-digit cron expression specifying how when the source
            polls for new data. Example: '0 0 * * *' to poll daily at midnight.
        :param lookback_days: How far back in time to start data monitoring
            from. (max 365) (deprecated)
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param cursor_field: Timestamp column specifying when each row in the table
            was added/updated.
            https://docs.validio.io/docs/data-warehouse#general-considerations
        :param description: Description of the resource.
        :param billing_project: GCP project id to use for billing and quota
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

        self.project = project
        self.dataset = dataset
        self.table = table
        self.cursor_field = cursor_field
        self.lookback_days = lookback_days
        self.schedule = schedule
        self.billing_project = billing_project

        if self.lookback_days is not None:
            self.add_deprecation(
                "Field lookback_days is deprecated on sources, please "
                "use the lookback field on tumbling windows instead."
            )

        if self.cursor_field is not None:
            self.add_deprecation(
                "Field cursor_field is deprecated on warehouse sources. Instead use "
                "the field data_time_field on windows."
            )

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "project",
                "dataset",
                "table",
                "cursor_field",
            },
        }

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "lookback_days",
                "schedule",
                "billing_project",
            },
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            "dataset": self.dataset,
            "project": self.project,
            "table": self.table,
        }


class SnowflakeSource(WarehouseSource):
    """
    A Snowflake source configuration.

    https://docs.validio.io/docs/snowflake
    """

    def __init__(
        self,
        *,
        name: str,
        credential: SnowflakeCredential,
        database: str,
        table: str,
        schedule: str | None,
        schema: str,
        lookback_days: int | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        cursor_field: str | None = None,
        warehouse: str | None = None,
        role: str | None = None,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param database: Name of the snowflake database to connect to
        :param table: Name of table to monitor
        :param warehouse: Snowflake virtual warehouse to use to run queries
        :param role: Snowflake role to assume when running queries
        :param schedule: A 5-digit cron expression specifying how when the source
            polls for new data. Example: '0 0 * * *' to poll daily at midnight.
        :param schema: Name of the schema in the database that contains the
            table to monitor
        :param lookback_days: How far back in time to start data ingestion
            from. (max 365) (deprecated)
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param cursor_field: Timestamp column specifying when each row in the table
            was added/updated
            https://docs.validio.io/docs/data-warehouse#general-considerations
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

        self.database = database
        self.schema = schema
        self.table = table
        self.warehouse = warehouse
        self.role = role
        self.cursor_field = cursor_field
        self.lookback_days = lookback_days
        self.schedule = schedule

        if self.lookback_days is not None:
            self.add_deprecation(
                "Field lookback_days is deprecated on sources, please "
                "use the lookback field on tumbling windows instead."
            )

        if self.cursor_field is not None:
            self.add_deprecation(
                "Field cursor_field is deprecated on warehouse sources. Instead use "
                "the field data_time_field on windows."
            )

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "schema",
                "database",
                "table",
                "cursor_field",
            },
        }

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "lookback_days",
                "role",
                "schedule",
                "warehouse",
            },
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            "database": self.database,
            "schema": self.schema,
            "table": self.table,
            "role": self.role,
            "warehouse": self.warehouse,
        }


class PostgresLikeSource(WarehouseSource):
    """A Postgres compatible source configuration."""

    def __init__(
        self,
        *,
        name: str,
        credential: PostgreSqlCredential | AwsRedshiftCredential,
        database: str | None,
        table: str,
        schedule: str | None,
        schema: str,
        lookback_days: int | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        cursor_field: str | None = None,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param table: Name of table to monitor.
        :param database: Name of the database containing the specified schema. If none
            is provided, the `default_database` of the provided credential is used.
        :param schedule: A 5-digit cron expression specifying how when the source
            polls for new data. Example: '0 0 * * *' to poll daily at midnight.
        :param schema: Name of the schema in the database that contains the table.
        :param lookback_days: How far back in time to start data ingestion
            from. (max 365) (deprecated)
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param cursor_field: Timestamp column specifying when each row in the table
            was added/updated.
            https://docs.validio.io/docs/data-warehouse#general-considerations
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

        self.schema = schema
        self.table = table
        self.database = database
        self.cursor_field = cursor_field
        self.lookback_days = lookback_days
        self.schedule = schedule

        if self.lookback_days is not None:
            self.add_deprecation(
                "Field lookback_days is deprecated on sources, please "
                "use the lookback field on tumbling windows instead."
            )

        if self.cursor_field is not None:
            self.add_deprecation(
                "Field cursor_field is deprecated on warehouse sources. Instead use "
                "the field data_time_field on windows."
            )

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "schema",
                "database",
                "table",
                "cursor_field",
            },
        }

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "lookback_days",
                "schedule",
            },
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            "database": self.database,
            "schema": self.schema,
            "table": self.table,
        }


class PostgreSqlSource(PostgresLikeSource):
    """A PostgreSql source configuration.

    https://docs.validio.io/docs/postgresql
    """


class AwsRedshiftSource(PostgresLikeSource):
    """A Redshift source configuration.

    https://docs.validio.io/docs/redshift
    """


class AwsAthenaSource(WarehouseSource):
    """
    An AWS Athena source configuration.

    https://docs.validio.io/docs/athena
    """

    def __init__(
        self,
        *,
        name: str,
        credential: AwsAthenaCredential,
        catalog: str,
        database: str,
        table: str,
        schedule: str | None,
        lookback_days: int | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        cursor_field: str | None = None,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param catalog: Name of the Athena catalog to connect to
        :param database: Name of the database in the catalog
        :param table: Name of table to monitor
        :param schedule: A 5-digit cron expression specifying how when the source
            polls for new data. Example: '0 0 * * *' to poll daily at midnight.
        :param lookback_days: How far back in time to start data ingestion
            from. (max 365) (deprecated)
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param cursor_field: Timestamp column specifying when each row in the table
            was added/updated
            https://docs.validio.io/docs/data-warehouse#general-considerations
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

        self.catalog = catalog
        self.database = database
        self.table = table
        self.cursor_field = cursor_field
        self.lookback_days = lookback_days
        self.schedule = schedule

        if self.lookback_days is not None:
            self.add_deprecation(
                "Field lookback_days is deprecated on sources, please "
                "use the lookback field on tumbling windows instead."
            )

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "catalog",
                "database",
                "table",
                "cursor_field",
            },
        }

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "lookback_days",
                "schedule",
            },
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            "catalog": self.catalog,
            "database": self.database,
            "table": self.table,
        }


class DatabricksSource(WarehouseSource):
    """
    A Databricks source configuration.

    https://docs.validio.io/docs/databricks
    """

    def __init__(
        self,
        *,
        name: str,
        credential: DatabricksCredential,
        catalog: str,
        table: str,
        schedule: str | None,
        schema: str,
        lookback_days: int | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        cursor_field: str | None = None,
        http_path: str | None = None,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param catalog: Name of the Databricks catalog to connect to
        :param table: Name of table to monitor
        :param schedule: A 5-digit cron expression specifying how when the source
            polls for new data. Example: '0 0 * * *' to poll daily at midnight.
        :param schema: Name of the schema in the catalog
        :param lookback_days: How far back in time to start data ingestion
            from. (max 365) (deprecated)
        :param cursor_field: Timestamp column specifying when each row in the table
            was added/updated
            https://docs.validio.io/docs/data-warehouse#general-considerations
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param http_path: Overrides the connection path of the compute resource to use.
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

        self.catalog = catalog
        self.schema = schema
        self.table = table
        self.cursor_field = cursor_field
        self.lookback_days = lookback_days
        self.schedule = schedule
        self.http_path = http_path

        if self.lookback_days is not None:
            self.add_deprecation(
                "Field lookback_days is deprecated on sources, please "
                "use the lookback field on tumbling windows instead."
            )

        if self.cursor_field is not None:
            self.add_deprecation(
                "Field cursor_field is deprecated on warehouse sources. Instead use "
                "the field data_time_field on windows."
            )

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "catalog",
                "schema",
                "table",
                "cursor_field",
            },
        }

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"lookback_days", "schedule", "http_path"},
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            "catalog": self.catalog,
            "schema": self.schema,
            "table": self.table,
        }


class AzureSynapseSource(WarehouseSource):
    """
    A Azure Synapse source configuration.

    https://docs.validio.io/docs/azure-synapse
    """

    def __init__(
        self,
        *,
        name: str,
        credential: AzureSynapseCredential,
        database: str,
        table: str,
        schedule: str | None,
        schema: str,
        lookback_days: int | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        cursor_field: str | None = None,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param database: Name of the Azure Synapse database to connect to
        :param table: Name of table to monitor
        :param schedule: A 5-digit cron expression specifying how when the source
            polls for new data. Example: '0 0 * * *' to poll daily at midnight.
        :param schema: Name of the schema in the database
        :param lookback_days: How far back in time to start data ingestion
            from. (max 365) (deprecated)
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param cursor_field: Timestamp column specifying when each row in the table
            was added/updated
            https://docs.validio.io/docs/data-warehouse#general-considerations
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

        self.database = database
        self.schema = schema
        self.table = table
        self.cursor_field = cursor_field
        self.lookback_days = lookback_days
        self.schedule = schedule

        if self.lookback_days is not None:
            self.add_deprecation(
                "Field lookback_days is deprecated on sources, please "
                "use the lookback field on tumbling windows instead."
            )

        if self.cursor_field is not None:
            self.add_deprecation(
                "Field cursor_field is deprecated on warehouse sources. Instead use "
                "the field data_time_field on windows."
            )

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "database",
                "schema",
                "table",
                "cursor_field",
            },
        }

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "lookback_days",
                "schedule",
            },
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            "database": self.database,
            "schema": self.schema,
            "table": self.table,
        }


class ClickHouseSource(WarehouseSource):
    """
    A ClickHouse source configuration.

    https://docs.validio.io/docs/clickhouse
    """

    def __init__(
        self,
        *,
        name: str,
        credential: ClickHouseCredential,
        database: str,
        table: str,
        schedule: str | None,
        lookback_days: int | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        cursor_field: str | None = None,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param database: Name of the ClickHouse databse to connect to
        :param table: Name of table to monitor
        :param schedule: A 5-digit cron expression specifying how when the source
            polls for new data. Example: '0 0 * * *' to poll daily at midnight.
        :param lookback_days: How far back in time to start data ingestion
            from. (max 365) (deprecated)
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param cursor_field: Timestamp column specifying when each row in the table
            was added/updated
            https://docs.validio.io/docs/data-warehouse#general-considerations
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

        self.database = database
        self.table = table
        self.cursor_field = cursor_field
        self.lookback_days = lookback_days
        self.schedule = schedule

        if self.lookback_days is not None:
            self.add_deprecation(
                "Field lookback_days is deprecated on sources, please "
                "use the lookback field on tumbling windows instead."
            )

        if self.cursor_field is not None:
            self.add_deprecation(
                "Field cursor_field is deprecated on warehouse sources. Instead use "
                "the field data_time_field on windows."
            )

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "database",
                "table",
                "cursor_field",
            },
        }

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "lookback_days",
                "schedule",
            },
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            "database": self.database,
            "table": self.table,
        }


class SqlSource(WarehouseSource):
    """A Sql source configuration."""

    def __init__(
        self,
        *,
        name: str,
        credential: WarehouseCredential,
        sql_query: str,
        schedule: str | None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the source.
        :param credential: Credential used to connect to the source.
        :param sql_query: The SQL query to use as data source.
        :param schedule: A 5-digit cron expression specifying how when the source
            polls for new data. Example: '0 0 * * *' to poll daily at midnight.
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

        if not isinstance(credential, get_args(WarehouseCredential)):
            allowed = "\n * ".join([x.__name__ for x in get_args(WarehouseCredential)])
            raise ManifestConfigurationError(
                f'Invalid credential type for SQL source "{name}".\n\n'
                f"Supported credential types:\n\n * {allowed}"
            )

        self.sql_query = sql_query
        self.schedule = schedule

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "sql_query",
                "schedule",
            },
        }

    async def _api_infer_schema(self, credential: Credential, session: Session) -> None:
        response = await sql_source_preview(
            session=session,
            credential_id=credential._must_id(),
            sql_query=self.sql_query,
            dry_run=False,
            source_name=self.name,
        )

        self.jtd_schema = response["jtdSchema"]
        _sanitize_jtd_schema(self.jtd_schema)

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        # Not used since we do custom inference for sql source
        return None


class MsSqlServerSource(Source):
    """A Microsoft Sql Server source configuration."""

    def __init__(
        self,
        name: str,
        credential: MsSqlServerCredential,
        database: str,
        schema: str,
        table: str,
        schedule: str | None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param database: Name of the database to connect to.
        :param schema: Name of the schema in the database.
        :param table: Name of table to monitor.
        :param schedule: A 5-digit cron expression specifying how when the source
            polls for new data. Example: '0 0 * * *' to poll daily at midnight.
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )
        self.database = database
        self.schema = schema
        self.table = table
        self.schedule = schedule

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "database",
                "schema",
                "table",
            },
        }

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"schedule"},
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            "database": self.database,
            "schema": self.schema,
            "table": self.table,
        }


class OracleSource(Source):
    """An Oracle source configuration."""

    def __init__(
        self,
        name: str,
        credential: OracleCredential,
        database: str,
        schema: str,
        table: str,
        schedule: str | None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        jtd_schema: JsonTypeDefinition | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param database: Name of the database to connect to.
        :param schema: Name of the schema in the database.
        :param table: Name of table to monitor.
        :param schedule: A 5-digit cron expression specifying how when the source
            polls for new data. Example: '0 0 * * *' to poll daily at midnight.
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

        self.database = database
        self.schema = schema
        self.table = table
        self.schedule = schedule

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "database",
                "schema",
                "table",
            },
        }

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"schedule"},
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            "database": self.database,
            "schema": self.schema,
            "table": self.table,
        }


# Streaming


class StreamingMessageFormat(Diffable):
    """Message format configuration for a streaming source."""

    def __init__(
        self,
        format: (
            StreamingSourceMessageFormat | None
        ) = StreamingSourceMessageFormat.JSON,
        schema: str | None = None,
    ):
        """
        Constructor.

        :param format: Specifies the format of messages in the stream
        :param schema: Schema of messages in the stream
        """
        self.format = format
        self.schema = schema

    @staticmethod
    def _from_any(other: Any) -> "StreamingMessageFormat":
        if isinstance(other, StreamingMessageFormat):
            return other
        if isinstance(other, dict):
            return StreamingMessageFormat(**other)

        params = {
            f: getattr(other, f)
            for f in list(inspect.signature(StreamingMessageFormat).parameters)
        }
        return StreamingMessageFormat(**params)

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            "format",
            "schema",
        }

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        return {}

    def _encode(self) -> dict[str, object]:
        return self.__dict__


class StreamSource(Source):
    """Base class for streaming sources."""

    def __init__(
        self,
        name: str,
        credential: Credential,
        display_name: str | None,
        ignore_changes: bool = False,
        jtd_schema: JsonTypeDefinition | None = None,
        message_format: StreamingMessageFormat | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """Constructor."""
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            description=description,
            tags=tags,
        )

        self.message_format = (
            StreamingMessageFormat()
            if message_format is None
            else StreamingMessageFormat._from_any(message_format)
        )

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        return {
            "message_format": self.message_format,
        }

    def _message_format_input(self) -> dict[str, Any]:
        return {
            "format": self.message_format.format,
            "schema": self.message_format.schema,
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            **(super()._api_infer_schema_input() or {}),  # type: ignore[safe-super]
            "messageFormat": self._message_format_input(),
        }

    def _api_input_overrides(self) -> dict[str, Any]:
        return {
            **super()._api_input_overrides(),
            "messageFormat": self._message_format_input(),
        }


class AwsKinesisSource(StreamSource):
    """
    A Kinesis source configuration.

    https://docs.validio.io/docs/kinesis
    """

    def __init__(
        self,
        *,
        name: str,
        credential: AwsCredential,
        region: str,
        stream_name: str,
        display_name: str | None = None,
        ignore_changes: bool = False,
        jtd_schema: JsonTypeDefinition | None = None,
        message_format: StreamingMessageFormat | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param region: AWS region where the Kinesis stream resides.
        :param stream_name: The Kinesis stream to monitor.
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param message_format: The format of messages in the stream.
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            message_format=message_format,
            description=description,
            tags=tags,
        )

        self.region = region
        self.stream_name = stream_name

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "region",
                "stream_name",
            },
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            **(super()._api_infer_schema_input() or {}),
            "region": self.region,
            "stream_name": self.stream_name,
        }


class GcpPubSubSource(StreamSource, ABC):
    """A PubSub source configuration."""

    def __init__(
        self,
        *,
        name: str,
        credential: GcpCredential,
        project: str,
        subscription_id: str,
        display_name: str | None = None,
        ignore_changes: bool = False,
        jtd_schema: JsonTypeDefinition | None = None,
        message_format: StreamingMessageFormat | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param project: The GCP project where the pubsub topic resides.
        :param subscription_id: The subscription ID of the subscription
            to use to consumer messages from the topic.
            https://cloud.google.com/pubsub/docs/create-subscription
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param message_format: The format of messages in the stream.
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            message_format=message_format,
            description=description,
            tags=tags,
        )

        self.project = project
        self.subscription_id = subscription_id

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{
                "project",
                "subscription_id",
            },
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            **(super()._api_infer_schema_input() or {}),
            "project": self.project,
            "subscription_id": self.subscription_id,
        }


class KafkaSource(StreamSource):
    """
    A Kafka source configuration.

    https://docs.validio.io/docs/kafka
    """

    def __init__(
        self,
        *,
        name: str,
        credential: KafkaCredential,
        topic: str,
        display_name: str | None = None,
        ignore_changes: bool = False,
        jtd_schema: JsonTypeDefinition | None = None,
        message_format: StreamingMessageFormat | None = None,
        description: str | None = None,
        tags: list[Tag] | None = None,
    ):
        """
        Constructor.

        :param topic: Topic to read data from.
        :param display_name: Human-readable name for the source. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param message_format: The format of messages in the stream.
        :param description: Description of the resource.
        :param tags: Tags to add to the resource
        """
        super().__init__(
            name=name,
            credential=credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            jtd_schema=jtd_schema,
            message_format=message_format,
            description=description,
            tags=tags,
        )

        self.topic = topic

    def _immutable_fields(self) -> set[str]:
        return {
            *super()._immutable_fields(),
            *{"topic"},
        }

    def _api_infer_schema_input(self) -> dict[str, object] | None:
        return {
            **(super()._api_infer_schema_input() or {}),
            "topic": self.topic,
        }
