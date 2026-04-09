from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.models import ResultResponse
from core.job_store import job_store

router = APIRouter()


@router.get("/result/{job_id}", response_model=ResultResponse)
async def get_result(job_id: str) -> ResultResponse:
    job = job_store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job.result is None:
        return ResultResponse(status=job.status, findings=[])

    return ResultResponse(
        status=job.result.status,
        findings=job.result.findings,
        heatmap_url=job.result.heatmap_url,
        verdict=job.result.verdict,
        overall_confidence=job.result.overall_confidence,
        timeline=job.result.timeline,
        dna=job.result.dna,
    )
