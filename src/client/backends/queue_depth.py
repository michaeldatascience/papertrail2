"""Process-local VLM concurrency gate."""

from __future__ import annotations

from contextlib import contextmanager
from threading import BoundedSemaphore

from src.config import get_settings


_capacity = 0
_semaphore: BoundedSemaphore | None = None


def configure_from_settings() -> None:
    global _capacity, _semaphore
    capacity = int(get_settings().vlm.max_concurrent_requests)
    if capacity == _capacity:
        return
    _capacity = capacity
    _semaphore = BoundedSemaphore(capacity) if capacity > 0 else None


@contextmanager
def vlm_queue_slot():
    sem = _semaphore
    if sem is None:
        yield
        return
    sem.acquire()
    try:
        yield
    finally:
        sem.release()
