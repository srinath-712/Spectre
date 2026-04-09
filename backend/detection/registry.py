from __future__ import annotations

from detection.base import BaseDetector
from detection.modules import (
    AIGeneratedDetector,
    AddedContentDetector,
    CopyPasteDetector,
    DocumentMergeDetector,
    ErasureDetector,
    OverwriteDetector,
    PartialAIEditDetector,
    SpacingIrregularityDetector,
    WatermarkRemovalDetector,
)

_DETECTOR_TYPES: dict[str, type[BaseDetector]] = {
    CopyPasteDetector.name: CopyPasteDetector,
    OverwriteDetector.name: OverwriteDetector,
    AddedContentDetector.name: AddedContentDetector,
    ErasureDetector.name: ErasureDetector,
    DocumentMergeDetector.name: DocumentMergeDetector,
    WatermarkRemovalDetector.name: WatermarkRemovalDetector,
    SpacingIrregularityDetector.name: SpacingIrregularityDetector,
    AIGeneratedDetector.name: AIGeneratedDetector,
    PartialAIEditDetector.name: PartialAIEditDetector,
}


def detector_names() -> list[str]:
    return list(_DETECTOR_TYPES.keys())


def create_detector(name: str) -> BaseDetector:
    detector_type = _DETECTOR_TYPES.get(name)
    if detector_type is None:
        raise ValueError(f"Unknown detector: {name}")
    return detector_type()
