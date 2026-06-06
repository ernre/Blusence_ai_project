"""Queue abstractions for local and production serving."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from queue import Queue
from uuid import uuid4

from vpe.types import TryOnRequest


@dataclass(frozen=True)
class InferenceJob:
    """Queued inference job."""

    job_id: str
    request: TryOnRequest


@dataclass
class JobStore:
    """In-memory status store for local development."""

    statuses: dict[str, dict[str, str]] = field(default_factory=dict)

    def set_status(self, job_id: str, status: str, output_path: Path | None = None) -> None:
        payload = {"status": status}
        if output_path is not None:
            payload["output_path"] = str(output_path)
        self.statuses[job_id] = payload


class MemoryInferenceQueue:
    """Thread-safe local queue used before Redis/RQ is configured."""

    def __init__(self, store: JobStore | None = None) -> None:
        self.store = store or JobStore()
        self._queue: Queue[InferenceJob] = Queue()

    def enqueue(self, request: TryOnRequest) -> str:
        job_id = str(uuid4())
        self.store.set_status(job_id, "queued")
        self._queue.put(InferenceJob(job_id=job_id, request=request))
        return job_id

    def get(self) -> InferenceJob:
        return self._queue.get()
