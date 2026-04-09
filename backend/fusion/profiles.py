from __future__ import annotations

from dataclasses import dataclass

from api.models import Domain


@dataclass(frozen=True)
class DomainProfile:
    domain: Domain
    iou_threshold: float
    tampered_threshold: float
    suspicious_threshold: float
    detector_weights: dict[str, float]


_PROFILES: dict[str, DomainProfile] = {
    'medical': DomainProfile(
        domain='medical',
        iou_threshold=0.32,
        tampered_threshold=0.74,
        suspicious_threshold=0.46,
        detector_weights={
            'added_content': 1.18,
            'ai_edit': 1.22,
            'overwrite': 1.10,
            'copy_paste': 1.06,
        },
    ),
    'financial': DomainProfile(
        domain='financial',
        iou_threshold=0.36,
        tampered_threshold=0.78,
        suspicious_threshold=0.49,
        detector_weights={
            'copy_paste': 1.20,
            'spacing': 1.15,
            'overwrite': 1.14,
            'watermark': 1.08,
        },
    ),
    'legal': DomainProfile(
        domain='legal',
        iou_threshold=0.38,
        tampered_threshold=0.80,
        suspicious_threshold=0.52,
        detector_weights={
            'spacing': 1.20,
            'merged': 1.12,
            'copy_paste': 1.10,
            'ai_generated': 1.08,
        },
    ),
    'id': DomainProfile(
        domain='id',
        iou_threshold=0.30,
        tampered_threshold=0.72,
        suspicious_threshold=0.44,
        detector_weights={
            'ai_generated': 1.24,
            'ai_edit': 1.20,
            'erasure': 1.10,
            'added_content': 1.12,
        },
    ),
}


def get_profile(domain: str) -> DomainProfile:
    return _PROFILES.get(domain, _PROFILES['medical'])
