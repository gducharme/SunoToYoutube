from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime


@contextmanager
def process_clock(name: str | None = None):
    """Context manager to print start and end timestamps."""
    label = name or "process"
    start = datetime.now()
    print(f"{label} started at {start.isoformat(timespec='seconds')}")
    try:
        yield
    finally:
        end = datetime.now()
        print(f"{label} ended at {end.isoformat(timespec='seconds')} (duration {end - start})")

