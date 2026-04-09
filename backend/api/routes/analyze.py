from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.models import AnalyzeResponse
from core.ingestion import ingest_document, read_upload_bytes
from core.job_store import job_store
from core.mock_data import build_result_from_findings
from core.preprocessing import preprocess_document
from detection.orchestrator import run_detectors
from fusion.engine import derive_verdict_and_confidence, fuse_findings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_document(
    file: UploadFile = File(...),
    domain: str = Form(...),
) -> AnalyzeResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")

    if not (file.content_type == "application/pdf" or str(file.content_type).startswith("image/")):
        raise HTTPException(status_code=415, detail="Only PDF and image uploads are supported.")

    job_id = f"job_{uuid4().hex[:12]}"
    job_store.create_job(job_id=job_id, filename=file.filename, domain=domain)
    job_store.update_status(job_id, "processing")

    try:
        payload = await read_upload_bytes(file)
    except ValueError as exc:
        job_store.update_status(job_id, "error")
        raise HTTPException(status_code=413, detail=str(exc)) from exc

    try:
        ingested = ingest_document(payload, filename=file.filename, content_type=file.content_type)
        processed_pages, preprocess_summary = preprocess_document(ingested.pages)
        logger.info(
            "analysis_preprocessed job_id=%s source_type=%s pages=%s ingested_pages=%s avg_skew=%s resized=%s",
            job_id,
            ingested.source_type,
            ingested.page_count,
            ingested.ingested_pages,
            preprocess_summary.average_skew_angle,
            preprocess_summary.resized,
        )

        detector_result = run_detectors(image=processed_pages[0], domain=domain)
        fused_findings, fusion_summary = fuse_findings(detector_result.findings, domain=domain)
        verdict, overall_confidence = derive_verdict_and_confidence(fused_findings, domain=domain)
        logger.info(
            "analysis_detectors job_id=%s findings=%s fused=%s failures=%s verdict=%s confidence=%s",
            job_id,
            len(detector_result.findings),
            fusion_summary.output_count,
            len(detector_result.failures),
            verdict,
            overall_confidence,
        )
    except RuntimeError as exc:
        job_store.update_status(job_id, "error")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        job_store.update_status(job_id, "error")
        raise HTTPException(status_code=422, detail=f"Failed to process document: {exc}") from exc

    result = build_result_from_findings(
        job_id=job_id,
        filename=file.filename,
        payload=payload,
        processed_image=processed_pages[0],
        findings=fused_findings,
        verdict=verdict,
        overall_confidence=overall_confidence,
    )
    job_store.set_runtime_image(job_id, processed_pages[0])
    job_store.set_result(job_id, result)

    return AnalyzeResponse(job_id=job_id, status="completed")
