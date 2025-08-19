from typing import Any

import pytest

from validio_sdk.code.plan import _create_resource_diff_object
from validio_sdk.resource._diffable import Diffable
from validio_sdk.resource._resource import Resource, ResourceGraph
from validio_sdk.resource.channels import SlackChannel, WebhookChannel
from validio_sdk.resource.credentials import (
    SnowflakeCredential,
    SnowflakeCredentialUserPassword,
)


@pytest.mark.parametrize(
    (
        "resource",
        "show_secrets",
        "secret_fields_changed",
        "expected_when_manifest",
        "expected_when_not_manifest",
    ),
    [
        # Since VR-4020, the webhook URL is the same as any other secret field on
        # a webhook channel.
        # We still have special treatment for webhook URL on other channel types
        # This test is present to prevent a regression and can be removed when
        # VR-4047 is addressed.
        #
        # No fields are indicated as changed in "secret_fields_changed", so no
        # fields are flagged as changed, including the webhook URL.
        (
            WebhookChannel(
                name="ch1",
                application_link_url="app",
                webhook_url="webhook",
                display_name="name",
                auth_header="header",
                __internal__=ResourceGraph(),
            ),
            False,
            {
                "auth_header": False,
                "webhook_url": False,
            },
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "webhook_url": "REDACTED",  # Secret field is hidden
                "auth_header": "REDACTED",  # Secret field is hidden
            },
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "webhook_url": "REDACTED",  # Secret field is not marked as changed
                "auth_header": "REDACTED",  # Secret field is not marked as changed
            },
        ),
        # Since VR-4020, the webhook URL is the same as any other secret field on
        # a webhook channel.
        # We still have special treatment for webhook URL on other channel types
        # This test is present to prevent a regression and can be removed when
        # VR-4047 is addressed.
        #
        # Previously webhook URL would be flagged as changed if any field changed.
        # This no longer applies for the webhook channel.
        (
            WebhookChannel(
                name="ch1",
                application_link_url="app",
                webhook_url="webhook",
                display_name="name",
                auth_header="header",
                __internal__=ResourceGraph(),
            ),
            False,
            {
                "auth_header": True,
                "webhook_url": False,
            },
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "webhook_url": "REDACTED",  # Secret field is hidden
                "auth_header": "REDACTED",  # Secret field is hidden
            },
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "webhook_url": "REDACTED",  # Secret field is not marked as changed
                "auth_header": "REDACTED-PREVIOUS",  # Secret field is marked as changed
            },
        ),
        # Using a channel that is not a Webhook channel with many secret fields, but
        # using the secret fields instead of the webhook URL field.
        # Only "token" is flagged as changed in the "secret_fields_changed".
        (
            SlackChannel(
                name="ch1",
                application_link_url="app",
                app_token="secret",
                slack_channel_id="sid",
                display_name="name",
                token="token",
                interactive_message_enabled=True,
                __internal__=ResourceGraph(),
            ),
            False,
            {
                "token": True,
                "app_token": False,
            },
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "app_token": "REDACTED",  # Secret field is hidden
                "slack_channel_id": "sid",
                "token": "REDACTED",  # Secret field is hidden
                "signing_secret": "REDACTED",  # Secret field is hidden
                "interactive_message_enabled": True,
            },
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "app_token": "REDACTED",
                "slack_channel_id": "sid",
                "token": "REDACTED-PREVIOUS",  # Secret field is marked as changed
                "signing_secret": "REDACTED",
                "interactive_message_enabled": True,
            },
        ),
        # When "secret_fields_changed" is empty the secret fields will not be marked as
        # changed
        (
            SlackChannel(
                name="ch1",
                application_link_url="app",
                app_token="secret",
                slack_channel_id="sid",
                display_name="name",
                token="token",
                interactive_message_enabled=True,
                __internal__=ResourceGraph(),
            ),
            False,
            None,
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "app_token": "REDACTED",  # Secret field is hidden
                "slack_channel_id": "sid",
                "token": "REDACTED",  # Secret field is hidden
                "signing_secret": "REDACTED",
                "interactive_message_enabled": True,
            },
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "app_token": "REDACTED",  # Secret field not marked as changed
                "slack_channel_id": "sid",
                "token": "REDACTED",  # Secret field not marked as changed
                "signing_secret": "REDACTED",
                "interactive_message_enabled": True,
            },
        ),
        # When fields are not found in "secret_fields_changed", the secret fields will
        # not be marked as changed
        (
            SlackChannel(
                name="ch1",
                application_link_url="app",
                slack_channel_id="sid",
                display_name="name",
                token="token",
                app_token="secret",
                interactive_message_enabled=True,
                __internal__=ResourceGraph(),
            ),
            False,
            {},
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "app_token": "REDACTED",  # Secret field is hidden
                "slack_channel_id": "sid",
                "token": "REDACTED",  # Secret field is hidden
                "signing_secret": "REDACTED",  # Secret field is hidden
                "interactive_message_enabled": True,
            },
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "app_token": "REDACTED",  # Secret field not marked as changed
                "slack_channel_id": "sid",
                "token": "REDACTED",  # Secret field not marked as changed
                "signing_secret": "REDACTED",  # Secret field not marked as changed
                "interactive_message_enabled": True,
            },
        ),
        # Using a channel that is not a Webhook channel with many secret fields, but
        # using the secret fields instead of the webhook URL field.
        # Only "token" is flagged as changed in the "secret_fields_changed".
        # Also setting "show_secrets" to True.
        (
            SlackChannel(
                name="ch1",
                application_link_url="app",
                slack_channel_id="sid",
                display_name="name",
                token="token",
                app_token="secret",
                interactive_message_enabled=True,
                __internal__=ResourceGraph(),
            ),
            True,
            {
                "token": True,
                "app_token": False,
            },
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "app_token": "secret",  # Secret field is shown
                "slack_channel_id": "sid",
                "token": "token",  # Secret field is shown
                "signing_secret": None,
                "interactive_message_enabled": True,
            },
            {
                "name": "ch1",
                "display_name": "name",
                "ignore_changes": False,
                "application_link_url": "app",
                "app_token": "secret",  # Secret field is shown
                "slack_channel_id": "sid",
                "token": "token",  # Secret field is shown
                "signing_secret": None,
                "interactive_message_enabled": True,
            },
        ),
        # Testing that flagging of changes of nested secrets works correctly.
        (
            SnowflakeCredential(
                name="c1",
                display_name="name",
                account="account",
                auth=SnowflakeCredentialUserPassword(
                    user="user",
                    password="password",
                ),
                warehouse="warehouse",
                role="role",
                __internal__=ResourceGraph(),
            ),
            False,
            {
                "auth": {
                    "user": False,
                    "password": True,
                },
            },
            {
                "name": "c1",
                "display_name": "name",
                "enable_catalog": False,
                "ignore_changes": False,
                "account": "account",
                "auth": {
                    "user": "user",
                    "password": "REDACTED",  # Secret field is redacted
                },
                "warehouse": "warehouse",
                "role": "role",
            },
            {
                "name": "c1",
                "display_name": "name",
                "enable_catalog": False,
                "ignore_changes": False,
                "account": "account",
                "auth": {
                    "user": "user",
                    # Secret field is marked as changed
                    "password": "REDACTED-PREVIOUS",
                },
                "warehouse": "warehouse",
                "role": "role",
            },
        ),
    ],
)
def test__create_resource_diff_object_should_diff_secrets_correctly(
    resource: Resource | Diffable | dict,
    show_secrets: bool,
    secret_fields_changed: dict[str, Any],
    expected_when_manifest: dict[str, object],
    expected_when_not_manifest: dict[str, object],
) -> None:
    actual_when_manifest = _create_resource_diff_object(
        resource,
        show_secrets=show_secrets,
        secret_fields_changed=secret_fields_changed,
        is_manifest=True,
    )
    assert actual_when_manifest == expected_when_manifest

    actual_when_not_manifest = _create_resource_diff_object(
        resource,
        show_secrets=show_secrets,
        secret_fields_changed=secret_fields_changed,
        is_manifest=False,
    )
    assert actual_when_not_manifest == expected_when_not_manifest
