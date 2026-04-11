"""
Extract feature vectors from synthetic images using the heuristic detectors.
Produces CSV files with one row per image, columns = feature names + label.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from joblib import Parallel, delayed

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from detection.base import DetectorContext
from detection.registry import create_detector, detector_names


FEATURE_COLUMNS = [
    # CHANGE 1: JPEG-resistant (replaces copy_paste_max_corr)
    "dct_block_hash_matches",
    "patch_self_similarity",
    "blocking_artifact_consistency",
    # Kept
    "overwrite_std_ratio",
    # CHANGE 2: Edge-based (replaces added_content_var_ratio)
    "edge_density_ratio",
    "local_frequency_anomaly",
    "ink_coverage_ratio",
    # Kept
    "erasure_smoothness_gain",
    "merged_contrast_delta",
    "watermark_peak_ratio",
    "spacing_outlier_score",
    "ai_generated_ratio",
    # CHANGE 3: Noise-based (replaces ai_edit_local_var_ratio)
    "noise_fingerprint_mismatch",
    "ela_local_vs_neighbor",
    "compression_artifact_density",
    # CHANGE 4: Raw pre-JPEG features
    "watermark_peak_ratio_raw",
    "ai_generated_ratio_raw",
]


def extract_features_for_image(image: np.ndarray, domain: str = "medical") -> dict[str, float]:
    """Run all detectors on an image and return the shared_features dict."""
    context = DetectorContext(image=image, domain=domain)
    for name in detector_names():
        detector = create_detector(name)
        try:
            detector.detect(context)
        except Exception:
            pass
    features = {}
    for col in FEATURE_COLUMNS:
        features[col] = context.shared_features.get(col, 0.0)
    return features


def _process_single_item(item: dict) -> tuple[dict[str, float] | None, str | None]:
    try:
        img_path = item["image_path"]
        label = item.get("class") or item.get("type", "authentic")
        img = np.array(Image.open(img_path).convert("L"), dtype=np.uint8)
        features = extract_features_for_image(img)

        # CHANGE 4: Pre-JPEG raw features for ai_generated and watermark
        if label in ("ai_generated", "watermark"):
            pre_jpeg_path = img_path.replace(".png", "_pre_jpeg.png")
            pre_jpeg_file = Path(pre_jpeg_path)
            if pre_jpeg_file.exists():
                raw_img = np.array(Image.open(pre_jpeg_file).convert("L"), dtype=np.uint8)
                raw_ctx = DetectorContext(image=raw_img, domain="medical")
                # Run only the relevant detectors on the clean version
                for det_name in ["watermark", "ai_generated"]:
                    det = create_detector(det_name)
                    try:
                        det.detect(raw_ctx)
                    except Exception:
                        pass
                features["watermark_peak_ratio_raw"] = raw_ctx.shared_features.get("watermark_peak_ratio", 0.0)
                features["ai_generated_ratio_raw"] = raw_ctx.shared_features.get("ai_generated_ratio", 0.0)

        return features, label
    except Exception as e:
        print(f"Error processing {item.get('id')}: {e}")
        return None, None


def extract_dataset(split_path: Path) -> tuple[list[dict[str, float]], list[str]]:
    """Extract features for all images in a split file using multiprocessing."""
    items = json.loads(split_path.read_text())

    print(f"Extracting {len(items)} items using 6 workers...")
    results = Parallel(n_jobs=6, verbose=1)(
        delayed(_process_single_item)(item) for item in items
    )

    all_features = []
    all_labels = []
    for feats, lbl in results:
        if feats is not None and lbl is not None:
            all_features.append(feats)
            all_labels.append(lbl)

    return all_features, all_labels


def features_to_csv(features: list[dict[str, float]], labels: list[str], output_path: Path) -> None:
    """Write features + labels to CSV."""
    header = ",".join(FEATURE_COLUMNS + ["label"])
    rows = []
    for feat, label in zip(features, labels):
        row_vals = [str(feat.get(col, 0.0)) for col in FEATURE_COLUMNS]
        row_vals.append(label)
        rows.append(",".join(row_vals))

    output_path.write_text(header + "\n" + "\n".join(rows) + "\n")
    print(f"Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    data_dir = BACKEND_ROOT / "data" / "synthetic" / "splits"
    output_dir = BACKEND_ROOT / "data" / "features"
    output_dir.mkdir(parents=True, exist_ok=True)

    for split_name in ["train", "val", "test"]:
        split_file = data_dir / f"{split_name}.json"
        if not split_file.exists():
            print(f"Skipping {split_name}: {split_file} not found")
            continue

        features, labels = extract_dataset(split_file)
        features_to_csv(features, labels, output_dir / f"{split_name}.csv")
