# =============================================================================
# Job Store — in-memory UUID-keyed job storage
# =============================================================================
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from schemas.mto import JobStatus, MTOResponse


@dataclass
class Job:
    job_id: str
    status: JobStatus = JobStatus.PENDING
    progress: int = 0
    current_step: str = "Queued"
    mock: bool = False
    provider_requested: Optional[str] = None
    fallback: bool = False
    created_at: float = field(default_factory=time.time)
    processing_time_ms: Optional[int] = None
    result: Optional[MTOResponse] = None
    error: Optional[str] = None

    def elapsed_ms(self) -> int:
        return int((time.time() - self.created_at) * 1000)


class JobStore:
    """Thread-safe in-memory job storage.

    Sufficient for single-user assessment. For production, replace with
    Redis + Celery or a database-backed store.
    """

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def create(self) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(job_id=job_id)
        self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def update(self, job_id: str, **kwargs) -> Optional[Job]:
        job = self._jobs.get(job_id)
        if job is None:
            return None
        for key, value in kwargs.items():
            setattr(job, key, value)
        return job

    def all_jobs(self) -> list[Job]:
        return list(self._jobs.values())


# Module-level singleton — shared across the FastAPI app
job_store = JobStore()
