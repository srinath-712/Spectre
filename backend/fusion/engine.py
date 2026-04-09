from __future__ import annotations

import math
from dataclasses import dataclass

from api.models import BoundingBox, Finding
from fusion.profiles import get_profile


@dataclass(frozen=True)
class FusionSummary:
    input_count: int
    output_count: int


def _iou(a: BoundingBox, b: BoundingBox) -> float:
    ax2 = a.x + a.w
    ay2 = a.y + a.h
    bx2 = b.x + b.w
    by2 = b.y + b.h

    inter_x1 = max(a.x, b.x)
    inter_y1 = max(a.y, b.y)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = max(1.0, a.w * a.h)
    area_b = max(1.0, b.w * b.h)
    union = area_a + area_b - inter_area
    if union <= 0:
        return 0.0
    return inter_area / union


def _sigmoid_calibrate(score: float) -> float:
    calibrated = 1.0 / (1.0 + math.exp(-((score - 0.55) * 5.4)))
    return float(max(0.01, min(0.99, calibrated)))


def _severity_from_confidence(confidence: float) -> str:
    if confidence >= 0.82:
        return "high"
    if confidence >= 0.62:
        return "medium"
    return "low"


def _merge_bbox(boxes: list[BoundingBox]) -> BoundingBox:
    x1 = min(box.x for box in boxes)
    y1 = min(box.y for box in boxes)
    x2 = max(box.x + box.w for box in boxes)
    y2 = max(box.y + box.h for box in boxes)
    return BoundingBox(x=x1, y=y1, w=x2 - x1, h=y2 - y1)


def fuse_findings(
    findings: list[Finding],
    domain: str = "medical",
    iou_threshold: float = 0.35,
) -> tuple[list[Finding], FusionSummary]:
    if not findings:
        return [], FusionSummary(input_count=0, output_count=0)

    profile = get_profile(domain)
    threshold = profile.iou_threshold if iou_threshold == 0.35 else iou_threshold

    weighted_inputs: list[Finding] = []
    for finding in findings:
        weight = profile.detector_weights.get(finding.type, 1.0)
        weighted_confidence = max(0.0, min(0.99, finding.confidence * weight))
        weighted_inputs.append(
            finding.model_copy(
                update={
                    "confidence": weighted_confidence,
                    "severity": _severity_from_confidence(weighted_confidence),
                }
            )
        )

    by_type: dict[str, list[Finding]] = {}
    for finding in weighted_inputs:
        by_type.setdefault(finding.type, []).append(finding)

    fused: list[Finding] = []
    for finding_type, typed_findings in by_type.items():
        ordered = sorted(typed_findings, key=lambda item: item.confidence, reverse=True)
        consumed: set[int] = set()

        for idx, seed in enumerate(ordered):
            if idx in consumed:
                continue

            cluster: list[Finding] = [seed]
            consumed.add(idx)

            for j in range(idx + 1, len(ordered)):
                if j in consumed:
                    continue
                candidate = ordered[j]
                if _iou(seed.bbox, candidate.bbox) >= threshold:
                    cluster.append(candidate)
                    consumed.add(j)

            avg_confidence = sum(item.confidence for item in cluster) / len(cluster)
            calibrated = _sigmoid_calibrate(avg_confidence)

            merged_signals: list[str] = []
            for item in cluster:
                merged_signals.extend(item.signals)
            dedup_signals = list(dict.fromkeys(merged_signals))[:4]
            merged_bbox = _merge_bbox([item.bbox for item in cluster])

            fused.append(
                Finding(
                    region_id=seed.region_id,
                    bbox=merged_bbox,
                    type=finding_type,
                    confidence=calibrated,
                    signals=dedup_signals,
                    severity=_severity_from_confidence(calibrated),
                    description=seed.description,
                )
            )

    fused_sorted = sorted(fused, key=lambda item: item.confidence, reverse=True)
    return fused_sorted, FusionSummary(input_count=len(weighted_inputs), output_count=len(fused_sorted))


def derive_verdict_and_confidence(findings: list[Finding], domain: str = "medical") -> tuple[str, float]:
    if not findings:
        return "Authentic", 0.09

    profile = get_profile(domain)

    avg = sum(item.confidence for item in findings) / len(findings)
    peak = max(item.confidence for item in findings)
    score = float(max(avg, peak * 0.92))

    if score >= profile.tampered_threshold:
        return "Tampered", round(score, 4)
    if score >= profile.suspicious_threshold:
        return "Suspicious", round(score, 4)
    return "Authentic", round(score, 4)
