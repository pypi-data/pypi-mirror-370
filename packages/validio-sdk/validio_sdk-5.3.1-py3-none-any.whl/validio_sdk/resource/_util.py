from dataclasses import dataclass
from typing import Any

from gql.transport.exceptions import TransportQueryError, TransportServerError

from validio_sdk.exception import ValidioError


@dataclass
class SourceSchemaReinference:
    source_names: set[str] | None

    def should_reinfer_schema_for_source(self, source_name: str) -> bool:
        if self.source_names is None:
            return False
        if len(self.source_names) == 0:  # ReInfer for all
            return True
        return source_name in self.source_names


def _sanitize_error(
    e: TransportQueryError | TransportServerError,
    show_secrets: bool,
) -> Exception:
    if show_secrets:
        return e

    code = ""
    if isinstance(e, TransportServerError):
        code = f" ({e.code})"

    raise ValidioError(
        f"API error{code}: The error message has been "
        "suppressed because it potentially contains sensitive information; "
        "If you would like to view the error message, run again with --show-secrets"
    )


def _rename_dict_key(d: dict[str, Any], from_key: str, to_key: str) -> None:
    if from_key not in d:
        return

    d[to_key] = d[from_key]
    del d[from_key]
