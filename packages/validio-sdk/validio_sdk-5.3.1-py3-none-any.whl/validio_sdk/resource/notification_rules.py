"""Notification rule configuration."""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, cast

from validio_sdk.exception import ValidioError
from validio_sdk.resource._diffable import Diffable
from validio_sdk.resource._resource import Resource, ResourceGraph
from validio_sdk.resource._serde import (
    NODE_TYPE_FIELD_NAME,
    _api_create_input_params,
    _api_update_input_params,
    _encode_resource,
    get_config_node,
)
from validio_sdk.resource.channels import Channel
from validio_sdk.resource.sources import Source
from validio_sdk.resource.tags import Tag

if TYPE_CHECKING:
    from validio_sdk.code._import import ImportContext
    from validio_sdk.resource._diff import DiffContext


class IncidentSeverity(str, Enum):
    """Severity of an incident severity condition."""

    HIGH = "HIGH"
    LOW = "LOW"
    MEDIUM = "MEDIUM"


class IssueTypename(str, Enum):
    """Name of issue type."""

    GenericSourceError = "GenericSourceError"
    SchemaChangeSourceError = "SchemaChangeSourceError"
    SegmentLimitExceededSourceError = "SegmentLimitExceededSourceError"
    ValidatorIncident = "ValidatorIncident"


@dataclass
class SegmentCondition:
    """A segment condition is a field and value to match segments on."""

    field: str
    value: str

    def _encode(self) -> dict[str, object]:
        return self.__dict__


class Conditions(Diffable):
    """Conditions used for notification rules."""

    def __init__(
        self,
        *,
        owner_condition: "OwnerNotificationRuleCondition | None" = None,
        segment_conditions: list["SegmentNotificationRuleCondition"] | None = None,
        severity_condition: "SeverityNotificationRuleCondition | None" = None,
        source_condition: "SourceNotificationRuleCondition | None" = None,
        tag_conditions: list["TagNotificationRuleCondition"] | None = None,
        type_condition: "TypeNotificationRuleCondition | None" = None,
    ) -> None:
        """Constructor."""
        self._node_type = self.__class__.__name__

        self.owner_condition = owner_condition
        self.segment_conditions = segment_conditions
        self.severity_condition = severity_condition
        self.source_condition = source_condition
        self.tag_conditions = tag_conditions
        self.type_condition = type_condition

        if self.tag_conditions is not None:
            self.tag_conditions.sort(key=lambda t: t.tag_names)

        if self.segment_conditions is not None:
            self.segment_conditions.sort(
                key=lambda s: sorted((fv.field, fv.value) for fv in s.segments)
            )

    def _immutable_fields(self) -> set[str]:
        return set()

    def _mutable_fields(self) -> set[str]:
        return set()

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        # For some reason mypy doesn't recognize <Type>Condition -> Condition ->
        # Diffable as fulfiling the Diffable type.
        objects: dict[str, Diffable | list[Diffable] | None] = {  # type: ignore
            "owner_condition": self.owner_condition,
            "segment_conditions": self.segment_conditions,  # type: ignore
            "severity_condition": self.severity_condition,
            "source_condition": self.source_condition,
            "tag_conditions": self.tag_conditions,  # type: ignore
            "type_condition": self.type_condition,
        }

        return objects

    def _encode(self) -> dict[str, object]:
        return self.__dict__

    @staticmethod
    def _decode(ctx: "DiffContext", obj: dict[str, Any]) -> "Conditions":
        cls = eval(obj[NODE_TYPE_FIELD_NAME])

        args = {}
        for k, v in obj.items():
            if v is None:
                continue

            if k == NODE_TYPE_FIELD_NAME:
                continue

            if isinstance(v, list):
                values = []
                for value_element in v:
                    condition_cls = eval(value_element[NODE_TYPE_FIELD_NAME])
                    values.append(condition_cls._decode(ctx, value_element))

                args[k] = values
            else:
                condition_cls = eval(v[NODE_TYPE_FIELD_NAME])
                args[k] = condition_cls._decode(ctx, v)

        return cls(**args)

    def _create_input(self, ctx: "DiffContext") -> dict[str, Any]:
        conditions: dict[str, Any] = {}
        if self.owner_condition is not None:
            conditions["ownerCondition"] = {"owners": self.owner_condition.owners}

        if self.severity_condition is not None:
            conditions["severityCondition"] = {
                "severities": [s.value for s in self.severity_condition.severities]
            }

        if self.source_condition is not None:
            conditions["sourceCondition"] = {
                "sourceIds": [
                    ctx.sources[source_name]._must_id()
                    for source_name in self.source_condition.sources
                ],
            }

        if self.type_condition is not None:
            conditions["typeCondition"] = {"types": self.type_condition.types}

        if self.segment_conditions is not None:
            conditions["segmentConditions"] = [
                {"segments": [s._encode() for s in segment_condition.segments]}
                for segment_condition in self.segment_conditions
            ]

        if self.tag_conditions is not None:
            try:
                conditions["tagConditions"] = [
                    {
                        "tagIds": [
                            ctx.tags[name]._must_id()
                            for name in tag_condition.tag_names
                        ]
                    }
                    for tag_condition in self.tag_conditions
                ]
            except KeyError as e:
                # This only happens if they user uses legacy key-value
                # dictionary but defines a tag that doesn't exist. This should
                # never happen for new manifest and only serves as backwards
                # compatibility for existing manifests.
                raise ValidioError(
                    "A tag referenced is missing on the server. "
                    "Please ensure the tag is created or use a `Tag` "
                    "resource in your manifest to create it first.\n"
                    f"{e}"
                )

        return conditions

    def _api_create_input(self, ctx: "DiffContext") -> dict[str, Any]:
        return self._create_input(ctx)

    def _api_update_input(self, ctx: "DiffContext") -> dict[str, Any]:
        return self._create_input(ctx)

    @classmethod
    def _new_from_api(
        cls: type["Conditions"],
        ctx: "DiffContext",
        api_conditions: dict[str, Any],
    ) -> "Conditions":
        """
        Create a new Conditions from API response.

        Input for creating and updating conditions for a notification rules in
        the API is a typed struct with fields for each condition type. Some of
        them might occur several times and is a list where others are just plain
        values.

        Output from the API however lists conditions as an array with elements
        being one conditions per row. This includes both across different
        condition types, f.ex. source conditions and type conditions are two
        different elements, but also for each condition that is represented as a
        list on the input, f.ex. each tag or segment will be returned as
        separate elements.

        This method will convert the API response and the expanded array for
        conditions to a `Conditions` type which is the same as the
        representation for create and update.
        """
        conditions = cls()

        for condition_type, condition in api_conditions.items():
            if condition is None:
                continue

            match condition_type:
                case "ownerCondition":
                    conditions.owner_condition = OwnerNotificationRuleCondition(
                        owners=[x["id"] for x in condition["config"]["owners"]]
                    )
                case "segmentConditions":
                    segment_conditions = [
                        SegmentNotificationRuleCondition(
                            segments=[
                                SegmentCondition(field=x["field"], value=x["value"])
                                for x in c["config"]["segments"]
                            ]
                        )
                        for c in condition
                    ]

                    conditions.segment_conditions = segment_conditions
                case "severityCondition":
                    conditions.severity_condition = SeverityNotificationRuleCondition(
                        severities=condition["config"]["severities"]
                    )
                case "sourceCondition":
                    sources = [
                        ctx.sources[source["resourceName"]]
                        for source in condition["config"]["sources"]
                        if source is not None and source["resourceName"] in ctx.sources
                    ]

                    conditions.source_condition = SourceNotificationRuleCondition(
                        sources=sources
                    )
                case "tagConditions":
                    tag_conditions = [
                        TagNotificationRuleCondition(
                            tags=[
                                ctx.tags[Tag._unique_name(x["key"], x["value"])]
                                for x in c["config"]["tags"]
                            ]
                        )
                        for c in condition
                    ]

                    conditions.tag_conditions = tag_conditions

                case "typeCondition":
                    conditions.type_condition = TypeNotificationRuleCondition(
                        types=[IssueTypename(x) for x in condition["config"]["types"]]
                    )

        return conditions


class NotificationRuleCondition(Diffable):
    """A condition for notification rules."""

    def __init__(self) -> None:
        """Base class for all notification rule conditions."""
        self._node_type = self.__class__.__name__

    def _immutable_fields(self) -> set[str]:
        return set()

    def _mutable_fields(self) -> set[str]:
        return set()

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        return {}

    def _encode(self) -> dict[str, Any]:
        return self.__dict__

    @staticmethod
    def _decode(_: "DiffContext", obj: dict[str, Any]) -> "NotificationRuleCondition":
        cls = eval(obj[NODE_TYPE_FIELD_NAME])
        return cls(**{k: v for k, v in obj.items() if k != NODE_TYPE_FIELD_NAME})


class OwnerNotificationRuleCondition(NotificationRuleCondition):
    """A condition for owners."""

    def __init__(self, *, owners: list[str]):
        """
        Constructor.

        :param owners: User IDs in uuid format. Will send notification for
        reasources owned by these users.
        """
        super().__init__()

        from uuid import UUID

        # Ensure we only try to work with valid UUIDs.
        for owner in owners:
            try:
                UUID(owner)
            except ValueError:
                raise ValidioError("owner must be id of type uuid")

        self.owners = owners
        self.owners.sort()

    def _mutable_fields(self) -> set[str]:
        return {"owners"}


class SegmentNotificationRuleCondition(NotificationRuleCondition):
    """A condition for segments."""

    def __init__(self, *, segments: dict[str, str] | list[SegmentCondition]):
        """
        Constructor.

        :param segments: Key value pairs of field and field values for segments
        to send notifications for.
        """
        super().__init__()
        self._legacy = False

        if isinstance(segments, dict):
            self._legacy = True
            segments = [SegmentCondition(field=k, value=v) for k, v in segments.items()]

        self.segments = segments
        self.segments.sort(key=lambda fv: (fv.field, fv.value))

    def _mutable_fields(self) -> set[str]:
        return {"segments"}

    @staticmethod
    def _decode(_: "DiffContext", obj: dict[str, Any]) -> "NotificationRuleCondition":
        cls = eval(obj[NODE_TYPE_FIELD_NAME])
        segments = [
            SegmentCondition(field=x["field"], value=x["value"])
            for x in obj["segments"]
        ]

        return cls(segments=segments)


class SeverityNotificationRuleCondition(NotificationRuleCondition):
    """A condition for severity."""

    def __init__(
        self,
        *,
        severities: list[IncidentSeverity],
    ):
        """
        Constructor.

        :param severities: List of severities to send notifications for.
        """
        super().__init__()
        self.severities = [
            (
                severity
                if isinstance(severity, IncidentSeverity)
                else IncidentSeverity(severity)
            )
            for severity in severities
        ]
        self.severities.sort()

    def _mutable_fields(self) -> set[str]:
        return {"severities"}


class SourceNotificationRuleCondition(NotificationRuleCondition):
    """A condition for sources."""

    def __init__(self, *, sources: list[Source]):
        """
        Constructor.

        :param sources: List of sources to send notifications for.
        """
        super().__init__()
        self.sources = [source.name for source in sources]
        self.sources.sort()

    def _mutable_fields(self) -> set[str]:
        return {"sources"}

    @staticmethod
    def _decode(
        ctx: "DiffContext", obj: dict[str, Any]
    ) -> "SourceNotificationRuleCondition":
        sources = [ctx.sources[source] for source in obj["sources"]]
        return SourceNotificationRuleCondition(sources=sources)

    def _import_str(
        self,
        indent_level: int,
        import_ctx: "ImportContext",
        inits: list[tuple[str, Any, str | None]] | None = None,
        skip_fields: set[str] | None = None,
    ) -> str:
        from validio_sdk.code._import import VariableName

        inits = inits or []
        inits.append(
            (
                "sources",
                [
                    VariableName(import_ctx.get_variable(Source, name))
                    for name in self.sources
                ],
                None,
            ),
        )

        return super()._import_str(
            indent_level,
            import_ctx,
            inits,
            skip_fields,
        )


class TagNotificationRuleCondition(NotificationRuleCondition):
    """A condition for tags."""

    def __init__(self, *, tags: dict[str, str | None] | list[Tag]):
        """
        Constructor.

        :param tags: Key value pairs of tags to send notifications for.
        """
        super().__init__()
        self._legacy = False

        if isinstance(tags, list):
            tag_list: list[Tag] = tags
        elif isinstance(tags, dict):
            self._legacy = True

            tag_list = [
                # This is for the names only, we don't care about adding them to
                # the proper resource graph.
                Tag(key=k, value=v, __internal__=ResourceGraph())
                for k, v in tags.items()
            ]
        else:
            raise ValidioError(f"Unexpected type for tags {type(tags)}")

        self.tag_names = [t.name for t in tag_list] if tag_list is not None else []

        # Ensure always sorted to avoid producing diff when order changes.
        self.tag_names.sort()

    def _mutable_fields(self) -> set[str]:
        return {"tag_names"}

    @staticmethod
    def _decode(
        ctx: "DiffContext", obj: dict[str, Any]
    ) -> "TagNotificationRuleCondition":
        names = cast(list[str], obj["tag_names"])

        if all(name in ctx.tags for name in names):
            tags: list[Tag] | dict[str, str | None] = [ctx.tags[name] for name in names]
        else:
            # Backwards compatibility to support key-value pairs.
            # We don't need to support this for new tags so this is only for
            # legacy users that used to use key-value-pairs and doesn't have the
            # tag in the manifest.
            #
            # Since this isn't the first time they apply a tag however, we know
            # the tag has previously been created and the server. If the user
            # wants to change to a tag that doesn't exist they would have to use
            # the new Tag resource.
            tags = {}
            for name in names:
                key, value = Tag._key_and_value_from_unique_name(name)
                tags[key] = value

        del obj["tag_names"]

        return TagNotificationRuleCondition(tags=tags)

    def _import_str(
        self,
        indent_level: int,
        import_ctx: "ImportContext",
        inits: list[tuple[str, Any, str | None]] | None = None,
        skip_fields: set[str] | None = None,
    ) -> str:
        from validio_sdk.code._import import VariableName

        inits = inits or []
        inits.append(
            (
                "tags",
                [
                    VariableName(import_ctx.get_variable(Tag, name))
                    for name in self.tag_names
                ],
                None,
            ),
        )

        return super()._import_str(
            indent_level,
            import_ctx,
            inits,
            skip_fields,
        )


class TypeNotificationRuleCondition(NotificationRuleCondition):
    """A condition for sources."""

    def __init__(
        self,
        *,
        types: list[IssueTypename],
    ):
        """
        Constructor.

        :param types: A list of event types to send notifications for.
        """
        super().__init__()
        self.types = [
            (type_ if isinstance(type_, IssueTypename) else IssueTypename(type_))
            for type_ in types
        ]
        self.types.sort()

    def _mutable_fields(self) -> set[str]:
        return {"types"}


class NotificationRule(Resource):
    """
    A notification rule.

    https://docs.validio.io/docs/notifications
    """

    def __init__(
        self,
        *,
        name: str,
        channel: Channel,
        conditions: Conditions | None = None,
        display_name: str | None = None,
        ignore_changes: bool = False,
    ):
        """
        Constructor.

        :param name: Unique resource name assigned to the window
        :param channel: The channel to attach the rule to
        :param conditions: List of conditions for the notification rule.
        :param display_name: Human-readable name for the channel. This name is
          visible in the UI and does not need to be unique.
        :param ignore_changes: If set to true, changes to the resource will be ignored.
        """
        super().__init__(
            name=name,
            display_name=display_name,
            ignore_changes=ignore_changes,
            __internal__=channel._resource_graph,
        )

        self.channel_name = channel.name

        # If conditions wasn't set, set it to an empty `Conditions` with all
        # fields to `None` to not have to account for `None`-ness of the field.
        self.conditions = conditions or Conditions()

        if self.conditions.tag_conditions is not None and any(
            x._legacy for x in self.conditions.tag_conditions
        ):
            self.add_deprecation(
                "Adding tag conditions with a dictionary is deprecated, please use a "
                "`Tag` resource instead"
            )

        if self.conditions.segment_conditions is not None and any(
            x._legacy for x in self.conditions.segment_conditions
        ):
            self.add_deprecation(
                "Adding segment conditions with a dictionary is deprecated, "
                "please use `SegmentCondition` from "
                "`validio_sdk.resource.notificaion_rule` instead"
            )

        channel.add(self.name, self)

        self._check_condition_deprecation()

    def _check_condition_deprecation(self) -> None:
        # TODO(VR-3875): Fully remove after deprecation warning period.
        cond = self.conditions
        self._check_and_delete_arg_deprecation_on_child(cond)
        self._check_and_delete_arg_deprecation_on_child(cond.owner_condition)
        self._check_and_delete_arg_deprecation_on_child(cond.severity_condition)
        self._check_and_delete_arg_deprecation_on_child(cond.source_condition)
        self._check_and_delete_arg_deprecation_on_child(cond.type_condition)

        for s in cond.segment_conditions or []:
            self._check_and_delete_arg_deprecation_on_child(s)

        for t in cond.tag_conditions or []:
            self._check_and_delete_arg_deprecation_on_child(t)

    def _nested_objects(self) -> dict[str, Diffable | list[Diffable] | None]:
        objects: dict[str, Diffable | list[Diffable] | None] = {
            "conditions": self.conditions,
        }

        return objects

    def _immutable_fields(self) -> set[str]:
        return {"channel_name"}

    def resource_class_name(self) -> str:
        """Returns the base class name."""
        return "NotificationRule"

    def _api_create_response_field_name(self) -> str:
        return "notificationRule"

    def _api_create_input(self, _namespace: str, ctx: "DiffContext") -> Any:
        return _api_create_input_params(
            self,
            overrides={
                "channelId": ctx.channels[self.channel_name]._must_id(),
                "config": self.conditions._api_create_input(ctx),
            },
            skip_fields={"sources", "notificationTypenames"},
        )

    def _api_update_input(self, _namespace: str, ctx: "DiffContext") -> Any:
        return _api_update_input_params(
            self,
            overrides={
                "config": self.conditions._api_update_input(ctx),
            },
        )

    def _api_delete_arguments(self) -> dict[str, str]:
        return {"input": f"{self.resource_class_name()}DeleteInput!"}

    def _api_delete_input(self) -> Any:
        return {"input": {"id": self._must_id()}}

    def _encode(self) -> dict[str, object]:
        # Drop fields here that are not part of the constructor for when
        # we deserialize back. They will be reinitialized by the constructor.
        return _encode_resource(self, skip_fields={"channel_name"})

    @staticmethod
    def _decode(
        ctx: "DiffContext",
        channel: Channel,
        obj: dict[str, Any],
    ) -> "NotificationRule":
        args: dict[str, Any] = get_config_node(obj)

        conditions = Conditions._decode(ctx, args["conditions"])

        return NotificationRule(
            **{
                **args,
                "channel": channel,
                "conditions": conditions,
            }
        )  # type: ignore
