from __future__ import annotations

from dataclasses import dataclass, field
from os import getenv
from pathlib import Path


def _parse_int(name: str, default: int) -> int:
    raw = getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _parse_list(name: str, default: list[str]) -> list[str]:
    raw = getenv(name)
    if raw is None or not raw.strip():
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = getenv("SPECTRE_APP_NAME", "Spectre API")
    app_version: str = getenv("SPECTRE_APP_VERSION", "0.1.0")
    api_prefix: str = getenv("SPECTRE_API_PREFIX", "/api")
    host: str = getenv("SPECTRE_HOST", "0.0.0.0")
    port: int = _parse_int("SPECTRE_PORT", 8000)
    max_upload_mb: int = _parse_int("SPECTRE_MAX_UPLOAD_MB", 20)
    max_pdf_pages: int = _parse_int("SPECTRE_MAX_PDF_PAGES", 5)
    pdf_render_dpi: int = _parse_int("SPECTRE_PDF_RENDER_DPI", 180)
    detector_max_workers: int = _parse_int("SPECTRE_DETECTOR_MAX_WORKERS", 4)
    detector_timeout_seconds: int = _parse_int("SPECTRE_DETECTOR_TIMEOUT_SECONDS", 8)
    detector_execution_engine: str = getenv("SPECTRE_DETECTOR_ENGINE", "thread")
    output_dir: Path = Path(getenv("SPECTRE_OUTPUT_DIR", "backend/output"))
    allowed_origins: list[str] = field(
        default_factory=lambda: _parse_list("SPECTRE_ALLOWED_ORIGINS", ["*"])
    )
    heuristic_only: bool = getenv("SPECTRE_HEURISTIC_ONLY", "false").lower() == "true"
    ocr_force_fallback: bool = getenv("SPECTRE_OCR_FORCE_FALLBACK", "false").lower() == "true"
    ml_model_dir: Path = Path(getenv("SPECTRE_MODEL_DIR", "backend/models"))

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


settings = Settings()
