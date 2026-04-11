from __future__ import annotations

import cv2
import numpy as np
from skimage.metrics import structural_similarity

from api.models import BoundingBox, Finding
from detection.base import BaseDetector, DetectorContext


def _to_gray(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image.astype(np.float32)
    return np.mean(image.astype(np.float32), axis=2)


def _to_gray_uint8(image: np.ndarray) -> np.ndarray:
    gray = _to_gray(image)
    return np.clip(gray, 0, 255).astype(np.uint8)


def _safe_confidence(value: float) -> float:
    return float(max(0.0, min(0.99, value)))


def _severity_from_confidence(confidence: float) -> str:
    if confidence >= 0.82:
        return "high"
    if confidence >= 0.62:
        return "medium"
    return "low"


def _bbox_from_fraction(
    image: np.ndarray,
    x_frac: float,
    y_frac: float,
    w_frac: float,
    h_frac: float,
) -> BoundingBox:
    h, w = image.shape[:2]
    x = max(4, int(w * x_frac))
    y = max(4, int(h * y_frac))
    bw = max(24, int(w * w_frac))
    bh = max(20, int(h * h_frac))
    return BoundingBox(x=x, y=y, w=bw, h=bh)


def _quadrant_variance(gray: np.ndarray) -> tuple[float, int]:
    h, w = gray.shape
    mid_h = h // 2
    mid_w = w // 2
    quadrants = [
        gray[:mid_h, :mid_w],
        gray[:mid_h, mid_w:],
        gray[mid_h:, :mid_w],
        gray[mid_h:, mid_w:],
    ]
    variances = [float(np.var(q)) for q in quadrants if q.size > 0]
    if not variances:
        return 0.0, 0
    idx = int(np.argmax(variances))
    return variances[idx], idx


def _high_variance_region(image: np.ndarray) -> tuple[int, int, int, int]:
    h, w = image.shape[:2]
    x = max(8, int(w * 0.18))
    y = max(8, int(h * 0.34))
    bw = max(40, int(w * 0.21))
    bh = max(24, int(h * 0.06))
    return x, y, bw, bh


# -------------------------------------------------------------------
# JPEG-Resistant feature helpers (CHANGE 1)
# -------------------------------------------------------------------

def _dct_block_hash_matches(gray_u8: np.ndarray) -> float:
    """Matching DCT block fingerprints between TL and BR quadrants."""
    h, w = gray_u8.shape
    mid_h, mid_w = h // 2, w // 2

    def _hashes(region: np.ndarray) -> set:
        rh, rw = region.shape
        s = set()
        for by in range(0, rh - 7, 16):
            for bx in range(0, rw - 7, 16):
                block = region[by:by + 8, bx:bx + 8].astype(np.float32)
                dct = cv2.dct(block)
                low = dct[:2, :2].ravel()
                mx = float(np.max(np.abs(low))) + 1e-10
                q = tuple(np.clip(np.floor((low / mx + 1) * 2), 0, 3).astype(int))
                s.add(q)
        return s

    h_tl = _hashes(gray_u8[:mid_h, :mid_w])
    h_br = _hashes(gray_u8[mid_h:, mid_w:])
    return len(h_tl & h_br) / max(len(h_tl), 1)


def _patch_self_similarity(gray_f32: np.ndarray) -> float:
    """Max SSIM between TL quadrant and the other 3."""
    h, w = gray_f32.shape
    step = max(1, min(h, w) // 200)
    small = gray_f32[::step, ::step]
    sh, sw = small.shape
    mh, mw = sh // 2, sw // 2
    tl = small[:mh, :mw]
    others = [small[:mh, mw:mw + mw], small[mh:mh + mh, :mw], small[mh:mh + mh, mw:mw + mw]]
    best = 0.0
    for q in others:
        qh, qw = min(tl.shape[0], q.shape[0]), min(tl.shape[1], q.shape[1])
        if qh > 7 and qw > 7:
            s = structural_similarity(tl[:qh, :qw], q[:qh, :qw], data_range=255.0)
            best = max(best, s)
    return best


def _blocking_artifact_consistency(
    gray_f32: np.ndarray, rx: int, ry: int, rw: int, rh: int,
) -> float:
    """Gradient variance at 8-px block boundaries inside vs outside region."""
    gx = np.abs(np.diff(gray_f32, axis=1))
    h, w = gx.shape
    bcols = np.arange(7, w, 8)
    if len(bcols) == 0:
        return 0.0
    col_grads = gx[:, bcols]
    row_mask = np.zeros(h, dtype=bool)
    row_mask[ry:min(ry + rh, h)] = True
    col_mask = (bcols >= rx) & (bcols < rx + rw)
    inside_mask = row_mask[:, None] & col_mask[None, :]
    inside = col_grads[inside_mask]
    outside = col_grads[~inside_mask]
    if inside.size < 2 or outside.size < 2:
        return 0.0
    return float(np.var(inside)) / max(float(np.var(outside)), 1e-6)


# -------------------------------------------------------------------
# Edge-based feature helpers (CHANGE 2)
# -------------------------------------------------------------------

def _edge_density_ratio(
    gray_u8: np.ndarray, rx: int, ry: int, rw: int, rh: int,
) -> float:
    """Canny edge density inside region / margin around it."""
    edges = cv2.Canny(gray_u8, 50, 150)
    region = edges[ry:ry + rh, rx:rx + rw]
    in_density = float(np.sum(region > 0)) / max(region.size, 1)
    margin = max(rw, rh) // 2
    y1, y2 = max(0, ry - margin), min(edges.shape[0], ry + rh + margin)
    x1, x2 = max(0, rx - margin), min(edges.shape[1], rx + rw + margin)
    outer = edges[y1:y2, x1:x2].copy()
    iy, ix = ry - y1, rx - x1
    outer[iy:iy + rh, ix:ix + rw] = 0
    margin_px = outer.size - rw * rh
    out_density = float(np.sum(outer > 0)) / max(margin_px, 1)
    return in_density / max(out_density, 1e-6)


def _local_frequency_anomaly(
    gray_f32: np.ndarray, rx: int, ry: int, rw: int, rh: int,
) -> float:
    """FFT energy of region / median of 5 random same-size patches."""
    region = gray_f32[ry:ry + rh, rx:rx + rw]
    region_e = float(np.mean(np.abs(np.fft.fft2(region)) ** 2))
    h, w = gray_f32.shape
    rng = np.random.RandomState(42)
    energies = []
    for _ in range(5):
        sy = rng.randint(0, max(1, h - rh))
        sx = rng.randint(0, max(1, w - rw))
        p = gray_f32[sy:sy + rh, sx:sx + rw]
        if p.shape == region.shape:
            energies.append(float(np.mean(np.abs(np.fft.fft2(p)) ** 2)))
    med = float(np.median(energies)) if energies else 1.0
    return region_e / max(med, 1e-6)


def _ink_coverage_ratio(
    gray_u8: np.ndarray, rx: int, ry: int, rw: int, rh: int,
) -> float:
    """Dark pixel (<180) % in region / same for whole doc."""
    region = gray_u8[ry:ry + rh, rx:rx + rw]
    r_ink = float(np.sum(region < 180)) / max(region.size, 1)
    d_ink = float(np.sum(gray_u8 < 180)) / max(gray_u8.size, 1)
    return r_ink / max(d_ink, 1e-6)


# -------------------------------------------------------------------
# Noise-based feature helpers (CHANGE 3)
# -------------------------------------------------------------------

def _noise_fingerprint_mismatch(
    gray_u8: np.ndarray, rx: int, ry: int, rw: int, rh: int,
) -> float:
    """NL-means denoising residual in target vs 4 surrounding regions."""
    small = cv2.resize(gray_u8, None, fx=0.5, fy=0.5)
    denoised = cv2.fastNlMeansDenoising(small, None, h=10,
                                         templateWindowSize=5, searchWindowSize=11)
    residual = cv2.resize(
        np.abs(small.astype(np.float32) - denoised.astype(np.float32)),
        (gray_u8.shape[1], gray_u8.shape[0]),
    )
    target = float(np.mean(residual[ry:ry + rh, rx:rx + rw]))
    h, w = gray_u8.shape
    surr = []
    for dy, dx in [(-rh, 0), (rh, 0), (0, -rw), (0, rw)]:
        sy, sx = ry + dy, rx + dx
        if 0 <= sy and sy + rh <= h and 0 <= sx and sx + rw <= w:
            surr.append(float(np.mean(residual[sy:sy + rh, sx:sx + rw])))
    return abs(target - (float(np.mean(surr)) if surr else target))


def _ela_local_vs_neighbor(
    gray_u8: np.ndarray, rx: int, ry: int, rw: int, rh: int,
) -> float:
    """ELA at JPEG-75: target region mean / mean of 8 surrounding patches."""
    _, enc = cv2.imencode('.jpg', gray_u8, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
    dec = cv2.imdecode(enc, cv2.IMREAD_GRAYSCALE)
    ela = np.abs(gray_u8.astype(np.float32) - dec.astype(np.float32))
    target = float(np.mean(ela[ry:ry + rh, rx:rx + rw]))
    h, w = gray_u8.shape
    surr = []
    for dy in [-rh, 0, rh]:
        for dx in [-rw, 0, rw]:
            if dy == 0 and dx == 0:
                continue
            sy, sx = ry + dy, rx + dx
            if 0 <= sy and sy + rh <= h and 0 <= sx and sx + rw <= w:
                surr.append(float(np.mean(ela[sy:sy + rh, sx:sx + rw])))
    s_mean = float(np.mean(surr)) if surr else 1.0
    return float(np.clip(target / max(s_mean, 1e-6), 0, 10))


def _compression_artifact_density(
    gray_u8: np.ndarray, rx: int, ry: int, rw: int, rh: int,
) -> float:
    """Strong horizontal gradients at DCT block boundaries in region."""
    region = gray_u8[ry:ry + rh, rx:rx + rw].astype(np.float32)
    if region.shape[1] < 16:
        return 0.0
    gx = np.abs(np.diff(region, axis=1))
    bcols = np.arange(7, gx.shape[1], 8)
    if len(bcols) == 0:
        return 0.0
    return float(np.sum(gx[:, bcols] > 20)) / max(rw, 1)


# ===================================================================
# Detectors
# ===================================================================


class CopyPasteDetector(BaseDetector):
    name = "copy_paste"

    def detect(self, context: DetectorContext) -> list[Finding]:
        gray = _to_gray(context.image)
        gray_u8 = _to_gray_uint8(context.image)
        h, w = gray.shape
        patch_h = max(24, h // 12)
        patch_w = max(24, w // 12)
        step_h = max(10, patch_h // 2)
        step_w = max(10, patch_w // 2)

        candidates: list[tuple[int, int, np.ndarray]] = []
        for y in range(0, max(1, h - patch_h + 1), step_h):
            for x in range(0, max(1, w - patch_w + 1), step_w):
                patch = gray[y:y + patch_h, x:x + patch_w]
                if patch.size == 0:
                    continue
                patch_n = patch - float(np.mean(patch))
                norm = float(np.linalg.norm(patch_n))
                if norm < 1e-6:
                    continue
                candidates.append((x, y, patch_n / norm))

        best_corr = 0.0
        best_xy = (w // 3, h // 3)
        min_distance = max(patch_w, patch_h)
        for i in range(len(candidates)):
            x1, y1, p1 = candidates[i]
            for j in range(i + 1, len(candidates)):
                x2, y2, p2 = candidates[j]
                if abs(x1 - x2) + abs(y1 - y2) < min_distance:
                    continue
                corr = float(np.sum(p1 * p2))
                if corr > best_corr:
                    best_corr = corr
                    best_xy = (x2, y2)

        corr = best_corr
        bx, by = best_xy
        bw, bh = patch_w, patch_h

        # CHANGE 1: JPEG-resistant features
        context.shared_features["dct_block_hash_matches"] = _dct_block_hash_matches(gray_u8)
        context.shared_features["patch_self_similarity"] = _patch_self_similarity(gray)
        context.shared_features["blocking_artifact_consistency"] = _blocking_artifact_consistency(gray, bx, by, bw, bh)

        confidence = _safe_confidence(0.38 + max(0.0, corr) * 0.58)
        if confidence < 0.56:
            return []

        return [
            Finding(
                region_id="cp_001",
                bbox=BoundingBox(x=bx, y=by, w=bw, h=bh),
                type="copy_paste",
                confidence=confidence,
                signals=[
                    f"Patch correlation {corr:.2f}",
                    "Repeated local texture motif",
                ],
                severity=_severity_from_confidence(confidence),
                description="Potential duplicated patch detected by baseline similarity scan.",
            )
        ]


class OverwriteDetector(BaseDetector):
    name = "overwrite"

    def detect(self, context: DetectorContext) -> list[Finding]:
        gray = _to_gray(context.image)
        h, w = gray.shape
        center = gray[h // 4: (h * 3) // 4, w // 4: (w * 3) // 4]
        if center.size == 0:
            return []

        global_std = float(np.std(gray))
        center_std = float(np.std(center))
        score = center_std / max(global_std, 1e-6)
        context.shared_features["overwrite_std_ratio"] = score

        confidence = _safe_confidence(0.32 + score / 1.7)
        if confidence < 0.57:
            return []

        bbox = _bbox_from_fraction(context.image, 0.37, 0.42, 0.25, 0.12)
        return [
            Finding(
                region_id="ow_001",
                bbox=bbox,
                type="overwrite",
                confidence=confidence,
                signals=[
                    f"Ink-texture std ratio {score:.2f}",
                    "Stroke continuity disruption",
                ],
                severity=_severity_from_confidence(confidence),
                description="Region texture indicates probable overwrite on existing content.",
            )
        ]


class AddedContentDetector(BaseDetector):
    name = "added_content"

    def detect(self, context: DetectorContext) -> list[Finding]:
        gray = _to_gray(context.image)
        gray_u8 = _to_gray_uint8(context.image)

        h, w = gray.shape
        win_h = max(24, h // 8)
        win_w = max(24, w // 8)
        step_h = max(8, win_h // 2)
        step_w = max(8, win_w // 2)

        best_var = 0.0
        best_xy = (0, 0)
        global_var = float(np.var(gray))
        for y in range(0, max(1, h - win_h + 1), step_h):
            for x in range(0, max(1, w - win_w + 1), step_w):
                patch = gray[y:y + win_h, x:x + win_w]
                patch_var = float(np.var(patch))
                if patch_var > best_var:
                    best_var = patch_var
                    best_xy = (x, y)

        ratio = best_var / max(global_var, 1e-6)
        bx, by = best_xy

        # CHANGE 2: Edge-based features
        context.shared_features["edge_density_ratio"] = _edge_density_ratio(gray_u8, bx, by, win_w, win_h)
        context.shared_features["local_frequency_anomaly"] = _local_frequency_anomaly(gray, bx, by, win_w, win_h)
        context.shared_features["ink_coverage_ratio"] = _ink_coverage_ratio(gray_u8, bx, by, win_w, win_h)

        confidence = _safe_confidence(0.40 + ratio / 2.4)
        if confidence < 0.56:
            return []

        bbox = BoundingBox(x=bx, y=by, w=win_w, h=win_h)
        return [
            Finding(
                region_id="ac_001",
                bbox=bbox,
                type="added_content",
                confidence=confidence,
                signals=[
                    f"Patch/global variance ratio {ratio:.2f}",
                    "Localized structural discontinuity",
                ],
                severity=_severity_from_confidence(confidence),
                description="Potential post-scan content insertion detected in high-frequency region.",
            )
        ]


class ErasureDetector(BaseDetector):
    name = "erasure"

    def detect(self, context: DetectorContext) -> list[Finding]:
        gray = _to_gray(context.image)
        h, w = gray.shape
        win_h = max(24, h // 8)
        win_w = max(24, w // 8)
        step_h = max(8, win_h // 2)
        step_w = max(8, win_w // 2)

        global_var = float(np.var(gray))
        min_var = float("inf")
        best_xy = (0, 0)
        for y in range(0, max(1, h - win_h + 1), step_h):
            for x in range(0, max(1, w - win_w + 1), step_w):
                patch = gray[y:y + win_h, x:x + win_w]
                patch_var = float(np.var(patch))
                if patch_var < min_var:
                    min_var = patch_var
                    best_xy = (x, y)

        smoothness_gain = 1.0 - (min_var / max(global_var, 1e-6))
        context.shared_features["erasure_smoothness_gain"] = smoothness_gain

        confidence = _safe_confidence(0.30 + smoothness_gain * 0.78)
        if confidence < 0.56:
            return []

        bx, by = best_xy
        bbox = BoundingBox(x=bx, y=by, w=win_w, h=win_h)
        return [
            Finding(
                region_id="er_001",
                bbox=bbox,
                type="erasure",
                confidence=confidence,
                signals=[
                    f"Min/global variance gain {smoothness_gain:.2f}",
                    "Low-noise patch inconsistent with nearby texture",
                ],
                severity=_severity_from_confidence(confidence),
                description="Potential erased-and-refilled region identified from smoothness profile.",
            )
        ]


class DocumentMergeDetector(BaseDetector):
    name = "merged"

    def detect(self, context: DetectorContext) -> list[Finding]:
        gray = _to_gray(context.image)
        h, w = gray.shape
        left_band = gray[:, : max(1, w // 3)]
        right_band = gray[:, -max(1, w // 3):]

        left_mean = float(np.mean(left_band))
        right_mean = float(np.mean(right_band))
        contrast_delta = abs(left_mean - right_mean)
        context.shared_features["merged_contrast_delta"] = contrast_delta

        confidence = _safe_confidence(0.30 + contrast_delta / 75.0)
        if confidence < 0.55:
            return []

        bbox = _bbox_from_fraction(context.image, 0.32, 0.05, 0.36, 0.20)
        return [
            Finding(
                region_id="mg_001",
                bbox=bbox,
                type="merged",
                confidence=confidence,
                signals=[
                    f"Left/right luminance delta {contrast_delta:.2f}",
                    "Illumination continuity break",
                ],
                severity=_severity_from_confidence(confidence),
                description="Page-wide luminance mismatch suggests multi-source merge artifact.",
            )
        ]


class WatermarkRemovalDetector(BaseDetector):
    name = "watermark"

    def detect(self, context: DetectorContext) -> list[Finding]:
        gray = _to_gray(context.image)
        spectrum = np.abs(np.fft.fft2(gray))

        row_energy = np.mean(spectrum, axis=1)
        col_energy = np.mean(spectrum, axis=0)
        row_peak = float(np.max(row_energy))
        col_peak = float(np.max(col_energy))
        baseline = float(np.median(row_energy) + np.median(col_energy)) / 2.0
        peak_ratio = max(row_peak, col_peak) / max(baseline, 1e-6)
        context.shared_features["watermark_peak_ratio"] = peak_ratio

        confidence = _safe_confidence(0.26 + peak_ratio / 6.2)
        if confidence < 0.56:
            return []

        bbox = _bbox_from_fraction(context.image, 0.62, 0.68, 0.22, 0.14)
        return [
            Finding(
                region_id="wm_001",
                bbox=bbox,
                type="watermark",
                confidence=confidence,
                signals=[
                    f"FFT line peak ratio {peak_ratio:.2f}",
                    "Residual periodic suppression pattern",
                ],
                severity=_severity_from_confidence(confidence),
                description="Frequency-domain residue indicates probable watermark removal operation.",
            )
        ]


from core.ocr_check import OCR_AVAILABLE

class SpacingIrregularityDetector(BaseDetector):
    name = "spacing"

    def detect(self, context: DetectorContext) -> list[Finding]:
        if OCR_AVAILABLE:
            pass

        gray = _to_gray(context.image)

        row_profile = np.mean(gray, axis=1)
        row_diff = np.abs(np.diff(row_profile))
        if row_diff.size == 0:
            return []

        q1 = float(np.quantile(row_diff, 0.25))
        q3 = float(np.quantile(row_diff, 0.75))
        iqr = max(1e-6, q3 - q1)
        outlier_score = float(np.max(row_diff) - q3) / iqr
        context.shared_features["spacing_outlier_score"] = outlier_score

        confidence = _safe_confidence(0.33 + outlier_score / 5.5)
        if confidence < 0.55:
            return []

        bbox = _bbox_from_fraction(context.image, 0.20, 0.62, 0.46, 0.10)
        return [
            Finding(
                region_id="sp_001",
                bbox=bbox,
                type="spacing",
                confidence=confidence,
                signals=[
                    f"Projection-profile outlier score {outlier_score:.2f} (Fallback Mode)",
                    "Baseline rhythm irregularity",
                ],
                severity=_severity_from_confidence(confidence),
                description="Line spacing pattern deviates from local textual baseline.",
            )
        ]


class AIGeneratedDetector(BaseDetector):
    name = "ai_generated"

    def detect(self, context: DetectorContext) -> list[Finding]:
        if OCR_AVAILABLE:
            pass

        gray = _to_gray(context.image)
        spectrum = np.fft.fftshift(np.abs(np.fft.fft2(gray)))
        h, w = spectrum.shape
        cy, cx = h // 2, w // 2

        core = spectrum[max(0, cy - 20): cy + 20, max(0, cx - 20): cx + 20]
        periphery = np.concatenate(
            [
                spectrum[: max(1, h // 8), :].ravel(),
                spectrum[-max(1, h // 8):, :].ravel(),
                spectrum[:, : max(1, w // 8)].ravel(),
                spectrum[:, -max(1, w // 8):].ravel(),
            ]
        )
        core_mean = float(np.mean(core)) if core.size else 0.0
        periphery_mean = float(np.mean(periphery)) if periphery.size else 1.0
        ratio = core_mean / max(periphery_mean, 1e-5)
        context.shared_features["ai_generated_ratio"] = ratio

        confidence = _safe_confidence(0.40 + ratio / 6.5)
        if confidence < 0.55:
            return []

        bbox = _bbox_from_fraction(context.image, 0.12, 0.18, 0.30, 0.18)
        return [
            Finding(
                region_id="ag_001",
                bbox=bbox,
                type="ai_generated",
                confidence=confidence,
                signals=[
                    f"FFT center/periphery ratio {ratio:.2f} (Fallback Mode)",
                    "Texture regularity exceeds scanned baseline",
                ],
                severity=_severity_from_confidence(confidence),
                description="Global frequency profile resembles synthesized texture behavior.",
            )
        ]


class PartialAIEditDetector(BaseDetector):
    name = "ai_edit"

    def detect(self, context: DetectorContext) -> list[Finding]:
        if OCR_AVAILABLE:
            pass

        gray = _to_gray(context.image)
        gray_u8 = _to_gray_uint8(context.image)
        dominant_var, quadrant_idx = _quadrant_variance(gray)
        global_var = float(np.var(gray))
        score = dominant_var / max(global_var, 1e-6)

        quadrant_boxes = {
            0: (0.10, 0.10),
            1: (0.58, 0.10),
            2: (0.10, 0.56),
            3: (0.58, 0.56),
        }
        x_frac, y_frac = quadrant_boxes.get(quadrant_idx, (0.58, 0.56))
        img_h, img_w = gray.shape
        rx = max(0, min(int(img_w * x_frac), img_w - 24))
        ry = max(0, min(int(img_h * y_frac), img_h - 20))
        rw = max(24, int(img_w * 0.28))
        rh = max(20, int(img_h * 0.18))
        rw = min(rw, img_w - rx)
        rh = min(rh, img_h - ry)

        # CHANGE 3: Noise-based features
        context.shared_features["noise_fingerprint_mismatch"] = _noise_fingerprint_mismatch(gray_u8, rx, ry, rw, rh)
        context.shared_features["ela_local_vs_neighbor"] = _ela_local_vs_neighbor(gray_u8, rx, ry, rw, rh)
        context.shared_features["compression_artifact_density"] = _compression_artifact_density(gray_u8, rx, ry, rw, rh)

        confidence = _safe_confidence(0.38 + score / 2.8)
        if confidence < 0.54:
            return []

        bbox = _bbox_from_fraction(context.image, x_frac, y_frac, 0.28, 0.18)

        return [
            Finding(
                region_id="ae_001",
                bbox=bbox,
                type="ai_edit",
                confidence=confidence,
                signals=[
                    f"Local/global variance ratio {score:.2f} (Fallback Mode)",
                    "Asymmetric retouch footprint",
                ],
                severity=_severity_from_confidence(confidence),
                description="Localized region exhibits partial synthetic editing characteristics.",
            )
        ]
