from __future__ import annotations

from hashlib import sha256
from typing import cast

import numpy as np

from api.models import AnalysisResult, BoundingBox, DocumentDNA, Finding, Verdict
from output.engine import build_output_artifacts


def _mock_findings() -> list[Finding]:
    return [
        Finding(
            region_id="r001",
            bbox=BoundingBox(x=120, y=340, w=200, h=45),
            type="copy_paste",
            confidence=0.94,
            signals=["ELA artifact mismatch", "SIFT keypoint repetition"],
            severity="high",
            description="Duplicate text texture found in patient identifier zone.",
        ),
        Finding(
            region_id="r002",
            bbox=BoundingBox(x=460, y=670, w=170, h=52),
            type="ai_edit",
            confidence=0.83,
            signals=["Local FFT spectrum drift", "Kerning deviation spike"],
            severity="medium",
            description="Localized edit artifact near signature and approval stamp.",
        ),
    ]


def build_mock_result(job_id: str, filename: str) -> AnalysisResult:
    digest = sha256(f"{job_id}:{filename}".encode("utf-8")).hexdigest()
    dna = DocumentDNA(
        dna_id=f"DNA-{digest[:8].upper()}",
        hash=digest,
        scanner_profile="noise-profile-v1",
        matched_known=False,
    )

    return AnalysisResult(
        status="completed",
        job_id=job_id,
        findings=_mock_findings(),
        heatmap_url=None,
        verdict="Tampered",
        overall_confidence=0.89,
        timeline=[],
        dna=dna,
    )


def build_result_from_findings(
    *,
    job_id: str,
    filename: str,
    payload: bytes,
    processed_image: np.ndarray,
    findings: list[Finding],
    verdict: str,
    overall_confidence: float,
) -> AnalysisResult:
    heatmap_url, timeline, dna = build_output_artifacts(
        payload=payload,
        processed_image=processed_image,
        findings=findings,
    )

    return AnalysisResult(
        status="completed",
        job_id=job_id,
        findings=findings,
        heatmap_url=heatmap_url,
        verdict=cast(Verdict, verdict),
        overall_confidence=overall_confidence,
        timeline=timeline,
        dna=dna,
    )
