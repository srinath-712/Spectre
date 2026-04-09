from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any

import numpy as np

from api.models import AnalysisResult, JobState


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobState] = {}
        self._runtime_images: dict[str, np.ndarray] = {}
        self._lock = Lock()

    def create_job(self, job_id: str, filename: str, domain: str) -> JobState:
        now = datetime.now(timezone.utc)
        job = JobState(
            id=job_id,
            filename=filename,
            domain=domain,
            status="uploading",
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self._jobs[job_id] = job
        return job

    def update_status(self, job_id: str, status: str) -> JobState | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            updated = job.model_copy(
                update={
                    "status": status,
                    "updated_at": datetime.now(timezone.utc),
                }
            )
            self._jobs[job_id] = updated
            return updated

    def set_result(self, job_id: str, result: AnalysisResult) -> JobState | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            updated = job.model_copy(
                update={
                    "status": "completed",
                    "result": result,
                    "updated_at": datetime.now(timezone.utc),
                }
            )
            self._jobs[job_id] = updated
            return updated

    def set_runtime_image(self, job_id: str, image: np.ndarray) -> None:
        with self._lock:
            self._runtime_images[job_id] = image

    def get_runtime_image(self, job_id: str) -> np.ndarray | None:
        with self._lock:
            return self._runtime_images.get(job_id)

    def get_job(self, job_id: str) -> JobState | None:
        with self._lock:
            return self._jobs.get(job_id)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {key: value.model_dump() for key, value in self._jobs.items()}


job_store = JobStore()
