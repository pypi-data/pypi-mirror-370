from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)


# ProgressBar is a wrapper around the rich progress bar library.
# It requires initial description of the task (can be updated later) and total
# number of steps.
class ProgressBar:
    def __init__(
        self, description: str, total: int, show_progress: bool = True
    ) -> None:
        self.show_progress = show_progress
        self.progress_bar = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            disable=not self.show_progress,
        )
        self.task_id = self.progress_bar.add_task(
            description,
            total=total,
        )

    # Update the progress bar with advancement and/or new description.
    # Once the total number of steps is reached, the progress bar won't get
    # updated anymore.
    def update(
        self, *, advance: int | None = None, description: str | None = None
    ) -> None:
        if not self.progress_bar.finished:
            self.progress_bar.update(
                self.task_id, advance=advance, description=description
            )

    def __enter__(self) -> None:
        self.progress_bar.start()

    def __exit__(self, *args) -> None:  # type: ignore
        self.progress_bar.stop()
