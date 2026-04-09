from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PreprocessSummary:
    pages_processed: int
    average_skew_angle: float
    resized: bool
    denoise_applied: bool


def _to_grayscale(image: np.ndarray) -> np.ndarray:
    try:
        import cv2

        if image.ndim == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except Exception:
        if image.ndim == 2:
            return image
        return np.mean(image, axis=2).astype(np.uint8)


def _estimate_skew_angle(gray: np.ndarray) -> float:
    try:
        import cv2

        _, binary = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        points = cv2.findNonZero(binary)
        if points is None:
            return 0.0

        rect = cv2.minAreaRect(points)
        angle = float(rect[-1])
        if angle < -45:
            angle = 90 + angle
        elif angle > 45:
            angle = angle - 90
        return angle
    except Exception:
        return 0.0


def _deskew(gray: np.ndarray, angle: float) -> np.ndarray:
    if abs(angle) < 0.1:
        return gray

    try:
        import cv2

        h, w = gray.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(
            gray,
            matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
    except Exception:
        return gray


def _denoise(gray: np.ndarray) -> np.ndarray:
    try:
        import cv2

        return cv2.fastNlMeansDenoising(gray, None, 7, 7, 21)
    except Exception:
        return gray


def _normalize_size(gray: np.ndarray, target_long_edge: int = 1800) -> tuple[np.ndarray, bool]:
    h, w = gray.shape[:2]
    long_edge = max(h, w)
    if long_edge <= target_long_edge:
        return gray, False

    scale = target_long_edge / float(long_edge)
    new_w, new_h = int(w * scale), int(h * scale)

    try:
        import cv2

        resized = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized, True
    except Exception:
        return gray, False


def preprocess_document(pages: list[np.ndarray]) -> tuple[list[np.ndarray], PreprocessSummary]:
    processed_pages: list[np.ndarray] = []
    skew_angles: list[float] = []
    resized_any = False

    for page in pages:
        gray = _to_grayscale(page)
        angle = _estimate_skew_angle(gray)
        skew_angles.append(angle)

        deskewed = _deskew(gray, angle)
        denoised = _denoise(deskewed)
        normalized, resized = _normalize_size(denoised)
        resized_any = resized_any or resized
        processed_pages.append(normalized)

    avg_angle = sum(skew_angles) / len(skew_angles) if skew_angles else 0.0
    summary = PreprocessSummary(
        pages_processed=len(processed_pages),
        average_skew_angle=round(avg_angle, 4),
        resized=resized_any,
        denoise_applied=True,
    )
    return processed_pages, summary

def normalize_for_phase2_stub(_: bytes) -> dict[str, str]:
    # Phase 2A scaffold: this will be replaced by real OpenCV preprocessing in Phase 2B.
    return {
        "deskew": "pending",
        "denoise": "pending",
        "normalize": "pending",
    }
