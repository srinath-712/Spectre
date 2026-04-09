from __future__ import annotations

from pathlib import Path

from core.config import settings


def ensure_runtime_dirs() -> None:
    output_root = settings.output_dir
    reports_dir = output_root / "reports"
    artifacts_dir = output_root / "artifacts"

    for path in (output_root, reports_dir, artifacts_dir):
        Path(path).mkdir(parents=True, exist_ok=True)
