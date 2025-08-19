import asyncio
import inspect
from typing import Any

from camel_converter import to_camel, to_snake
from gql.transport.exceptions import TransportQueryError

# We need to import the validio_sdk module due to the `eval`
# ruff: noqa: F401
import validio_sdk
from validio_sdk._api import api
from validio_sdk.client import Session
from validio_sdk.code._progress import ProgressBar
from validio_sdk.exception import ValidioBugError, ValidioError
from validio_sdk.resource._diff import (
    DiffContext,
    GraphDiff,
    ResourceUpdate,
    ResourceUpdates,
    infer_schemas,
)
from validio_sdk.resource._diff_util import (
    must_find_channel,
    must_find_credential,
    must_find_filter,
    must_find_segmentation,
    must_find_source,
    must_find_tag,
    must_find_window,
)
from validio_sdk.resource._resource import Resource, ResourceGraph
from validio_sdk.resource._util import _rename_dict_key, _sanitize_error
from validio_sdk.resource.channels import (
    Channel,
    EmailChannel,
    MsTeamsChannel,
    SlackChannel,
    WebhookChannel,
)
from validio_sdk.resource.credentials import (
    AtlanCredential,
    AwsAthenaCredential,
    AwsCredential,
    AwsRedshiftCredential,
    AzureSynapseEntraIdCredential,
    AzureSynapseSqlCredential,
    ClickHouseCredential,
    Credential,
    DatabricksCredential,
    DbtCloudCredential,
    DbtCoreCredential,
    DemoCredential,
    GcpCredential,
    KafkaSaslSslPlainCredential,
    KafkaSslCredential,
    LookerCredential,
    MsPowerBiCredential,
    MsPowerBiCredentialAuthEntraId,
    MsSqlServerCredential,
    MsSqlServerCredentialAuth,
    MsSqlServerCredentialEntraId,
    MsSqlServerCredentialUserPassword,
    OracleCredential,
    OracleCredentialAuth,
    OracleCredentialUserPassword,
    PostgreSqlCredential,
    SigmaCredential,
    SnowflakeCredential,
    SnowflakeCredentialAuth,
    SnowflakeCredentialKeyPair,
    SnowflakeCredentialUserPassword,
    TableauConnectedAppCredential,
    TableauPersonalAccessTokenCredential,
)
from validio_sdk.resource.filters import Filter, SqlFilter
from validio_sdk.resource.notification_rules import Conditions
from validio_sdk.resource.segmentations import Segmentation
from validio_sdk.resource.sources import AzureSynapseSource, Source, SqlSource
from validio_sdk.resource.tags import Tag
from validio_sdk.resource.thresholds import Threshold
from validio_sdk.resource.validators import Reference, SqlValidator, Validator

# Some credentials depend on other credentials, i.e. wrapping credentials. This
# list contains all of those and can be used when sorting to ensure they always
# end up where you want them.
CREDENTIALS_WITH_DEPENDENCIES = {"DbtCoreCredential", "DbtCloudCredential"}
DELETE_BATCH_SIZE = 1000


async def load_resources(
    namespace: str, session: Session, progress_bar: ProgressBar
) -> DiffContext:
    g = ResourceGraph()
    ctx = DiffContext()

    # Ordering matters here - we need to load parent resources before children
    progress_bar.update(description="Loading tags")
    await load_tags(g, ctx, session=session)
    progress_bar.update(advance=1)
    progress_bar.update(description="Loading credentials")
    await load_credentials(namespace, g, ctx, session=session)
    progress_bar.update(advance=1)
    progress_bar.update(description="Loading channels")
    await load_channels(namespace, g, ctx, session=session)
    progress_bar.update(advance=1)
    progress_bar.update(description="Loading sources")
    await load_sources(namespace, ctx, session=session)
    progress_bar.update(advance=1)
    progress_bar.update(description="Loading filters")
    await load_filters(namespace, ctx, session=session)
    progress_bar.update(advance=1)
    progress_bar.update(description="Loading windows")
    await load_windows(namespace, ctx, session=session)
    progress_bar.update(advance=1)
    progress_bar.update(description="Loading segmentations")
    await load_segmentations(namespace, ctx, session=session)
    progress_bar.update(advance=1)
    progress_bar.update(description="Loading notification rules")
    await load_notification_rules(namespace, ctx, session=session)
    progress_bar.update(advance=1)
    progress_bar.update(description="Loading validators")
    await load_validators(namespace, ctx, session=session)
    progress_bar.update(advance=1)

    return ctx


async def load_tags(
    g: ResourceGraph,
    ctx: DiffContext,
    session: Session,
) -> None:
    resources = await api.get_tags(session=session)

    if not isinstance(resources, list):
        raise ValidioError("failed to load tags")

    for t in resources:
        tag = Tag(
            key=t["key"],
            value=t["value"],
            __internal__=g,
        )
        tag._id.value = t["id"]

        ctx.tags[tag.name] = tag


# ruff: noqa: PLR0915
async def load_credentials(
    # ruff: noqa: ARG001
    namespace: str,
    g: ResourceGraph,
    ctx: DiffContext,
    session: Session,
) -> None:
    credentials = await api.get_credentials(
        namespace_id=namespace,
        session=session,
    )

    if not isinstance(credentials, list):
        raise ValidioError("failed to load credentials")

    # Ensure we sort the credentials so the ones that depend on other
    # credentials (wrapping credentials) always comes last.
    credentials.sort(key=lambda c: c["__typename"] in CREDENTIALS_WITH_DEPENDENCIES)

    for c in credentials:
        name = c["resourceName"]
        display_name = c["name"]

        # The 'secret' parts of a credential are left unset since they are not
        # provided by the API. We check for changes to them specially.
        match c["__typename"]:
            case "DemoCredential":
                credential: Credential = DemoCredential(
                    name=name,
                    display_name=display_name,
                    __internal__=g,
                )
            case "DbtCoreCredential":
                credential = DbtCoreCredential(
                    name=name,
                    warehouse_credential=must_find_credential(
                        ctx,
                        c["config"]["warehouseCredential"]["resourceName"],
                    ),
                    display_name=display_name,
                    __internal__=g,
                )
            case "DbtCloudCredential":
                credential = DbtCloudCredential(
                    name=name,
                    account_id=c["config"]["accountId"],
                    api_base_url=c["config"]["apiBaseUrl"],
                    token="UNSET",
                    warehouse_credential=must_find_credential(
                        ctx,
                        c["config"]["warehouseCredential"]["resourceName"],
                    ),
                    display_name=display_name,
                    __internal__=g,
                )
            case "AtlanCredential":
                credential = AtlanCredential(
                    name=name,
                    display_name=display_name,
                    application_link_url=c["config"]["applicationLinkUrl"],
                    base_url=c["config"]["baseUrl"],
                    api_token="UNSET",
                    __internal__=g,
                )
            case "GcpCredential":
                credential = GcpCredential(
                    name=name,
                    credential="UNSET",
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    billing_project=c["config"]["billingProject"],
                    __internal__=g,
                )
            case "AwsCredential":
                credential = AwsCredential(
                    name=name,
                    access_key=c["config"]["accessKey"],
                    secret_key="UNSET",
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "PostgreSqlCredential":
                credential = PostgreSqlCredential(
                    name=name,
                    host=c["config"]["host"],
                    port=c["config"]["port"],
                    user=c["config"]["user"],
                    password="UNSET",
                    default_database=c["config"]["defaultDatabase"],
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "AwsRedshiftCredential":
                credential = AwsRedshiftCredential(
                    name=name,
                    host=c["config"]["host"],
                    port=c["config"]["port"],
                    user=c["config"]["user"],
                    password="UNSET",
                    default_database=c["config"]["defaultDatabase"],
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "AwsAthenaCredential":
                credential = AwsAthenaCredential(
                    name=name,
                    access_key=c["config"]["accessKey"],
                    secret_key="UNSET",
                    region=c["config"]["region"],
                    query_result_location=c["config"]["queryResultLocation"],
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "AzureSynapseEntraIdCredential":
                credential = AzureSynapseEntraIdCredential(
                    name=name,
                    host=c["config"]["host"],
                    port=c["config"]["port"],
                    backend_type=c["config"]["backendType"],
                    client_id=c["config"]["clientId"],
                    client_secret="UNSET",
                    database=c["config"]["database"],
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "AzureSynapseSqlCredential":
                credential = AzureSynapseSqlCredential(
                    name=name,
                    host=c["config"]["host"],
                    port=c["config"]["port"],
                    backend_type=c["config"]["backendType"],
                    username=c["config"]["username"],
                    password="UNSET",
                    database=c["config"]["database"],
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "ClickHouseCredential":
                credential = ClickHouseCredential(
                    name=name,
                    protocol=c["config"]["protocol"],
                    host=c["config"]["host"],
                    port=int(c["config"]["port"]),
                    username=c["config"]["username"],
                    password="UNSET",
                    default_database=c["config"]["defaultDatabase"],
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "DatabricksCredential":
                credential = DatabricksCredential(
                    name=name,
                    host=c["config"]["host"],
                    port=c["config"]["port"],
                    access_token="UNSET",
                    http_path=c["config"]["httpPath"],
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "SnowflakeCredential":
                auth_type = c["config"]["auth"]["__typename"]

                if auth_type == "SnowflakeCredentialUserPassword":
                    sf_auth: SnowflakeCredentialAuth = SnowflakeCredentialUserPassword(
                        user=c["config"]["auth"]["user"],
                        password="UNSET",
                    )
                elif auth_type == "SnowflakeCredentialKeyPair":
                    sf_auth = SnowflakeCredentialKeyPair(
                        user=c["config"]["auth"]["user"],
                        private_key="UNSET",
                        private_key_passphrase="UNSET",
                    )
                else:
                    raise ValidioBugError(f"Unknown Snowflake auth type: '{auth_type}'")

                credential = SnowflakeCredential(
                    name=name,
                    account=c["config"]["account"],
                    auth=sf_auth,
                    warehouse=c["config"]["warehouse"],
                    role=c["config"]["role"],
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "MsSqlServerCredential":
                auth_type = c["config"]["auth"]["__typename"]

                if auth_type == "MsSqlServerCredentialUserPassword":
                    ms_auth: MsSqlServerCredentialAuth = (
                        MsSqlServerCredentialUserPassword(
                            user=c["config"]["auth"]["user"],
                            password="UNSET",
                        )
                    )
                elif auth_type == "MsSqlServerCredentialEntraId":
                    ms_auth = MsSqlServerCredentialEntraId(
                        client_id=c["config"]["auth"]["clientId"],
                        client_secret="UNSET",
                    )
                else:
                    raise ValidioBugError(
                        f"Unknown MsSqlServer auth type: '{auth_type}'"
                    )

                credential = MsSqlServerCredential(
                    name=name,
                    host=c["config"]["host"],
                    port=c["config"]["port"],
                    database=c["config"]["database"],
                    auth=ms_auth,
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "OracleCredential":
                auth_type = c["config"]["auth"]["__typename"]

                if auth_type == "OracleCredentialUserPassword":
                    oracle_auth: OracleCredentialAuth = OracleCredentialUserPassword(
                        user=c["config"]["auth"]["user"],
                        password="UNSET",
                    )
                else:
                    raise ValidioBugError(f"Unknown Oracle auth type: '{auth_type}'")

                credential = OracleCredential(
                    name=name,
                    host=c["config"]["host"],
                    port=c["config"]["port"],
                    database=c["config"]["database"],
                    auth=oracle_auth,
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "KafkaSslCredential":
                credential = KafkaSslCredential(
                    name=name,
                    bootstrap_servers=c["config"]["bootstrapServers"],
                    ca_certificate=c["config"]["caCertificate"],
                    client_certificate="UNSET",
                    client_private_key="UNSET",
                    client_private_key_password="UNSET",
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "KafkaSaslSslPlainCredential":
                credential = KafkaSaslSslPlainCredential(
                    name=name,
                    bootstrap_servers=c["config"]["bootstrapServers"],
                    username=c["config"]["username"],
                    password="UNSET",
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "LookerCredential":
                credential = LookerCredential(
                    name=name,
                    base_url=c["config"]["baseUrl"],
                    client_id=c["config"]["clientId"],
                    client_secret="UNSET",
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "MsPowerBiCredential":
                entra_id_auth = MsPowerBiCredentialAuthEntraId(
                    client_id=c["config"]["auth"]["clientId"],
                    client_secret="UNSET",
                    tenant_id=c["config"]["auth"]["tenantId"],
                )
                credential = MsPowerBiCredential(
                    name=name,
                    auth=entra_id_auth,
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "SigmaCredential":
                credential = SigmaCredential(
                    name=name,
                    base_url=c["config"]["baseUrl"],
                    client_id=c["config"]["clientId"],
                    client_secret="UNSET",
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "TableauConnectedAppCredential":
                credential = TableauConnectedAppCredential(
                    name=name,
                    host=c["config"]["host"],
                    site=c["config"]["site"],
                    user=c["config"]["user"],
                    client_id=c["config"]["clientId"],
                    secret_id=c["config"]["secretId"],
                    secret_value="UNSET",
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case "TableauPersonalAccessTokenCredential":
                credential = TableauPersonalAccessTokenCredential(
                    name=name,
                    host=c["config"]["host"],
                    site=c["config"]["site"],
                    token_name=c["config"]["tokenName"],
                    token_value="UNSET",
                    display_name=display_name,
                    enable_catalog=c["enableCatalog"],
                    __internal__=g,
                )
            case _:
                raise ValidioError(
                    f"unsupported credential '{name}' of type '{type(c)}'"
                )

        credential._id.value = c["id"]
        credential._namespace = c["namespace"]["id"]

        ctx.credentials[name] = credential


async def load_channels(
    namespace: str,
    g: ResourceGraph,
    ctx: DiffContext,
    session: Session,
) -> None:
    server_channels = await api.get_channels(namespace_id=namespace, session=session)

    if not isinstance(server_channels, list):
        raise ValidioError("failed to load channels")

    for ch in server_channels:
        name = ch["resourceName"]

        cfg = ch["config"]
        application_link_url = cfg["applicationLinkUrl"]
        interactive_message_enabled = cfg.get("interactiveMessageEnabled", None)
        display_name = ch["name"]
        # The 'secret' parts of a channel are left unset since they are not
        # provided by the API. We check for changes to them specially.
        match ch["__typename"]:
            case "MsTeamsChannel":
                channel: Channel = MsTeamsChannel(
                    name=name,
                    application_link_url=application_link_url,
                    ms_teams_channel_id=cfg["msTeamsChannelId"],
                    client_id="UNSET",
                    client_secret="UNSET",
                    interactive_message_enabled=interactive_message_enabled,
                    display_name=display_name,
                    __internal__=g,
                )
            case "SlackChannel":
                channel = SlackChannel(
                    name=name,
                    application_link_url=application_link_url,
                    slack_channel_id=cfg["slackChannelId"],
                    token="UNSET",
                    signing_secret="UNSET",
                    app_token="UNSET",
                    interactive_message_enabled=interactive_message_enabled,
                    display_name=display_name,
                    __internal__=g,
                )
            case "WebhookChannel":
                channel = WebhookChannel(
                    name=name,
                    application_link_url=application_link_url,
                    auth_header="UNSET",
                    webhook_url="UNSET",
                    display_name=display_name,
                    __internal__=g,
                )
            case "EmailChannel":
                auth = cfg["auth"]
                auth_cls = eval(
                    f"validio_sdk.resource.channels.{auth.pop('__typename')}"
                )
                channel = EmailChannel(
                    **{
                        **{to_snake(k): v for k, v in cfg.items()},
                        "name": name,
                        "application_link_url": application_link_url,
                        "display_name": display_name,
                        "interactive_message_enabled": interactive_message_enabled,
                        "auth": auth_cls(
                            **{
                                f: auth.get(to_camel(f), "UNSET")
                                for f in inspect.signature(auth_cls).parameters
                            }
                        ),
                        "__internal__": g,
                    }
                )
            case _:
                raise ValidioError(f"unsupported channel '{name}' of type '{type(ch)}'")

        channel._id.value = ch["id"]
        channel._namespace = ch["namespace"]["id"]
        ctx.channels[name] = channel


async def load_notification_rules(
    namespace: str,
    ctx: DiffContext,
    session: Session,
) -> None:
    rules = await api.get_notification_rules(namespace_id=namespace, session=session)

    if not isinstance(rules, list):
        raise ValidioError("failed to load rules")

    for r in rules:
        name = r["resourceName"]

        cls = eval(f"validio_sdk.resource.notification_rules.{r['__typename']}")

        rule = cls(
            name=name,
            channel=must_find_channel(ctx, r["channel"]["resourceName"]),
            conditions=Conditions._new_from_api(ctx, r["config"]),
            display_name=r["name"],
        )
        rule._id.value = r["id"]
        rule._namespace = r["namespace"]["id"]
        ctx.notification_rules[name] = rule


async def load_sources(
    namespace: str,
    ctx: DiffContext,
    session: Session,
) -> None:
    server_sources = await api.get_sources(namespace_id=namespace, session=session)

    if not isinstance(server_sources, list):
        raise ValidioError("failed to load sources")

    for s in server_sources:
        name = s["resourceName"]
        source_config = s.get("config", {})

        cls = eval(f"validio_sdk.resource.sources.{s['__typename']}")
        source = cls(
            **{
                **{to_snake(k): v for k, v in source_config.items()},
                "name": name,
                "display_name": s["name"],
                "credential": must_find_credential(
                    ctx, s["credential"]["resourceName"]
                ),
                "jtd_schema": s["jtdSchema"],
                "description": s["description"],
                "tags": [
                    must_find_tag(ctx, Tag._unique_name(t["key"], t["value"]))
                    for t in s["tags"]
                ],
            }
        )
        source._id.value = s["id"]
        source._namespace = s["namespace"]["id"]
        ctx.sources[name] = source


async def load_segmentations(
    namespace: str,
    ctx: DiffContext,
    session: Session,
) -> None:
    server_segmentations = await api.get_segmentations(
        namespace_id=namespace, session=session
    )

    if not isinstance(server_segmentations, list):
        raise ValidioError("failed to load segmentations")

    for s in server_segmentations:
        name = s["resourceName"]

        filter_ = (
            must_find_filter(ctx, s["filter"]["resourceName"]) if s["filter"] else None
        )
        segmentation = Segmentation(
            name=name,
            source=must_find_source(ctx, s["source"]["resourceName"]),
            fields=s["fields"],
            filter=filter_,
            display_name=s["name"],
            segment_usage=s["segmentUsage"],
        )

        segmentation._id.value = s["id"]
        segmentation._namespace = s["namespace"]["id"]
        ctx.segmentations[name] = segmentation


async def load_windows(
    namespace: str,
    ctx: DiffContext,
    session: Session,
) -> None:
    server_windows = await api.get_windows(namespace_id=namespace, session=session)

    if not isinstance(server_windows, list):
        raise ValidioError("failed to load windows")

    for w in server_windows:
        name = w["resourceName"]

        cls = eval(f"validio_sdk.resource.windows.{w['__typename']}")

        data_time_field = (
            {"data_time_field": w["dataTimeField"]} if "dataTimeField" in w else {}
        )

        window = cls(
            **{
                **{to_snake(k): v for k, v in w.get("config", {}).items()},
                "name": name,
                "display_name": w["name"],
                "source": must_find_source(ctx, w["source"]["resourceName"]),
                **data_time_field,
            }
        )

        window._id.value = w["id"]
        window._namespace = w["namespace"]["id"]
        ctx.windows[name] = window


async def load_filters(
    namespace: str,
    ctx: DiffContext,
    session: Session,
) -> None:
    server_filters = await api.get_filters(namespace_id=namespace, session=session)

    if not isinstance(server_filters, list):
        raise ValidioError("failed to load filters")

    for f in server_filters:
        name = f["resourceName"]

        cls = eval(f"validio_sdk.resource.filters.{f['__typename']}")

        filter_ = cls(
            **{
                **{to_snake(k): v for k, v in f.get("config", {}).items()},
                "name": name,
                "source": must_find_source(ctx, f["source"]["resourceName"]),
                "display_name": f["name"],
            }
        )

        filter_._id.value = f["id"]
        filter_._namespace = f["namespace"]["id"]
        ctx.filters[name] = filter_


# Takes in a graphql Threshold type
def convert_threshold(t: dict[str, Any]) -> Threshold:
    cls = eval(f"validio_sdk.resource.thresholds.{t['__typename']}")

    # Threshold parameters map 1-1 with resources, so
    # we call the constructor directly.
    return cls(**{to_snake(k): v for k, v in t.items() if k != "__typename"})


# Takes in a graphql ReferenceSourceConfig type
def convert_reference(ctx: DiffContext, r: dict[str, Any]) -> Reference:
    maybe_filter = (
        must_find_filter(ctx, r["sourceFilter"]["resourceName"])
        if r.get("sourceFilter")
        else None
    )

    return Reference(
        history=r["history"],
        offset=r["offset"],
        filter=maybe_filter,
    )


async def load_validators(
    namespace: str,
    ctx: DiffContext,
    session: Session,
) -> None:
    validators = await api.get_validators(
        namespace_id=namespace,
        session=session,
    )

    if not isinstance(validators, list):
        raise ValidioError("failed to load validators")

    for v in validators:
        name = v["resourceName"]
        display_name = v["name"]
        description = v["description"]
        config = v["config"]

        window = must_find_window(ctx, v["sourceConfig"]["window"]["resourceName"])
        segmentation = must_find_segmentation(
            ctx, v["sourceConfig"]["segmentation"]["resourceName"]
        )
        threshold = convert_threshold(config["threshold"])
        maybe_reference = (
            {"reference": convert_reference(ctx, v["referenceSourceConfig"])}
            if "referenceSourceConfig" in v
            else {}
        )
        maybe_filter = (
            {
                "filter": must_find_filter(
                    ctx,
                    v["sourceConfig"]["sourceFilter"]["resourceName"],
                )
            }
            if "sourceFilter" in v["sourceConfig"] and v["sourceConfig"]["sourceFilter"]
            else {}
        )

        # Volume validator still have a deprecated field that we use. It's
        # called sourceField in the API still but `optional_source_field` on
        # the resource class so we rename it here.
        if v["__typename"] == "VolumeValidator":
            _rename_dict_key(config, "sourceField", "optionalSourceField")

        config = {to_snake(k): v for k, v in config.items() if k != "threshold"}

        cls = eval(f"validio_sdk.resource.validators.{v['__typename']}")

        validator = cls(
            **{
                **config,
                **maybe_reference,
                **maybe_filter,
                "threshold": threshold,
                "name": name,
                "window": window,
                "segmentation": segmentation,
                "display_name": display_name,
                "description": description,
                "tags": [
                    must_find_tag(ctx, Tag._unique_name(t["key"], t["value"]))
                    for t in v["tags"]
                ],
            }
        )
        validator._id.value = v["id"]
        validator._namespace = v["namespace"]["id"]
        ctx.validators[name] = validator


async def apply_updates_on_server(
    namespace: str,
    ctx: DiffContext,
    diff: GraphDiff,
    session: Session,
    show_secrets: bool,
    progress_bar: ProgressBar,
    dry_run_sql: bool,
    test_credentials: bool,
) -> None:
    await apply_deletes(
        namespace=namespace,
        deletes=diff.to_delete,
        session=session,
        progress_bar=progress_bar,
    )

    # We perform create operations in two batches. First here creates top
    # level resources, then after performing updates, we create any remaining
    # resources. We do this due to a couple scenarios
    # - A resource potentially depends on the parent to be created first before
    #   it can be updated. Example is a notification rule that is being
    #   updated to reference a Source that is to be created. In such cases,
    #   we need to apply the create on parent resource before the update on
    #   child resource.
    # - Conversely, in some cases, a parent resource needs to be updated before
    #   the child resource can be created. e.g a validator that is referencing a
    #   new field in a schema needs the source to be updated first otherwise
    #   diver will reject the validator as invalid because the field does not
    #   yet exist.
    #
    # So, here we create the top level resources first - ensuring that any child
    # resource that relies on them are resolved properly.
    # We start with creating credentials only. Since sources need them to infer
    # schema.
    await apply_creates(
        namespace=namespace,
        manifest_ctx=ctx,
        creates=DiffContext(
            credentials=diff.to_create.credentials,
            tags=diff.to_create.tags,
        ),
        show_secrets=show_secrets,
        session=session,
        progress_bar=progress_bar,
        test_credentials=test_credentials,
    )

    # Resolve any pending source schemas now that we have their credential.
    sources_to_infer = [
        source
        for source in diff.to_create.sources.values()
        if source.jtd_schema is None
    ]
    await infer_schemas(
        manifest_ctx=ctx,
        sources=sources_to_infer,
        session=session,
    )

    # Create the remaining top level resources.
    await apply_creates(
        namespace=namespace,
        manifest_ctx=ctx,
        creates=DiffContext(
            sources=diff.to_create.sources,
            channels=diff.to_create.channels,
        ),
        show_secrets=show_secrets,
        session=session,
        progress_bar=progress_bar,
        dry_run_sql=dry_run_sql,
    )

    # Then apply updates.
    await apply_updates(
        namespace=namespace,
        manifest_ctx=ctx,
        updates=diff.to_update,
        session=session,
        progress_bar=progress_bar,
        dry_run_sql=dry_run_sql,
        test_credentials=test_credentials,
        show_secrets=show_secrets,
    )

    # Then apply remaining creates. Resources that have been created in
    # the previous steps are marked as _applied, so they will be skipped this
    # time around.
    await apply_creates(
        namespace=namespace,
        manifest_ctx=ctx,
        creates=diff.to_create,
        show_secrets=show_secrets,
        session=session,
        progress_bar=progress_bar,
        dry_run_sql=dry_run_sql,
    )


# ruff: noqa: PLR0912
async def apply_deletes(
    namespace: str,
    deletes: DiffContext,
    session: Session,
    progress_bar: ProgressBar,
) -> None:
    progress_bar.update(description="Deleting resources")
    # Delete notification rules first These reference sources so we
    # remove them before removing the sources they reference.
    await _delete_resources(
        list(deletes.notification_rules.values()), session, progress_bar
    )

    # For pipeline resources, start with sources (This cascades deletes,
    # so we don't have to individually delete child resources).
    await _delete_resources(list(deletes.sources.values()), session, progress_bar)

    # Delete child resources
    await _delete_resources(list(deletes.validators.values()), session, progress_bar)
    await _delete_resources(list(deletes.windows.values()), session, progress_bar)
    await _delete_resources(list(deletes.segmentations.values()), session, progress_bar)
    await _delete_resources(list(deletes.filters.values()), session, progress_bar)

    # Finally delete credentials - these do not cascade so the api rejects any
    # delete requests if there are existing child resources attached to a credential.
    await _delete_resources(list(deletes.credentials.values()), session, progress_bar)
    await _delete_resources(list(deletes.channels.values()), session, progress_bar)


async def _delete_resources(
    resources: list[Resource],
    session: Session,
    progress_bar: ProgressBar,
) -> None:
    if len(resources) == 0:
        return

    resource_type = resources[0].resource_class_name()
    # Set mutation name and input names based on resource type
    mutation_name = f"{to_camel(to_snake(resource_type))}sDelete"
    input_type = f"[{resource_type}Id!]!"
    for batch in [
        list(resources[i : i + DELETE_BATCH_SIZE])
        for i in range(0, len(resources), DELETE_BATCH_SIZE)
    ]:
        await api.execute_mutation(
            session,
            mutation_name,
            argument_types={"ids": input_type},
            variable_values={"ids": [r._must_id() for r in batch]},
        )
        for resource in batch:
            resource._applied = True
            progress_bar.update(advance=1)


async def apply_creates(
    namespace: str,
    manifest_ctx: DiffContext,
    creates: DiffContext,
    show_secrets: bool,
    session: Session,
    progress_bar: ProgressBar,
    dry_run_sql: bool = False,
    test_credentials: bool = True,
) -> None:
    progress_bar.update(description="Creating resources")
    # Creates must be applied top-down, parent first before child resources
    credentials = list(creates.credentials.values())

    # Ensure we sort the credentials so the ones that depend on other
    # credentials (wrapping credentials) always comes last.
    credentials.sort(key=lambda c: type(c) in CREDENTIALS_WITH_DEPENDENCIES)

    await _apply_create_on_chunk(
        list(credentials),
        session,
        namespace,
        manifest_ctx,
        show_secrets,
        progress_bar,
        test_credentials,
    )
    resources_by_type = [
        creates.tags.values(),
        creates.sources.values(),
        creates.channels.values(),
        creates.filters.values(),
        creates.segmentations.values(),
        creates.windows.values(),
        creates.notification_rules.values(),
        creates.validators.values(),
    ]
    for resources in resources_by_type:
        resources_list = list(resources)
        await _maybe_validate_queries(
            resources_list, manifest_ctx, session, dry_run_sql
        )

        await _apply_creates(
            resources_list,
            session,
            namespace,
            manifest_ctx,
            show_secrets,
            progress_bar,
        )


async def _apply_creates(
    resources: list[Any],
    session: Session,
    namespace: str,
    manifest_ctx: DiffContext,
    show_secrets: bool,
    progress_bar: ProgressBar,
) -> None:
    await asyncio.gather(
        *[
            _apply_create_on_chunk(
                chunk,
                session,
                namespace,
                manifest_ctx,
                show_secrets,
                progress_bar,
            )
            for chunk in api.split_to_chunks(resources)
        ]
    )


async def _apply_create_on_chunk(
    chunk: list[Resource],
    session: Session,
    namespace: str,
    manifest_ctx: DiffContext,
    show_secrets: bool,
    progress_bar: ProgressBar,
    test_credentials: bool = True,
) -> None:
    for r in chunk:
        if r._applied:
            continue

        if test_credentials and isinstance(r, Credential):
            await _maybe_test_credentials(
                manifest_ctx,
                session,
                namespace,
                r,
                show_secrets,
            )

        try:
            await r._api_create(namespace, manifest_ctx, session)
            r._applied = True
            progress_bar.update(advance=1)
        except TransportQueryError as e:
            raise (_sanitize_error(e, show_secrets) if isinstance(r, Credential) else e)


async def _maybe_test_credentials(
    ctx: DiffContext,
    session: Session,
    namespace: str,
    credential: Credential,
    show_secrets: bool,
) -> None:
    try:
        await test_credential(namespace, ctx, credential, session)
    except ValidioError as e:
        raise ValidioError(f"failed to verify credential '{credential.name}': {e}")
    except TransportQueryError as e:
        raise _sanitize_error(e, show_secrets)


async def _maybe_validate_queries(
    resources_list: list[Any],
    manifest_ctx: DiffContext,
    session: Session,
    dry_run_sql: bool,
) -> None:
    if (
        len(resources_list) > 0
        and isinstance(resources_list[0], Validator)
        and dry_run_sql
    ):
        await validate_validator_sql_queries(
            manifest_ctx,
            [v for v in resources_list if isinstance(v, SqlValidator)],
            session,
        )
    if (
        len(resources_list) > 0
        and isinstance(resources_list[0], Filter)
        and dry_run_sql
    ):
        await validate_filter_sql_queries(
            manifest_ctx,
            [v for v in resources_list if isinstance(v, SqlFilter)],
            session,
        )
    if (
        len(resources_list) > 0
        and isinstance(resources_list[0], Source)
        and dry_run_sql
    ):
        await validate_source_sql_queries(
            manifest_ctx,
            [v for v in resources_list if isinstance(v, SqlSource)],
            session,
        )


async def apply_updates(
    namespace: str,
    manifest_ctx: DiffContext,
    updates: ResourceUpdates,
    session: Session,
    progress_bar: ProgressBar,
    show_secrets: bool,
    dry_run_sql: bool = False,
    test_credentials: bool = True,
) -> None:
    progress_bar.update(description="Updating resources")
    all_updates = [
        list(updates.credentials.values()),
        list(updates.sources.values()),
        list(updates.filters.values()),
        list(updates.segmentations.values()),
        list(updates.windows.values()),
        list(updates.validators.values()),
        list(updates.channels.values()),
        list(updates.notification_rules.values()),
    ]

    for up in all_updates:
        await _maybe_validate_queries(
            [v.manifest for v in up], manifest_ctx, session, dry_run_sql
        )

        await _apply_updates(
            [u for u in up if not u.manifest._applied],
            namespace,
            manifest_ctx,
            session,
            progress_bar,
            show_secrets,
            test_credentials,
        )


async def _apply_updates(
    resources: list[ResourceUpdate],
    namespace: str,
    manifest_ctx: DiffContext,
    session: Session,
    progress_bar: ProgressBar,
    show_secrets: bool,
    test_credentials: bool,
) -> None:
    await asyncio.gather(
        *[
            _apply_updates_on_chunk(
                chunk,
                namespace,
                manifest_ctx,
                session,
                progress_bar,
                show_secrets,
                test_credentials,
            )
            for chunk in api.split_to_chunks(resources)
        ]
    )


async def _apply_updates_on_chunk(
    chunk: list[ResourceUpdate],
    namespace: str,
    manifest_ctx: DiffContext,
    session: Session,
    progress_bar: ProgressBar,
    show_secrets: bool,
    test_credentials: bool,
) -> None:
    for u in chunk:
        if u.manifest._applied:
            continue

        if test_credentials and isinstance(u.manifest, Credential):
            await _maybe_test_credentials(
                manifest_ctx,
                session,
                namespace,
                u.manifest,
                show_secrets,
            )

        await u.manifest._api_update(namespace, manifest_ctx, session=session)
        u.manifest._applied = True
        progress_bar.update(advance=1)


async def validate_validator_sql_queries(
    manifest_ctx: DiffContext,
    validators: list[SqlValidator],
    session: Session,
) -> None:
    for validator in validators:
        await validate_validator_sql_query(manifest_ctx, validator, session)


async def validate_validator_sql_query(
    manifest_ctx: DiffContext,
    validator: SqlValidator,
    session: Session,
) -> None:
    if isinstance(manifest_ctx.sources[validator.source_name], AzureSynapseSource):
        # Skipping Azure Synapse sources since dry run is not supported for query
        # validation
        return None

    source = manifest_ctx.sources.get(validator.source_name)
    segmentation = manifest_ctx.segmentations.get(validator.segmentation_name)
    window = manifest_ctx.windows.get(validator.window_name)
    if source is None or segmentation is None or window is None:
        return None

    return await api.validate_sql_validator_query(
        session,
        validator.query,
        validator.display_name,
        source._must_id(),
        segmentation._must_id(),
        window._must_id(),
    )


async def validate_filter_sql_queries(
    manifest_ctx: DiffContext,
    filters: list[SqlFilter],
    session: Session,
) -> None:
    for f in filters:
        await validate_filter_sql_query(manifest_ctx, f, session)


async def validate_filter_sql_query(
    manifest_ctx: DiffContext,
    f: SqlFilter,
    session: Session,
) -> None:
    if isinstance(manifest_ctx.sources[f.source_name], AzureSynapseSource):
        # Skipping Azure Synapse sources since dry run is not supported for query
        # validation
        return None

    source = manifest_ctx.sources.get(f.source_name)
    if source is None:
        return None

    return await api.validate_sql_filter_query(
        session,
        f.query,
        f.display_name,
        source._must_id(),
    )


async def validate_source_sql_queries(
    manifest_ctx: DiffContext,
    sources: list[SqlSource],
    session: Session,
) -> None:
    for s in sources:
        await validate_source_sql_query(manifest_ctx, s, session)


async def validate_source_sql_query(
    manifest_ctx: DiffContext,
    source: SqlSource,
    session: Session,
) -> None:
    credential = manifest_ctx.credentials.get(source.credential_name)
    if credential is None:
        return

    if isinstance(credential, AzureSynapseSqlCredential):
        # Skipping Azure Synapse credentials since dry run is not supported for query
        # validation
        return

    await api.sql_source_preview(
        session=session,
        credential_id=credential._must_id(),
        sql_query=source.sql_query,
        dry_run=True,
        source_name=source.name,
    )


async def test_credential(
    namespace: str,
    manifest_ctx: DiffContext,
    credential: Credential,
    session: Session,
) -> None:
    """Test if a credential is valid.

    :param namespace: The namespace for the credetnial
    :param manifest_ctx: A manifest `DiffContext`
    :param credential: The credential to verify
    :param session: An API session to do API calls
    :raises: ValidioError on invalid credentials
    """
    input = credential._api_test_credential_input(namespace, manifest_ctx)
    if not input:
        return None

    return await api.test_credential(session, input)
