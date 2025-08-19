"""Persistent configuration."""

import json
import os
from pathlib import Path

import platformdirs

from validio_sdk import ConfigInvalidError, ConfigNotFoundError
from validio_sdk.util import ClassJSONEncoder

CONFIG_PATH_ENV = "VALIDIO_CONFIG_PATH"
VALIDIO_ENDPOINT_ENV = "VALIDIO_ENDPOINT"
VALIDIO_ACCESS_KEY_ENV = "VALIDIO_ACCESS_KEY"
VALIDIO_SECRET_ACCESS_KEY_ENV = "VALIDIO_SECRET_ACCESS_KEY"


class ValidioConfig:
    """Representation of configuration to use in the Validio system and SDK."""

    def __init__(
        self,
        endpoint: str = "",
        access_key: str = "",
        access_secret: str = "",
        default_namespace: str = "default",
    ):
        """
        Constructor for `ValidioConfig`.

        Will ensure we can construct an object with the exposed property
        `access_secret`.
        """
        self.default_namespace = default_namespace
        self.endpoint = endpoint
        self.access_key = access_key
        self._access_secret = access_secret

    def asdict(self) -> dict[str, str]:
        """
        Return a dictionary representation of the class.

        This is used from our `ClassJSONEncoder` to ensure we save JSON
        representing the class with the external property names. By doing this
        we can also ensure that we can serialize the config by passing the JSON
        to the constructor.
        """
        return {
            "default_namespace": self.default_namespace,
            "endpoint": self.endpoint,
            "access_key": self.access_key,
            "access_secret": self._access_secret,
        }

    @staticmethod
    def _none_or_hidden(maybe_value: str | None) -> str:
        """
        Represent a hidden value but be explicit if unset.

        Will return fix length of asterisks for existing values but if no value
        exist a single dash is returned.
        """
        return "-" if maybe_value is None else "*****"

    @property
    def access_secret(self) -> str:  # noqa: D102 No reason to document property.
        return self._none_or_hidden(self._access_secret)

    @access_secret.setter
    def access_secret(self, value: str) -> None:
        self._access_secret = value

    def __repr__(self) -> str:
        """
        Representation of a `ValidioConfig`.

        Will ensure we don't print sensitive information.
        """
        return (
            f"{'Default namespace':<20} | {self.default_namespace}\n"
            f"{'Endpoint':<20} | {self.endpoint}\n"
            f"{'Access key':<20} | {self.access_key}\n"
            f"{'Access secret':<20} | {self._none_or_hidden(self.access_secret)}\n"
        )


class Config:
    """
    Config management.

    A class to work with configuration such as reading, writing and deleting.
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        """
        Creates a new instance of `Config`.

        :param config_dir: Optional directory where to put the config file. Will
            default to system default set by `platformdirs`.


        :returns: A `Config` instance.
        """
        if config_dir is None:
            config_dir = default_config_dir()

        self.config_path: Path = Path(config_dir, "config.json")
        self.validio_config: ValidioConfig | None = None

    def write(self, config: ValidioConfig) -> None:
        """
        Write the passed configuration to disk.

        This will fully overwrite the existing configuration, including any
        fields that's not a part of the `ValidioConfig`.

        :param config: A `ValidioConfig` object.
        """
        self.validio_config = config

        file_content = json.dumps(
            config, indent=2, sort_keys=True, cls=ClassJSONEncoder
        )

        self.config_path.write_text(file_content)

    def read(self) -> ValidioConfig:
        """
        Read persistent configuration.

        Will return `None` if no configuration is created yet.

        :returns: The configuration, or None
        :rtype: ValidioConfig | None
        :raises: ConfigNotFoundError if no configuration exists
        :raises: ConfigNotFoundError if the configuration is invalid
        """
        if self.validio_config is not None:
            return self.validio_config

        endpoint = os.getenv(VALIDIO_ENDPOINT_ENV, "")
        access_key = os.getenv(VALIDIO_ACCESS_KEY_ENV, "")
        access_secret = os.getenv(VALIDIO_SECRET_ACCESS_KEY_ENV, "")

        if not self.config_path.is_file():
            if not all([endpoint, access_key, access_secret]):
                raise ConfigNotFoundError(
                    VALIDIO_ENDPOINT_ENV,
                    VALIDIO_ACCESS_KEY_ENV,
                    VALIDIO_SECRET_ACCESS_KEY_ENV,
                )

            return ValidioConfig(
                endpoint=endpoint,
                access_key=access_key,
                access_secret=access_secret,
            )

        file_content = self.config_path.read_text()

        try:
            file_content_json = json.loads(file_content)
        except json.decoder.JSONDecodeError:
            raise ConfigInvalidError

        # Ensure we filter out the fields from the configuration that is
        # supported by ValidioConfig. We silently drop everything else.
        validio_config_fields = [x.lstrip("_") for x in list(vars(ValidioConfig()))]
        init_args = {
            k: v for k, v in file_content_json.items() if k in validio_config_fields
        }

        # Environment variables take precedence over configuration file.
        init_args["endpoint"] = endpoint or init_args["endpoint"]
        init_args["access_key"] = access_key or init_args["access_key"]
        init_args["access_secret"] = access_secret or init_args["access_secret"]

        try:
            return ValidioConfig(**init_args)
        except TypeError:
            raise ConfigInvalidError

    def remove(self) -> None:
        """Remove the configuration at the instance's `config_path`."""
        if self.config_path.is_file():
            self.config_path.unlink()

    def exists(self) -> bool:
        """Check if any configuration exist."""
        return self.validio_config is not None


def default_config_dir() -> Path:
    """Get the default config dir based on the OS."""
    env_path = os.getenv(CONFIG_PATH_ENV)
    if env_path is not None:
        return Path(env_path)

    config_dir = platformdirs.user_config_dir(
        appname="validio",
        appauthor="Validio AB",
        ensure_exists=True,
    )

    return Path(config_dir)
