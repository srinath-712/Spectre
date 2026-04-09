from __future__ import annotations

import base64
from io import BytesIO

import numpy as np

from api.models import Finding


def _to_uint8_gray(image: np.ndarray) -> np.ndarray:
    arr = image.astype(np.float32)
    if arr.ndim == 3:
        arr = np.mean(arr, axis=2)
    arr = arr - np.min(arr)
    maxv = np.max(arr)
    if maxv > 0:
        arr = arr / maxv
    return (arr * 255.0).astype(np.uint8)


def generate_heatmap_data_url(image: np.ndarray, findings: list[Finding]) -> str | None:
    if image.size == 0:
        return None

    gray = _to_uint8_gray(image)
    h, w = gray.shape
    score_map = np.zeros((h, w), dtype=np.float32)

    for finding in findings:
        x1 = max(0, int(finding.bbox.x))
        y1 = max(0, int(finding.bbox.y))
        x2 = min(w, int(finding.bbox.x + finding.bbox.w))
        y2 = min(h, int(finding.bbox.y + finding.bbox.h))
        if x2 <= x1 or y2 <= y1:
            continue
        score_map[y1:y2, x1:x2] += float(finding.confidence)

    if np.max(score_map) <= 1e-8:
        score_map += 0.01

    try:
        import cv2

        blur_size = max(11, int(min(h, w) * 0.06))
        if blur_size % 2 == 0:
            blur_size += 1

        smooth = cv2.GaussianBlur(score_map, (blur_size, blur_size), 0)
        norm = cv2.normalize(smooth, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        heat = cv2.applyColorMap(norm, cv2.COLORMAP_TURBO)
        base = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        overlay = cv2.addWeighted(base, 0.55, heat, 0.45, 0)

        success, encoded = cv2.imencode('.png', overlay)
        if not success:
            return None
        payload = encoded.tobytes()
    except Exception:
        from PIL import Image

        # Fallback: grayscale preview if OpenCV colormap is unavailable.
        pil_img = Image.fromarray(gray)
        buf = BytesIO()
        pil_img.save(buf, format='PNG')
        payload = buf.getvalue()

    b64 = base64.b64encode(payload).decode('ascii')
    return f"data:image/png;base64,{b64}"
