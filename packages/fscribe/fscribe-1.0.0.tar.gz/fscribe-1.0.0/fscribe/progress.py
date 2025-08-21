from typing import Optional

from tqdm import tqdm

from .interfaces import IProgressReporter


class ConsoleProgressReporter(IProgressReporter):
    def __init__(self) -> None:
        self._progress_bar: Optional[tqdm] = None

    def start_progress(self, total_items: int, description: str) -> None:
        self._progress_bar = tqdm(total=total_items, desc=description, unit="file")

    def update_progress(self, increment: int = 1) -> None:
        if self._progress_bar:
            self._progress_bar.update(increment)

    def finish_progress(self) -> None:
        if self._progress_bar:
            self._progress_bar.close()
            self._progress_bar = None


class SilentProgressReporter(IProgressReporter):
    def start_progress(self, total_items: int, description: str) -> None:
        pass

    def update_progress(self, increment: int = 1) -> None:
        pass

    def finish_progress(self) -> None:
        pass
