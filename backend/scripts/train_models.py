"""
Train per-class binary classifiers for the 9 tamper types.

CHANGE 5: watermark and ai_generated use StandardScaler + SVC(rbf).
All other classes use RandomForestClassifier(n_estimators=200, max_depth=12).
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

FEATURE_COLUMNS = [
    "dct_block_hash_matches",
    "patch_self_similarity",
    "blocking_artifact_consistency",
    "overwrite_std_ratio",
    "edge_density_ratio",
    "local_frequency_anomaly",
    "ink_coverage_ratio",
    "erasure_smoothness_gain",
    "merged_contrast_delta",
    "watermark_peak_ratio",
    "spacing_outlier_score",
    "ai_generated_ratio",
    "noise_fingerprint_mismatch",
    "ela_local_vs_neighbor",
    "compression_artifact_density",
    "watermark_peak_ratio_raw",
    "ai_generated_ratio_raw",
]

SVC_CLASSES = {"watermark", "ai_generated"}

TRANCHES = {
    "4A": ["added_content", "ai_generated", "ai_edit"],
    "4B": ["copy_paste", "overwrite", "spacing"],
    "4C": ["erasure", "merged", "watermark"],
}


def _load_csv(path: Path) -> tuple[np.ndarray, list[str]]:
    X_rows: list[list[float]] = []
    labels: list[str] = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            features = [float(row[col]) for col in FEATURE_COLUMNS]
            X_rows.append(features)
            labels.append(row["label"])
    return np.array(X_rows), labels


def _make_binary_labels(labels: list[str], positive_class: str) -> np.ndarray:
    return np.array([1 if lbl == positive_class else 0 for lbl in labels])


def _build_model(cls: str):
    """Build the appropriate model for a given class."""
    if cls in SVC_CLASSES:
        return Pipeline([
            ("scaler", StandardScaler()),
            ("svc", SVC(kernel="rbf", C=10, gamma="scale",
                        class_weight="balanced", probability=True, random_state=42)),
        ])
    return RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )


def train_model_for_class(
    cls: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
) -> tuple:
    model = _build_model(cls)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_val)
    metrics = {
        "class": cls,
        "model_type": "SVC" if cls in SVC_CLASSES else "RF",
        "f1": round(f1_score(y_val, y_pred, zero_division=0.0), 4),
        "precision": round(precision_score(y_val, y_pred, zero_division=0.0), 4),
        "recall": round(recall_score(y_val, y_pred, zero_division=0.0), 4),
        "val_positives": int(y_val.sum()),
        "val_total": len(y_val),
        "train_positives": int(y_train.sum()),
        "train_total": len(y_train),
    }
    return model, metrics


def train_tranche(
    tranche_name: str,
    classes: list[str],
    X_train: np.ndarray,
    labels_train: list[str],
    X_val: np.ndarray,
    labels_val: list[str],
    model_dir: Path,
) -> list[dict]:
    print(f"\n{'='*60}")
    print(f"  TRANCHE {tranche_name}: {classes}")
    print(f"{'='*60}")

    all_metrics = []
    for cls in classes:
        y_train = _make_binary_labels(labels_train, cls)
        y_val = _make_binary_labels(labels_val, cls)

        model, metrics = train_model_for_class(cls, X_train, y_train, X_val, y_val)

        model_path = model_dir / f"{cls}.joblib"
        joblib.dump(model, model_path)

        print(f"  [{cls}] ({metrics['model_type']}) F1={metrics['f1']:.4f}  "
              f"P={metrics['precision']:.4f}  R={metrics['recall']:.4f}  "
              f"(train={metrics['train_positives']}/{metrics['train_total']}, "
              f"val={metrics['val_positives']}/{metrics['val_total']})  "
              f"-> {model_path.name}")
        all_metrics.append(metrics)

    return all_metrics


def evaluate_on_test(
    model_dir: Path,
    X_test: np.ndarray,
    labels_test: list[str],
) -> list[dict]:
    print(f"\n{'='*60}")
    print(f"  TEST SET EVALUATION")
    print(f"{'='*60}")

    test_metrics = []
    for model_path in sorted(model_dir.glob("*.joblib")):
        cls = model_path.stem
        model = joblib.load(model_path)
        y_test = _make_binary_labels(labels_test, cls)
        y_pred = model.predict(X_test)

        metrics = {
            "class": cls,
            "f1": round(f1_score(y_test, y_pred, zero_division=0.0), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0.0), 4),
            "recall": round(recall_score(y_test, y_pred, zero_division=0.0), 4),
            "test_positives": int(y_test.sum()),
            "test_total": len(y_test),
        }
        print(f"  [{cls}] F1={metrics['f1']:.4f}  P={metrics['precision']:.4f}  "
              f"R={metrics['recall']:.4f}  "
              f"(positives={metrics['test_positives']}/{metrics['test_total']})")
        test_metrics.append(metrics)

    return test_metrics


def main() -> int:
    features_dir = BACKEND_ROOT / "data" / "features"
    model_dir = BACKEND_ROOT / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    X_train, labels_train = _load_csv(features_dir / "train.csv")
    X_val, labels_val = _load_csv(features_dir / "val.csv")
    X_test, labels_test = _load_csv(features_dir / "test.csv")

    print(f"Data loaded: train={len(labels_train)}, val={len(labels_val)}, test={len(labels_test)}")
    print(f"Feature dimensions: {X_train.shape[1]} columns")

    all_metrics: list[dict] = []

    for tranche_name, classes in TRANCHES.items():
        metrics = train_tranche(
            tranche_name, classes,
            X_train, labels_train,
            X_val, labels_val,
            model_dir,
        )
        all_metrics.extend(metrics)

    test_metrics = evaluate_on_test(model_dir, X_test, labels_test)

    report = {
        "validation_metrics": all_metrics,
        "test_metrics": test_metrics,
        "model_dir": str(model_dir),
        "feature_columns": FEATURE_COLUMNS,
        "tranches": {k: v for k, v in TRANCHES.items()},
    }
    report_path = model_dir / "training_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"\nFull report saved to {report_path}")

    avg_f1 = sum(m["f1"] for m in test_metrics) / max(len(test_metrics), 1)
    print(f"\n{'='*60}")
    print(f"  OVERALL TEST F1 (macro avg): {avg_f1:.4f}")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
