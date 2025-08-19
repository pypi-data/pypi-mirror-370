"""Credentials configuration."""

from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from camel_converter import to_camel

from validio_sdk._api.api import APIClient, test_credential
from validio_sdk.client.client import Session
from validio_sdk.resource._resource import (
    ApiSecretChangeNestedResource,
    Resource,
    ResourceGraph,
)
from validio_sdk.resource._resource_graph import RESOURCE_GRAPH
from validio_sdk.resource._serde import (
    NODE_TYPE_FIELD_NAME,
    ImportValue,
    _api_create_input_params,
    _api_update_input_params,
    _encode_resource,
    _import_resource_params,
    decode_nested_objects,
    get_children_node,
    get_config_node,
    with_resource_graph_info,
)

if TYPE_CHECKING:
    from validio_sdk.resource._diff import DiffContext
    from validio_sdk.resource._diffable import Diffable


class AzureSynapseBackendType(str, Enum):
    """Backend type used for Azure Synapse."""

    DEDICATED_SQL_POOL = "DEDICATED_SQL_POOL"
    SERVERLESS_SQL_POOL = "SERVERLESS_SQL_POOL"


class ClickHouseProtocol(str, Enum):
    """ClickHouse protocol."""

    HTTP = "HTTP"
    HTTPS = "HTTPS"
    NATIVE = "NATIVE"
    NATIVE_TLS = "NATIVE_TLS"


class Credential(Resource):
    """
    Base class for a credential resource.

    https://docs.validio.io/docs/credentials
    """

    def __init__(
        self,
        name: str,
        display_name: str | None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ) -> None:
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param __internal__: Should be left ignored. This is for internal usage only.
        """
        # Credentials are at the root sub-graphs.
        g: ResourceGraph = __internal__ or RESOURCE_GRAPH
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=g,
        )

        self._resource_graph: ResourceGraph = g
        self._resource_graph._add_root(self)

    @abstractmethod
    def _immutable_fields(self) -> set[str]:
        pass

    def _all_fields(self) -> set[str]:
        return {
            *super()._all_fields(),
            *self._secret_fields(),
        }

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "Credential"

    def _encode(self) -> dict[str, object]:
        return _encode_resource(self)

    @staticmethod
    def _decode(
        ctx: "DiffContext",
        cls: type,
        obj: dict[str, dict[str, object]],
        g: ResourceGraph,
    ) -> "Credential":
        from validio_sdk.resource.sources import Source

        args: dict[str, Any] = get_config_node(obj)

        decode_nested_objects(
            obj=args,
            cls_eval=lambda cls_name: eval(cls_name),
        )

        # Some credentials wrap other credentials and if so they have a field
        # set with the name of the other credential. For those we need to pop
        # the name from the config field names and instead ensure we have
        # `warehouse_credential` set to the full object.
        warehouse_credential_name = args.pop("warehouse_credential_name", None)
        if warehouse_credential_name:
            args["warehouse_credential"] = ctx.credentials[warehouse_credential_name]

        credential = cls(**with_resource_graph_info(args, g))
        children_obj = cast(
            dict[str, dict[str, dict[str, Any]]], get_children_node(obj)
        )

        Credential._decode_children(ctx, children_obj, credential, Source, "sources")

        return credential

    @staticmethod
    def _decode_children(
        ctx: "DiffContext",
        children_obj: dict[str, dict[str, dict[str, object]]],
        credential: "Credential",
        resource_cls: type,
        resource_module: str,
    ) -> None:
        # We need to import the validio_sdk module due to the `eval`
        # ruff: noqa: F401
        import validio_sdk

        resources_obj = children_obj.get(resource_cls.__name__, {})
        resources = {}
        for resource_name, value in resources_obj.items():
            cls = eval(
                f"validio_sdk.resource.{resource_module}.{value[NODE_TYPE_FIELD_NAME]}"
            )
            r = cast(Any, resource_cls)._decode(ctx, cls, value, credential)
            resources[resource_name] = r
            ctx.__getattribute__(resource_module)[resource_name] = r

        if len(resources) > 0:
            credential._children[resource_cls.__name__] = resources

    def _import_params(self) -> dict[str, ImportValue]:
        # We always skip all fields suffixe with `_name` if they're a part of
        # our `DiffContext`. Since `warehouse_credential_name` is not a child
        # resource this is also not a part of the context. Instead we'll
        # manually have to skip this field.
        skip_fields = {"warehouse_credential_name"}

        return {
            **_import_resource_params(resource=self, skip_fields=skip_fields),
        }

    def _api_create_input(self, namespace: str, _: "DiffContext") -> Any:
        overrides = {
            "namespaceId": namespace,
            **{
                to_camel(f): obj._api_input()
                for f, obj in self._nested_secret_objects().items()
            },
        }
        return _api_create_input_params(self, overrides=overrides)

    def _api_update_input(self, _namespace: str, _: "DiffContext") -> Any:
        overrides = {
            **{
                to_camel(f): obj._api_input()
                for f, obj in self._nested_secret_objects().items()
            }
        }
        return _api_update_input_params(self, overrides=overrides)

    def _api_test_credential_input(
        self, namespace: str, ctx: "DiffContext"
    ) -> dict[str, Any] | None:
        class_name = self.__class__.__name__

        # Lowercase first and drop the `Credential` suffix.
        variant = (
            class_name[0].lower() + class_name[1 : len(class_name) - len("Credential")]
        )

        test_input = self._api_test_credential_input_params(namespace, ctx)

        return {"input": {variant: test_input}}

    def _api_test_credential_input_params(
        self,
        namespace: str,
        ctx: "DiffContext",
        overrides: dict[str, Any] | None = None,
        skip_fields: set[str] | None = None,
    ) -> dict[str, Any]:
        overrides = overrides or {}
        skip_fields = skip_fields or set()

        skip_fields = {
            "displayName",
            "enableCatalog",
            "name",
            "namespaceId",
            "resourceName",
            *skip_fields,
        }

        create_input = self._api_create_input(namespace, ctx)["input"]
        test_input = {}

        for k, v in create_input.items():
            if k in skip_fields:
                continue

            if k in overrides:
                test_input[k] = overrides[k]
            else:
                test_input[k] = v

        return test_input


class AtlanCredential(Credential):
    """(BETA) An Atlan credential resource."""

    def __init__(
        self,
        *,
        name: str,
        application_link_url: str,
        base_url: str,
        api_token: str,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param application_link_url: URL to your Validio application
        :param base_url: URL to the Atlan instance, e.g. https://tenant.atlan.com
        :param api_token: The API token used to authenticate to Atlan
        :param display_name: Human-readable name for the credential. This name is
            visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )

        self.application_link_url = application_link_url
        self.base_url = base_url
        self.api_token = api_token

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"application_link_url", "base_url"},
        }

    def _secret_fields(self) -> set[str]:
        return {"api_token"}

    def _api_test_credential_input_params(
        self,
        namespace: str,
        ctx: "DiffContext",
        overrides: dict[str, Any] | None = None,
        skip_fields: set[str] | None = None,
    ) -> dict[str, Any]:
        skip_fields = skip_fields or set()

        return super()._api_test_credential_input_params(
            namespace,
            ctx,
            overrides,
            {
                *skip_fields,
                "applicationLinkUrl",
            },
        )


class DemoCredential(Credential):
    """A demo credential resource."""

    def __init__(
        self,
        *,
        name: str,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _secret_fields(self) -> set[str]:
        return set()

    def _api_test_credential_input(
        self, _namespace: str, _ctx: "DiffContext"
    ) -> dict[str, Any] | None:
        # There's nothing to test for demo credentials so by returning None we
        # bypass credential checking.
        return None


class DbtCredential(Credential):
    """A dbt base class credential."""

    def __init__(
        self,
        *,
        name: str,
        warehouse_credential: "Credential",
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param warehouse_credential: A credential that has access to the
        resources
        :param display_name: Human readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.warehouse_credential_name = warehouse_credential.name

    def _immutable_fields(self) -> set[str]:
        return set()

    def _secret_fields(self) -> set[str]:
        return set()

    def _api_create_input(self, namespace: str, ctx: "DiffContext") -> Any:
        return _api_create_input_params(
            self,
            skip_fields={"warehouseCredentialName"},
            overrides={
                "namespaceId": namespace,
                "warehouseCredentialId": ctx.credentials[
                    self.warehouse_credential_name
                ]._must_id(),
            },
        )

    def _api_update_input(self, _namespace: str, ctx: "DiffContext") -> Any:
        return _api_update_input_params(
            self,
            skip_fields={"warehouseCredentialName"},
            overrides={
                "warehouseCredentialId": ctx.credentials[
                    self.warehouse_credential_name
                ]._must_id(),
            },
        )


class DbtCoreCredential(DbtCredential):
    """A dbt core credential."""

    def __init__(
        self,
        *,
        name: str,
        warehouse_credential: "Credential",
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param warehouse_credential: A credential that has access to the
        resources
        :param display_name: Human readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            warehouse_credential=warehouse_credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"warehouse_credential_name"},
        }


class DbtCloudCredential(DbtCredential):
    """A dbt cloud credential."""

    def __init__(
        self,
        *,
        name: str,
        warehouse_credential: "Credential",
        account_id: str,
        token: str,
        api_base_url: str | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param warehouse_credential: A credential that has access to the
        resources
        :param account_id: dbt cloud account id
        :param api_base_url: Base URL to access the dbt cloud instance
        :param display_name: Human readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            warehouse_credential=warehouse_credential,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.account_id = account_id
        self.api_base_url = api_base_url
        self.token = token

    def _secret_fields(self) -> set[str]:
        return {"token"}

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"account_id", "api_base_url", "warehouse_credential_name"},
        }


class GcpCredential(Credential):
    """
    A credential resource that can be used to authenticate against
    Google Cloud Platform services.
    """

    def __init__(
        self,
        *,
        name: str,
        credential: str,
        billing_project: str | None = None,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param credential: Service account JSON credential
        :param billing_project: GCP project id to use for billing and quota
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.credential = credential
        self.enable_catalog = enable_catalog
        self.billing_project = billing_project

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {*super()._mutable_fields(), *{"enable_catalog", "billing_project"}}

    def _secret_fields(self) -> set[str]:
        return {"credential"}

    def _api_test_credential_input_params(
        self,
        namespace: str,
        ctx: "DiffContext",
        overrides: dict[str, Any] | None = None,
        skip_fields: set[str] | None = None,
    ) -> dict[str, Any]:
        skip_fields = skip_fields or set()

        return super()._api_test_credential_input_params(
            namespace,
            ctx,
            overrides,
            {
                *skip_fields,
                "billingProject",
            },
        )


class AwsCredential(Credential):
    """A credential resource that can be used to authenticate against AWS services."""

    def __init__(
        self,
        *,
        name: str,
        access_key: str,
        secret_key: str,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param access_key: Access key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        :param secret_key: Secret key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.access_key = access_key
        self.secret_key = secret_key
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"access_key", "enable_catalog"},
        }

    def _secret_fields(self) -> set[str]:
        return {"secret_key"}


class SnowflakeCredentialKeyPair(ApiSecretChangeNestedResource):
    """
    Snowflake key-pair based authentication.

    https://docs.snowflake.com/en/user-guide/key-pair-auth
    """

    def __init__(
        self,
        *,
        user: str,
        private_key: str,
        private_key_passphrase: str | None = None,
    ):
        """
        Constructor.

        :param user: Snowflake username.
        :param private_key: Plain or encrypted pem encoded private key.
        :param private_key_passphrase: Passphrase for encrypted private key.
        """
        self.user = user
        self.private_key = private_key
        self.private_key_passphrase = private_key_passphrase

    def _api_variant_name(self) -> str:
        return "keyPair"

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"user"}

    def _secret_fields(self) -> set[str]:
        return {"private_key", "private_key_passphrase"}

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {}


class SnowflakeCredentialUserPassword(ApiSecretChangeNestedResource):
    """Snowflake password-based authentication."""

    def __init__(
        self,
        *,
        user: str,
        password: str,
    ):
        """
        Constructor.

        :param user: Snowflake username.
        :param password: Snowflake password.
        """
        self.user = user
        self.password = password

    def _api_variant_name(self) -> str:
        return "userPassword"

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"user"}

    def _secret_fields(self) -> set[str]:
        return {"password"}

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {}


SnowflakeCredentialAuth = Union[
    SnowflakeCredentialKeyPair, SnowflakeCredentialUserPassword
]


class SnowflakeCredential(Credential):
    """A credential resource that can be used to connect to a Snowflake table."""

    def __init__(
        self,
        *,
        name: str,
        account: str,
        auth: SnowflakeCredentialAuth,
        warehouse: str | None = None,
        role: str | None = None,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param account: Snowflake account identifier.
        :param auth: Credentials to use for authentication.
        :param warehouse: Snowflake virtual warehouse to use to run queries.
        :param role: Snowflake role to assume when running queries.
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.account = account
        self.auth = auth
        self.warehouse = warehouse
        self.role = role
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"account", "warehouse", "role", "enable_catalog"},
        }

    def _secret_fields(self) -> set[str]:
        return set()

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {"auth": self.auth}


class PostgresLikeCredential(Credential):
    """
    A credential resource that can be used to connect to
    a Postgres-compatible table.
    """

    def __init__(
        self,
        *,
        name: str,
        host: str,
        port: int,
        user: str,
        password: str,
        default_database: str,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param host: DNS hostname or IP address at which to reach the database server.
        :param port: Port number of the database server.
        :param user: Username having read access to the desired table.
        :param password: Password of the specified user.
        :param default_database: Name of the default database to use this
            credential with. This can be overridden e.g. in a Source configuration.
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.default_database = default_database
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"host", "port", "user", "default_database", "enable_catalog"},
        }

    def _secret_fields(self) -> set[str]:
        return {"password"}


class PostgreSqlCredential(PostgresLikeCredential):
    """
    A credential resource that can be used to connect to a Postgres table.

    https://docs.validio.io/docs/postgresql
    """


class AwsRedshiftCredential(PostgresLikeCredential):
    """
    A credential resource that can be used to connect to a Redshift table.

    https://docs.validio.io/docs/redshift
    """


class AwsAthenaCredential(Credential):
    """Athena credential resource."""

    def __init__(
        self,
        *,
        name: str,
        access_key: str,
        secret_key: str,
        region: str,
        query_result_location: str,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param access_key: Access key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        :param secret_key: Secret key for the IAM user
            https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html
        :param region: Region where the Athena service resides. e.g. eu-central-1
        :param query_result_location: S3 bucket to store query results
            e.g s3://myathenabucket/results
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.query_result_location = query_result_location
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"access_key", "region", "query_result_location", "enable_catalog"},
        }

    def _secret_fields(self) -> set[str]:
        return {"secret_key"}


class KafkaSslCredential(Credential):
    """
    A Kafka TLS credential.

    Security protocol: SSL

    https://docs.validio.io/docs/kafka#authentication-methods-for-source-config
    """

    def __init__(
        self,
        *,
        name: str,
        bootstrap_servers: list[str],
        ca_certificate: str,
        client_certificate: str,
        client_private_key: str,
        client_private_key_password: str,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param bootstrap_servers: List of Kafka server addresses to connect to.
            example: ['localhost:9092']
        :param ca_certificate: Certificate of the Certificate authority (CA)
            in CRT format.
        :param client_certificate: Client SSL certificate in PEM format.
        :param client_private_key: Client private key certificate in PEM format.
        :param client_private_key_password: Password or passphrase of
            client_private_key.
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.bootstrap_servers = bootstrap_servers
        self.ca_certificate = ca_certificate
        self.client_certificate = client_certificate
        self.client_private_key = client_private_key
        self.client_private_key_password = client_private_key_password
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"bootstrap_servers", "enable_catalog"},
        }

    def _secret_fields(self) -> set[str]:
        return {
            "ca_certificate",
            "client_certificate",
            "client_private_key",
            "client_private_key_password",
        }


class KafkaSaslSslPlainCredential(Credential):
    """
    A Kafka SASL SSL credential.

    Security protocol: SASL_SSL
    Sasl mechanism: PLAIN

    https://docs.validio.io/docs/kafka#authentication-methods-for-source-config
    """

    def __init__(
        self,
        *,
        name: str,
        bootstrap_servers: list[str],
        username: str,
        password: str,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        ca_certificate: str | None = None,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param bootstrap_servers: List of Kafka server addresses to connect to.
            example: ['localhost:9092']
        :param username: Username for the credential
        :param password: Password for the credential
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param ca_certificate: Deprecated
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.bootstrap_servers = bootstrap_servers
        self.username = username
        self.password = password
        self.enable_catalog = enable_catalog
        self.ca_certificate = ca_certificate

        if ca_certificate:
            self.add_field_deprecation("ca_certificate")

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"username", "bootstrap_servers", "enable_catalog", "ca_certificate"},
        }

    def _secret_fields(self) -> set[str]:
        return {"password"}


KafkaCredential = Union[KafkaSslCredential, KafkaSaslSslPlainCredential]


class LookerCredential(Credential):
    """A credential resource that can be used to connect to Looker."""

    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        client_id: str,
        client_secret: str,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param base_url: Address to the Looker instance
        :param client_id: Looker credential client id
        :param client_secret: Looker credential client secret
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"base_url", "client_id", "enable_catalog"},
        }

    def _secret_fields(self) -> set[str]:
        return {"client_secret"}


class DatabricksCredential(Credential):
    """A credential resource that can be used to connect to a Databricks table."""

    def __init__(
        self,
        *,
        name: str,
        host: str,
        port: int,
        access_token: str,
        http_path: str,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param host: A host of Databricks deployment
        :param port: A port of Databricks deployment
        :param access_token: An access token of system principal or a user
        :param http_path: Connection path of the compute resource to use.
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.host = host
        self.port = port
        self.access_token = access_token
        self.http_path = http_path
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"host", "port", "http_path", "enable_catalog"},
        }

    def _secret_fields(self) -> set[str]:
        return {"access_token"}


class AzureSynapseCredential(Credential):
    """A base class of Azure Credential resource."""

    def __init__(
        self,
        *,
        name: str,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ) -> None:
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        :param __internal__: Should be left ignored. This is for internal usage only.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )


class AzureSynapseEntraIdCredential(AzureSynapseCredential):
    """An Entra ID credential resource that can be used
    to connect to an Azure Synapse table.
    """

    def __init__(
        self,
        *,
        name: str,
        host: str,
        port: int,
        backend_type: AzureSynapseBackendType,
        client_id: str,
        client_secret: str,
        database: str | None = None,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param host: A host of Azure Synapse deployment
        :param port: A port of Azure Synapse deployment
        :param backend_type: Backend type used for Azure Synapse
        :param client_id: Application (client) ID of Azure system account.
        :param client_secret: Client secret value of Azure system account.
        :param database: Name of the database to connect to
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )

        self.host = host
        self.port = port
        self.backend_type = backend_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.database = database
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "host",
                "port",
                "client_id",
                "database",
                "backend_type",
                "enable_catalog",
            },
        }

    def _secret_fields(self) -> set[str]:
        return {"client_secret"}


class AzureSynapseSqlCredential(AzureSynapseCredential):
    """A Sql credential resource that can be used
    to connect to an Azure Synapse table.
    """

    def __init__(
        self,
        *,
        name: str,
        host: str,
        port: int,
        backend_type: AzureSynapseBackendType,
        username: str,
        password: str,
        database: str | None = None,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param host: A host of Azure Synapse SQL pool server
        :param port: A port of Azure Synapse SQL pool server
        :param backend_type: Backend type used for Azure Synapse
        :param username: SQL Server username.
        :param password: SQL Server password.
        :param database: Name of the database to connect to
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )

        self.host = host
        self.port = port
        self.backend_type = backend_type
        self.username = username
        self.password = password
        self.database = database
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "host",
                "port",
                "username",
                "database",
                "backend_type",
                "enable_catalog",
            },
        }

    def _secret_fields(self) -> set[str]:
        return {"password"}


class MsSqlServerCredentialUserPassword(ApiSecretChangeNestedResource):
    """MsSql-compatible credential via user-password auth."""

    def __init__(
        self,
        user: str,
        password: str,
    ):
        """
        Constructor.

        :param user: User name.
        :param password: Password.
        """
        self.user = user
        self.password = password

    def _api_variant_name(self) -> str:
        return "userPassword"

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"user"}

    def _secret_fields(self) -> set[str]:
        return {"password"}

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {}


class MsSqlServerCredentialEntraId(ApiSecretChangeNestedResource):
    """MsSql-compatible credential via entra-id auth."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ):
        """
        Constructor.

        :param client_id: The client ID of your Azure registered application.
        :param client_secret: The client secret of your Azure registered application.
        """
        self.client_id = client_id
        self.client_secret = client_secret

    def _api_variant_name(self) -> str:
        return "entraId"

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"client_id"}

    def _secret_fields(self) -> set[str]:
        return {"client_secret"}

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {}


MsSqlServerCredentialAuth = Union[
    MsSqlServerCredentialUserPassword, MsSqlServerCredentialEntraId
]


class MsSqlServerCredential(Credential):
    """Credential to connect to a Microsoft Sql Server warehouse."""

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        auth: MsSqlServerCredentialAuth,
        database: str | None = None,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param host: Host address of the server.
        :param port: Port number of the server.
        :param auth: Credentials to use for authentication.
        :param database: Name of the database to connect to
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )

        self.host = host
        self.port = port
        self.auth = auth
        self.database = database
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "host",
                "port",
                "database",
                "enable_catalog",
            },
        }

    def _secret_fields(self) -> set[str]:
        return set()

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {"auth": self.auth}


class OracleCredentialUserPassword(ApiSecretChangeNestedResource):
    """Oracle credential via user-password auth."""

    def __init__(
        self,
        user: str,
        password: str,
    ):
        """
        Constructor.

        :param user: User name.
        :param password: Password.
        """
        self.user = user
        self.password = password

    def _api_variant_name(self) -> str:
        return "userPassword"

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"user"}

    def _secret_fields(self) -> set[str]:
        return {"password"}

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {}


OracleCredentialAuth = Union[OracleCredentialUserPassword]


class OracleCredential(Credential):
    """Credential to connect to an Oracle database."""

    def __init__(
        self,
        name: str,
        host: str,
        port: int,
        database: str,
        auth: OracleCredentialAuth,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param host: Host address of the server.
        :param port: Port number of the server.
        :param auth: Credentials to use for authentication.
        :param database: Name of the database to connect to
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )

        self.host = host
        self.port = port
        self.database = database
        self.auth = auth
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "host",
                "port",
                "database",
                "enable_catalog",
            },
        }

    def _secret_fields(self) -> set[str]:
        return set()

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {"auth": self.auth}


class TableauConnectedAppCredential(Credential):
    """
    A credential resource that can be used to connect
    to Tableau using connected app.
    """

    def __init__(
        self,
        *,
        name: str,
        host: str,
        user: str,
        client_id: str,
        secret_id: str,
        secret_value: str,
        site: str | None = None,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param host: Host address to the Tableau instance
        :param user: Tableau username
        :param client_id: The connected app's unique id
        :param secret_id: The connected app's secret key identifier.
        :param secret_value: The connected app's secret key.
        :param site: Name of Tableau site
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.host = host
        self.user = user
        self.client_id = client_id
        self.secret_id = secret_id
        self.secret_value = secret_value
        self.site = site
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"host", "site", "user", "client_id", "secret_id", "enable_catalog"},
        }

    def _secret_fields(self) -> set[str]:
        return {"secret_value"}


class TableauPersonalAccessTokenCredential(Credential):
    """
    A credential resource that can be used to connect
    to Tableau using a personal access token.
    """

    def __init__(
        self,
        *,
        name: str,
        host: str,
        token_name: str,
        token_value: str,
        site: str | None = None,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param host: Host address to the Tableau instance
        :param user: Tableau username
        :param token_name: Personal access token name
        :param token_value: Personal access token secret
        :param site: Name of Tableau site
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.host = host
        self.token_name = token_name
        self.token_value = token_value
        self.site = site
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"host", "site", "token_name", "enable_catalog"},
        }

    def _secret_fields(self) -> set[str]:
        return {"token_value"}


class ClickHouseCredential(Credential):
    """A credential resource that can be used to connect to a ClickHouse table."""

    def __init__(
        self,
        *,
        name: str,
        protocol: ClickHouseProtocol,
        host: str,
        port: int,
        username: str,
        password: str,
        default_database: str,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param protocol: A protocol of connection to a ClickHouse deployment.
        :param host: A host of ClickHouse deployment.
        :param port: A port of ClickHouse deployment.
        :param username: Username having read access to the desired database or tables.
        :param password: Password of the specified user.
        :param default_database: Name of the default database to use this
            credential with. This can be overridden e.g. in a Source configuration.
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )

        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.default_database = default_database
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{
                "protocol",
                "host",
                "port",
                "username",
                "default_database",
                "enable_catalog",
            },
        }

    def _secret_fields(self) -> set[str]:
        return {"password"}


class MsPowerBiCredentialAuthEntraId(ApiSecretChangeNestedResource):
    """Azure EntraID authentication for PowerBI."""

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        tenant_id: str,
    ):
        """
        Constructor.

        :param client_id: The client ID of your Azure registered application.
        :param client_secret: The client secret of your Azure registered application.
        :param tenant_id: The tenant ID of your Azure registered application.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id

    def _api_variant_name(self) -> str:
        return "entraId"

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {"client_id", "tenant_id"}

    def _secret_fields(self) -> set[str]:
        return {"client_secret"}

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {}


MsPowerBiCredentialAuth = Union[MsPowerBiCredentialAuthEntraId]


class MsPowerBiCredential(Credential):
    """
    A credential resource that can be used
    to connect to PowerBI using an EntraID credential.
    """

    def __init__(
        self,
        *,
        name: str,
        auth: MsPowerBiCredentialAuth,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param auth: Credentials to use for authentication.
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.auth = auth
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _secret_fields(self) -> set[str]:
        return set()

    def _nested_objects(
        self,
    ) -> dict[str, Optional["Diffable | list[Diffable]"] | None]:
        return {"auth": self.auth}


class SigmaCredential(Credential):
    """A Sigma credential resource."""

    def __init__(
        self,
        *,
        name: str,
        base_url: str,
        client_id: str,
        client_secret: str,
        enable_catalog: bool = False,
        display_name: str | None = None,
        ignore_changes: bool = False,
        __internal__: ResourceGraph | None = None,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the credential
        :param base_url: Address to the Sigma instance
        :param client_id: Sigma credential client id
        :param client_secret: Sigma credential client secret
        :param enable_catalog: If set to true, this credential will
            be used to fetch catalog information.
        :param display_name: Human-readable name for the credential. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=__internal__,
        )
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.enable_catalog = enable_catalog

    def _immutable_fields(self) -> set[str]:
        return set({})

    def _mutable_fields(self) -> set[str]:
        return {
            *super()._mutable_fields(),
            *{"base_url", "client_id", "enable_catalog"},
        }

    def _secret_fields(self) -> set[str]:
        return {"client_secret"}


WarehouseCredential = Union[
    AzureSynapseCredential,
    AwsAthenaCredential,
    AwsRedshiftCredential,
    ClickHouseCredential,
    DatabricksCredential,
    GcpCredential,
    PostgreSqlCredential,
    SnowflakeCredential,
]
