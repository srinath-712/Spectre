import json
from pathlib import Path

import numpy as np
from PIL import Image

def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def _base_image(width=800, height=1000) -> np.ndarray:
    """Create a simulated noisy scan background."""
    img = np.full((height, width), 240, dtype=np.float32)
    img += np.random.normal(0, 5, (height, width))
    # Add simulated text lines
    for y in range(100, height - 100, 30):
        img[y:y+10, 100:width-100] -= np.random.normal(100, 20, (10, width-200))
    return np.clip(img, 0, 255).astype(np.uint8)

def gen_copy_paste() -> tuple[np.ndarray, dict]:
    img = _base_image()
    # Copy from top-left to middle
    patch = img[150:250, 150:350].copy()
    img[400:500, 400:600] = patch
    return img, {"type": "copy_paste", "bbox": [400, 400, 200, 100]}

def gen_overwrite() -> tuple[np.ndarray, dict]:
    img = _base_image()
    # High variance dark patch
    img[400:460, 300:500] = np.clip(np.random.normal(50, 40, (60, 200)), 0, 255)
    return img, {"type": "overwrite", "bbox": [300, 400, 200, 60]}

def gen_added_content() -> tuple[np.ndarray, dict]:
    img = _base_image()
    # Inject high frequency noise
    img[600:700, 200:400] = np.clip(img[600:700, 200:400] - np.random.normal(80, 50, (100, 200)), 0, 255)
    return img, {"type": "added_content", "bbox": [200, 600, 200, 100]}

def gen_erasure() -> tuple[np.ndarray, dict]:
    img = _base_image()
    # Purely smooth background patch
    img[500:580, 300:500] = 240
    return img, {"type": "erasure", "bbox": [300, 500, 200, 80]}

def gen_merged() -> tuple[np.ndarray, dict]:
    img = _base_image()
    # Luminance mismatch
    img[:, :400] = np.clip(img[:, :400].astype(np.float32) - 30, 0, 255)
    img[:, 400:] = np.clip(img[:, 400:].astype(np.float32) + 20, 0, 255)
    return img, {"type": "merged", "bbox": [380, 0, 40, 1000]}

def gen_watermark() -> tuple[np.ndarray, dict]:
    img = _base_image()
    # Inject narrow lines that will persist in FFT
    for i in range(0, 1000, 50):
        img[i:i+2, :] = 250
    return img, {"type": "watermark", "bbox": [0, 0, 800, 1000]}

def gen_spacing() -> tuple[np.ndarray, dict]:
    img = _base_image()
    # Create irregular horizontal spacing
    img[350:370, 100:700] -= np.random.normal(120, 10, (20, 600)).astype(np.uint8)
    return img, {"type": "spacing", "bbox": [100, 350, 600, 20]}

def gen_ai_generated() -> tuple[np.ndarray, dict]:
    img = _base_image()
    # Inject high variance strictly in center to mimic AI core/periphery FFT
    h, w = img.shape
    cy, cx = h // 2, w // 2
    img[cy-50:cy+50, cx-50:cx+50] += np.random.normal(0, 80, (100, 100)).astype(np.uint8)
    return img, {"type": "ai_generated", "bbox": [cx-50, cy-50, 100, 100]}

def gen_ai_edit() -> tuple[np.ndarray, dict]:
    img = _base_image()
    # Quadrant 2 (bottom-left) variance anomaly
    img[700:850, 100:300] = np.clip(np.random.normal(150, 80, (150, 200)), 0, 255)
    return img, {"type": "ai_edit", "bbox": [100, 700, 200, 150]}

def generate_dataset(output_dir: Path, samples_per_class: int = 5):
    _ensure_dir(output_dir / "images")
    _ensure_dir(output_dir / "labels")
    
    generators = [
        gen_copy_paste, gen_overwrite, gen_added_content,
        gen_erasure, gen_merged, gen_watermark,
        gen_spacing, gen_ai_generated, gen_ai_edit
    ]
    
    manifest = []
    
    for i in range(samples_per_class):
        for gen in generators:
            img, label = gen()
            uid = f"{label['type']}_{i:03d}"
            
            img_path = output_dir / "images" / f"{uid}.png"
            Image.fromarray(img).save(img_path)
            
            label_path = output_dir / "labels" / f"{uid}.json"
            label_path.write_text(json.dumps(label))
            
            manifest.append({
                "id": uid,
                "type": label["type"],
                "image_path": str(img_path.absolute()),
                "label_path": str(label_path.absolute())
            })
            
    # Auth items
    for i in range(samples_per_class):
        img = _base_image()
        uid = f"authentic_{i:03d}"
        img_path = output_dir / "images" / f"{uid}.png"
        Image.fromarray(img).save(img_path)
        manifest.append({
            "id": uid,
            "type": "authentic",
            "image_path": str(img_path.absolute()),
            "label_path": None
        })

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Generated {len(manifest)} synthetic samples at {output_dir}")

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parents[1] / "data" / "synthetic"
    generate_dataset(out_dir, samples_per_class=10)
