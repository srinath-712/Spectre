from __future__ import annotations

import logging
import shutil
from typing import Final

from core.config import settings

logger = logging.getLogger(__name__)

def _check_ocr_availability() -> bool:
    if settings.ocr_force_fallback:
        logger.info("OCR forced fallback via configuration.")
        return False
        
    tesseract_path = shutil.which("tesseract")
    if tesseract_path is None:
        logger.warning("Tesseract binary not found in PATH. Defaulting to OCR fallback mode.")
        return False
        
    try:
        import pytesseract
        logger.info(f"OCR availability verified. Tesseract binary found at {tesseract_path}.")
        return True
    except ImportError:
        logger.warning("pytesseract package not installed. Defaulting to OCR fallback mode.")
        return False

# Global flag accessible by detectors
OCR_AVAILABLE: Final[bool] = _check_ocr_availability()
