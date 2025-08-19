"""Scalars used in our GraphQL schemas."""

from datetime import datetime

ValidioId = str
CredentialId = ValidioId
SegmentationId = ValidioId
SourceId = ValidioId
ValidatorId = ValidioId
WindowId = ValidioId

CronExpression = str

# Raw JSON, used for filters
JsonFilterExpression = dict

# JTD schema definition
JsonTypeDefinition = dict

# A JSONPath expression specifying a field within a datapoint.
# Examples:
#   user.address.street for nested structures.
#   name to select a non-nested field called `name`.
JsonPointer = str


def serialize_json_filter_expression(_: JsonFilterExpression) -> dict:
    """
    This serializer is unused and will be removed alongside the sdk.

    :param _: to be ignored
    :return: nothing
    """
    return {}


def serialize_rfc3339_datetime(value: datetime) -> datetime:
    """
    Adds TZINFO if not present to a Python Datetime object so that it conforms to the
    RFC3339 standard that is accepted by the platform.

    :param value: The datetime object
    :returns: A tz-aware datetime object
    """
    if value.tzinfo:
        return value

    return value.astimezone()
