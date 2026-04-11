import json
import random
from pathlib import Path
from typing import TypedDict

class SplitCounts(TypedDict):
    train: int
    val: int
    test: int

def split_dataset(data_dir: Path, split_ratio: tuple[float, float, float] = (0.7, 0.15, 0.15)):
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"Error: Manifest not found at {manifest_path}")
        return

    manifest = json.loads(manifest_path.read_text())
    
    # Group by class to ensure stratified splitting
    by_class: dict[str, list[dict]] = {}
    for item in manifest:
        by_class.setdefault(item["type"], []).append(item)
        
    train_split, val_split, test_split = [], [], []
    
    for cls, items in by_class.items():
        random.shuffle(items)
        n = len(items)
        train_end = int(n * split_ratio[0])
        val_end = train_end + int(n * split_ratio[1])
        
        train_split.extend(items[:train_end])
        val_split.extend(items[train_end:val_end])
        test_split.extend(items[val_end:])
        
    # Save splits
    split_dir = data_dir / "splits"
    split_dir.mkdir(exist_ok=True)
    
    (split_dir / "train.json").write_text(json.dumps(train_split, indent=2))
    (split_dir / "val.json").write_text(json.dumps(val_split, indent=2))
    (split_dir / "test.json").write_text(json.dumps(test_split, indent=2))
    
    print(f"Split created in {split_dir}")
    print(f"Train: {len(train_split)}, Val: {len(val_split)}, Test: {len(test_split)}")
    
    # Write Benchmark Contract Summary
    contract = {
        "schema_version": "1.0",
        "features_expected": [
            "copy_paste_max_corr",
            "overwrite_std_ratio",
            "added_content_var_ratio",
            "erasure_smoothness_gain",
            "merged_contrast_delta",
            "watermark_peak_ratio",
            "spacing_outlier_score",
            "ai_generated_ratio",
            "ai_edit_local_var_ratio"
        ],
        "splits": {
            "train": len(train_split),
            "val": len(val_split),
            "test": len(test_split)
        },
        "scoring_protocol": {
            "primary_metric": "f1_score",
            "secondary_metrics": ["precision", "recall", "auc_roc"],
            "threshold": 0.5
        }
    }
    
    (split_dir / "benchmark_contract.json").write_text(json.dumps(contract, indent=2))
    print("Benchmark contract generated.")

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parents[1] / "data" / "synthetic"
    split_dataset(out_dir)
