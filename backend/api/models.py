from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


TamperType = Literal[
    "copy_paste",
    "overwrite",
    "added_content",
    "erasure",
    "merged",
    "watermark",
    "spacing",
    "ai_generated",
    "ai_edit",
]
Domain = Literal['medical', 'financial', 'legal', 'id']

Severity = Literal["low", "medium", "high"]
Verdict = Literal["Authentic", "Suspicious", "Tampered"]
JobStatus = Literal["uploading", "processing", "completed", "error"]


class BoundingBox(BaseModel):
    x: float
    y: float
    w: float
    h: float


class Finding(BaseModel):
    region_id: str
    bbox: BoundingBox
    type: TamperType
    confidence: float = Field(ge=0.0, le=1.0)
    signals: list[str]
    severity: Severity
    description: str


class TimelineStep(BaseModel):
    id: str
    order: int
    description: str
    timestamp_offset: str | None = None


class DocumentDNA(BaseModel):
    dna_id: str
    hash: str
    scanner_profile: str
    matched_known: bool


class AnalysisResult(BaseModel):
    status: JobStatus
    job_id: str
    findings: list[Finding]
    heatmap_url: str | None = None
    verdict: Verdict
    overall_confidence: float = Field(ge=0.0, le=1.0)
    timeline: list[TimelineStep]
    dna: DocumentDNA


class ResultResponse(BaseModel):
    status: JobStatus
    findings: list[Finding]
    heatmap_url: str | None = None
    verdict: Verdict | None = None
    overall_confidence: float | None = None
    timeline: list[TimelineStep] = []
    dna: DocumentDNA | None = None


class AnalyzeResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobState(BaseModel):
    id: str
    filename: str
    domain: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    result: AnalysisResult | None = None


class FingerprintResponse(BaseModel):
    dna_id: str
    hash: str


class CompareResponse(BaseModel):
    delta: list[str]
    changed_regions: list[str]


class AdversarialRequest(BaseModel):
    job_id: str
    attack_type: Literal[
        "jpeg_recompress",
        "gaussian_noise",
        "geometric_warp",
        "downsample_upsample",
        "color_jitter",
    ]


class AdversarialResponse(BaseModel):
    attack_type: str
    delta_summary: list[str]
    findings_after_attack: list[Finding]
