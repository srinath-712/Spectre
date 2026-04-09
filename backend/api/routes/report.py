from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from core.config import settings
from core.job_store import job_store
from output.report import generate_forensic_report

router = APIRouter()


@router.get("/report/{job_id}")
async def get_report(job_id: str) -> FileResponse:
    job = job_store.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job.result is None:
        raise HTTPException(status_code=409, detail="Report is not ready until analysis completes.")

    reports_dir = settings.output_dir / "reports"
    report_path = reports_dir / f"{job_id}.pdf"
    generate_forensic_report(report_path=report_path, result=job.result, filename=job.filename)

    return FileResponse(
        path=report_path,
        media_type="application/pdf",
        filename=f"spectre_report_{job_id}.pdf",
    )
