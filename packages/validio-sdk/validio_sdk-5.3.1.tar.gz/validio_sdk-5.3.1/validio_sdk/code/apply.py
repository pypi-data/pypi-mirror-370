"""Apply command implementation."""

from validio_sdk._api.api import APIClient
from validio_sdk.code._progress import ProgressBar
from validio_sdk.resource._diff import GraphDiff
from validio_sdk.resource._resource import DiffContext
from validio_sdk.resource._server_resources import apply_updates_on_server


async def apply(
    namespace: str,
    client: APIClient,
    ctx: DiffContext,
    diff: GraphDiff,
    show_secrets: bool,
    show_progress: bool = True,
    dry_run_sql: bool = False,
    test_credentials: bool = True,
) -> None:
    """Applies the provided diff operations on the server."""
    progress_bar = ProgressBar(
        description="Applying changes",
        total=diff.num_operations(),
        show_progress=show_progress,
    )
    with progress_bar:
        async with client.client as session:
            await apply_updates_on_server(
                namespace,
                ctx,
                diff,
                session,
                show_secrets,
                progress_bar,
                dry_run_sql,
                test_credentials,
            )
