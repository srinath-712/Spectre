from __future__ import annotations

from api.models import DocumentDNA, Finding, TimelineStep
from output.dna import build_dna_id, hash_payload, scanner_profile_from_image
from output.heatmap import generate_heatmap_data_url
from output.timeline import reconstruct_timeline


def build_output_artifacts(
    *,
    payload: bytes,
    processed_image,
    findings: list[Finding],
) -> tuple[str | None, list[TimelineStep], DocumentDNA]:
    digest = hash_payload(payload)
    heatmap_url = generate_heatmap_data_url(processed_image, findings)
    timeline = reconstruct_timeline(findings)
    dna = DocumentDNA(
        dna_id=build_dna_id(digest),
        hash=digest,
        scanner_profile=scanner_profile_from_image(processed_image),
        matched_known=False,
    )
    return heatmap_url, timeline, dna
