from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.models import AdversarialRequest, AdversarialResponse
from core.job_store import job_store
from detection.orchestrator import run_detectors
from fusion.engine import derive_verdict_and_confidence, fuse_findings
from output.adversarial import apply_attack

router = APIRouter()


@router.post("/adversarial", response_model=AdversarialResponse)
async def adversarial_retest(payload: AdversarialRequest) -> AdversarialResponse:
    job = job_store.get_job(payload.job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job.result is None:
        raise HTTPException(status_code=409, detail="Adversarial retest requires completed analysis.")

    runtime_image = job_store.get_runtime_image(payload.job_id)
    if runtime_image is None:
        raise HTTPException(status_code=409, detail="No runtime image available for adversarial replay.")

    attacked_image = apply_attack(runtime_image, payload.attack_type)
    detector_result = run_detectors(image=attacked_image, domain=job.domain)
    fused_findings, _ = fuse_findings(detector_result.findings)
    verdict, confidence = derive_verdict_and_confidence(fused_findings)

    before_count = len(job.result.findings)
    after_count = len(fused_findings)

    return AdversarialResponse(
        attack_type=payload.attack_type,
        delta_summary=[
            f"Findings count changed from {before_count} to {after_count}.",
            f"Post-attack verdict: {verdict} ({confidence:.2f}).",
        ],
        findings_after_attack=fused_findings,
    )
