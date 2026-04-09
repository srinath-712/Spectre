from __future__ import annotations

import logging
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass

import numpy as np

from api.models import Finding
from core.config import settings
from detection.base import DetectorContext
from detection.registry import create_detector, detector_names

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DetectorFailure:
    detector: str
    reason: str


@dataclass(frozen=True)
class DetectorRunResult:
    findings: list[Finding]
    failures: list[DetectorFailure]


def _run_detector(detector_name: str, image: np.ndarray, domain: str) -> list[Finding]:
    detector = create_detector(detector_name)
    context = DetectorContext(image=image, domain=domain)
    return detector.detect(context)


def run_detectors(
    image: np.ndarray,
    domain: str,
    selected_detectors: list[str] | None = None,
) -> DetectorRunResult:
    names = selected_detectors or detector_names()
    findings: list[Finding] = []
    failures: list[DetectorFailure] = []

    if not names:
        return DetectorRunResult(findings=[], failures=[])

    engine = settings.detector_execution_engine.lower()
    if engine == "process":
        executor_cls = ProcessPoolExecutor
    else:
        executor_cls = ThreadPoolExecutor

    future_map: dict[Future[list[Finding]], str] = {}
    max_workers = max(1, min(settings.detector_max_workers, len(names)))

    with executor_cls(max_workers=max_workers) as executor:
        for name in names:
            future = executor.submit(_run_detector, name, image, domain)
            future_map[future] = name

        for future, name in future_map.items():
            try:
                detector_findings = future.result(timeout=settings.detector_timeout_seconds)
                findings.extend(detector_findings)
            except TimeoutError:
                failures.append(
                    DetectorFailure(
                        detector=name,
                        reason=f"Timed out after {settings.detector_timeout_seconds}s",
                    )
                )
            except Exception as exc:
                failures.append(DetectorFailure(detector=name, reason=str(exc)))

    if failures:
        logger.warning(
            "detector_failures count=%s details=%s",
            len(failures),
            [f"{item.detector}:{item.reason}" for item in failures],
        )

    return DetectorRunResult(findings=findings, failures=failures)
