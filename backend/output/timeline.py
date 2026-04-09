from __future__ import annotations

from api.models import Finding, TimelineStep

_TYPE_ORDER = {
    'erasure': 1,
    'copy_paste': 2,
    'overwrite': 3,
    'added_content': 4,
    'spacing': 5,
    'watermark': 6,
    'merged': 7,
    'ai_edit': 8,
    'ai_generated': 9,
}


def reconstruct_timeline(findings: list[Finding]) -> list[TimelineStep]:
    if not findings:
        return [
            TimelineStep(
                id='t1',
                order=1,
                description='No tamper sequence inferred from current detector outputs.',
                timestamp_offset='T+0s',
            )
        ]

    ordered = sorted(
        findings,
        key=lambda f: (_TYPE_ORDER.get(f.type, 99), -f.confidence),
    )

    timeline: list[TimelineStep] = []
    for idx, finding in enumerate(ordered[:8], start=1):
        label = finding.type.replace('_', ' ').title()
        timeline.append(
            TimelineStep(
                id=f't{idx}',
                order=idx,
                description=f'{label} inferred at region {finding.region_id} ({finding.severity} severity).',
                timestamp_offset=f'T+{idx * 5}s',
            )
        )
    return timeline
