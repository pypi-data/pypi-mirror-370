from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from cli_arena.dataset.dataset import Dataset


class RunLock:
    """File lock to avoid concurrent runs on the same dataset."""

    def __init__(self, root: Path | str = ".arena-lock") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def acquire(self, dataset: Dataset) -> Iterator[Path]:
        lock_file = self.root / f"{dataset.config.name or 'local'}-{dataset.config.version or 'local'}.lock"
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            os.write(fd, b"locked")
            os.close(fd)
            try:
                yield lock_file
            finally:
                try:
                    lock_file.unlink(missing_ok=True)
                except Exception:
                    pass
        except FileExistsError:
            raise RuntimeError(f"Run already in progress for dataset lock: {lock_file}")
