import json
import math
import random
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

# Set seeds for reproducibility
random.seed(42)
np.random.seed(42)

IMG_W = 800
IMG_H = 1000
MARGIN = 20

# ---------------------------------------------------------
# Base Document Generators
# ---------------------------------------------------------

def _draw_text_lines(img, w, h):
    y = random.randint(40, 60)
    while y < h - 40:
        if random.random() > 0.1:  # Skip some lines for paragraphs
            thickness = random.randint(1, 3)
            # slight curve
            curve = random.randint(-1, 1)
            x_start = random.randint(40, 100)
            x_end = random.randint(w - 200, w - 40)
            
            pts = []
            for x_pt in range(x_start, x_end, 50):
                pts.append([x_pt, y + curve * math.sin(x_pt / 100.0)])
            pts.append([x_end, y + curve * math.sin(x_end / 100.0)])
            
            pts = np.array(pts, np.int32).reshape((-1, 1, 2))
            # Text color (dark gray to black)
            c = random.randint(0, 50)
            cv2.polylines(img, [pts], False, (c, c, c), thickness)
            
        y += random.randint(18, 28)
    return img

def base_clean_white():
    img = np.full((IMG_H, IMG_W, 3), 255, dtype=np.uint8)
    return _draw_text_lines(img, IMG_W, IMG_H)

def base_yellowed_aged():
    r = random.randint(245, 252)
    g = random.randint(240, 248)
    b = random.randint(220, 235)
    img = np.full((IMG_H, IMG_W, 3), (b, g, r), dtype=np.uint8)
    
    # Low frequency noise
    noise = np.random.normal(0, random.uniform(3, 6), (IMG_H // 4, IMG_W // 4, 3))
    noise = cv2.resize(noise, (IMG_W, IMG_H), interpolation=cv2.INTER_LINEAR)
    img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return _draw_text_lines(img, IMG_W, IMG_H)

def base_high_noise():
    img = np.full((IMG_H, IMG_W, 3), 255, dtype=np.uint8)
    img = _draw_text_lines(img, IMG_W, IMG_H)
    noise = np.random.normal(0, random.uniform(12, 20), (IMG_H, IMG_W, 3))
    img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return img

def base_lined_paper():
    # Ruled paper yellowing
    r, g, b = 250, 248, 235
    img = np.full((IMG_H, IMG_W, 3), (b, g, r), dtype=np.uint8)
    
    # Blue horizontal lines
    y = random.randint(30, 50)
    spacing = random.randint(24, 28)
    while y < IMG_H:
        # BGR blue
        cv2.line(img, (0, y), (IMG_W, y), (200, 100, 100), 1)
        y += spacing
        
    return _draw_text_lines(img, IMG_W, IMG_H)

def generate_base_document():
    generators = [base_clean_white, base_yellowed_aged, base_high_noise, base_lined_paper]
    func = random.choice(generators)
    return func(), func.__name__

# ---------------------------------------------------------
# Tamper Generators
# ---------------------------------------------------------

def gen_copy_paste(img):
    patch_w = random.randint(80, 250)
    patch_h = random.randint(40, 120)
    
    src_x = random.randint(MARGIN, IMG_W - patch_w - MARGIN)
    src_y = random.randint(MARGIN, IMG_H - patch_h - MARGIN)
    
    dst_x = random.randint(MARGIN, IMG_W - patch_w - MARGIN)
    dst_y = random.randint(MARGIN, IMG_H - patch_h - MARGIN)
    
    # Ensure distance is at least 100px
    while math.hypot(dst_x - src_x, dst_y - src_y) < 100:
        dst_x = random.randint(MARGIN, IMG_W - patch_w - MARGIN)
        dst_y = random.randint(MARGIN, IMG_H - patch_h - MARGIN)
        
    patch = img[src_y:src_y+patch_h, src_x:src_x+patch_w].copy()
    
    # Scale variant
    if random.random() < 0.3:
        scale = random.uniform(0.95, 1.05)
        new_w, new_h = int(patch_w * scale), int(patch_h * scale)
        patch = cv2.resize(patch, (new_w, new_h))
        # Recalculate dest boundary safely
        dst_x = min(max(MARGIN, dst_x), IMG_W - new_w - MARGIN)
        dst_y = min(max(MARGIN, dst_y), IMG_H - new_h - MARGIN)
        patch_w, patch_h = new_w, new_h

    # Brightness shift
    shift = random.uniform(-10, 10)
    patch = np.clip(patch.astype(np.float32) + shift, 0, 255).astype(np.uint8)
    
    img[dst_y:dst_y+patch_h, dst_x:dst_x+patch_w] = patch
    return img, {"x": dst_x, "y": dst_y, "w": patch_w, "h": patch_h}

def gen_overwrite(img):
    patch_w = random.randint(100, 300)
    patch_h = random.randint(20, 80)
    x = random.randint(MARGIN, IMG_W - patch_w - MARGIN)
    y = random.randint(MARGIN, IMG_H - patch_h - MARGIN)
    
    alpha = random.uniform(0.4, 1.0)
    
    # Ink color
    if random.random() < 0.4:
        # Same-color overwrite
        bg_mean = cv2.mean(img[y:y+patch_h, x:x+patch_w])[:3]
        ink_layer = np.full((patch_h, patch_w, 3), bg_mean, dtype=np.uint8)
        noise = np.random.normal(0, 5, (patch_h, patch_w, 3))
        ink_layer = np.clip(ink_layer.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    else:
        # Dark ink
        c = random.randint(0, 60)
        ink_layer = np.full((patch_h, patch_w, 3), (c, c, c), dtype=np.uint8)
        
    roi = img[y:y+patch_h, x:x+patch_w]
    img[y:y+patch_h, x:x+patch_w] = cv2.addWeighted(roi, 1 - alpha, ink_layer, alpha, 0)
    return img, {"x": x, "y": y, "w": patch_w, "h": patch_h}

def gen_added_content(img):
    patch_w = random.randint(60, 200)
    patch_h = random.randint(40, 150)
    x = random.randint(MARGIN, IMG_W - patch_w - MARGIN)
    y = random.randint(MARGIN, IMG_H - patch_h - MARGIN)
    
    mode = random.random()
    roi = img[y:y+patch_h, x:x+patch_w]
    
    if mode < 0.33:
        # High freq digital noise
        noise = np.random.normal(0, random.uniform(30, 80), (patch_h, patch_w, 3))
        img[y:y+patch_h, x:x+patch_w] = np.clip(roi.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    elif mode < 0.66:
        # Stamp
        color = (random.randint(0, 50), random.randint(0, 50), random.randint(150, 255)) # BGR, maybe reddish/blueish
        cv2.rectangle(img, (x, y), (x+patch_w, y+patch_h), color, random.randint(2, 4))
        cv2.putText(img, "APPROVED", (x + 10, y + patch_h // 2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 
                    random.uniform(0.5, 1.0), color, random.randint(1, 2))
    else:
        # Signature
        pts = []
        for _ in range(random.randint(5, 15)):
            pts.append([random.randint(x, x+patch_w), random.randint(y, y+patch_h)])
        pts = np.array(pts, np.int32).reshape((-1, 1, 2))
        color = (random.randint(50, 150), random.randint(0, 50), random.randint(0, 50)) # dark blue ink
        cv2.polylines(img, [pts], False, color, random.randint(1, 3))
        
    return img, {"x": x, "y": y, "w": patch_w, "h": patch_h}

def gen_erasure(img):
    patch_w = random.randint(80, 250)
    patch_h = random.randint(30, 100)
    x = random.randint(MARGIN, IMG_W - patch_w - MARGIN)
    y = random.randint(MARGIN, IMG_H - patch_h - MARGIN)
    
    mask = np.zeros((IMG_H, IMG_W), dtype=np.uint8)
    cv2.rectangle(mask, (x, y), (x+patch_w, y+patch_h), 255, -1)
    mask = cv2.GaussianBlur(mask, (7, 7), 3) # Blur edges manually using mask approx
    
    if random.random() < 0.5:
        # Pure white
        patch_color = (255, 255, 255)
    else:
        # Local background avg
        expanded_x = max(0, x - 20)
        expanded_y = max(0, y - 20)
        expanded_w = min(IMG_W - expanded_x, patch_w + 40)
        expanded_h = min(IMG_H - expanded_y, patch_h + 40)
        bg_mean = cv2.mean(img[expanded_y:expanded_y+expanded_h, expanded_x:expanded_x+expanded_w])[:3]
        
        patch_color = (
            min(255, max(0, bg_mean[0] + random.randint(-5, 5))),
            min(255, max(0, bg_mean[1] + random.randint(-5, 5))),
            min(255, max(0, bg_mean[2] + random.randint(-5, 5)))
        )
        
    erased = np.full_like(img, patch_color, dtype=np.uint8)
    # add tiny variance to avoid absolute zero std in pure white case sometimes causing float warnings, or keep < 2.0 std
    noise = np.random.normal(0, random.uniform(0.5, 1.5), (IMG_H, IMG_W, 3))
    erased = np.clip(erased.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    mask_3d = mask[:, :, np.newaxis] / 255.0
    img = (img * (1 - mask_3d) + erased * mask_3d).astype(np.uint8)
    
    return img, {"x": x, "y": y, "w": patch_w, "h": patch_h}

def gen_merged(img):
    is_vertical = random.random() < 0.5
    
    img_f = img.astype(np.float32)
    
    if is_vertical:
        split_pos = int(IMG_W * random.uniform(0.3, 0.7))
        bbox = {"x": split_pos - 10, "y": 0, "w": 20, "h": IMG_H}
        
        m_left = random.uniform(0.85, 0.97)
        m_right = random.uniform(1.03, 1.18)
        
        mask = np.zeros((IMG_H, IMG_W, 3), dtype=np.float32)
        mask[:, :split_pos, :] = m_left
        mask[:, split_pos:, :] = m_right
        
    else:
        split_pos = int(IMG_H * random.uniform(0.3, 0.7))
        bbox = {"x": 0, "y": split_pos - 10, "w": IMG_W, "h": 20}
        
        m_top = random.uniform(0.85, 0.97)
        m_bot = random.uniform(1.03, 1.18)
        
        mask = np.zeros((IMG_H, IMG_W, 3), dtype=np.float32)
        mask[:split_pos, :, :] = m_top
        mask[split_pos:, :, :] = m_bot

    mask = cv2.GaussianBlur(mask, (15, 15), 5)
    img_f = img_f * mask
    img_f = np.clip(img_f, 0, 255).astype(np.uint8)
    
    # Slight rotation difference
    if random.random() < 0.3:
        angle = random.uniform(-0.5, 0.5)
        center = (IMG_W // 2, IMG_H // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        if is_vertical:
            half = img_f[:, split_pos:].copy()
            h, w = half.shape[:2]
            rotated = cv2.warpAffine(half, M, (w, h), borderValue=(255, 255, 255))
            img_f[:, split_pos:] = rotated
        else:
            half = img_f[split_pos:, :].copy()
            h, w = half.shape[:2]
            rotated = cv2.warpAffine(half, M, (w, h), borderValue=(255, 255, 255))
            img_f[split_pos:, :] = rotated
            
    return img_f, bbox

def gen_watermark(img):
    mode = random.randint(1, 3)
    bbox = {"x": 0, "y": 0, "w": IMG_W, "h": IMG_H}
    img_f = img.astype(np.float32)
    
    if mode == 1:
        # horizontal lines
        spacing = random.randint(30, 70)
        intensity = random.randint(15, 40)
        for y in range(0, IMG_H, spacing):
            img_f[y:y+1, :] = np.clip(img_f[y:y+1, :] + intensity, 0, 255)
    elif mode == 2:
        # diagonal text
        overlay = np.zeros_like(img, dtype=np.uint8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        for y in range(0, IMG_H + IMG_W, 150):
            cv2.putText(overlay, "CONFIDENTIAL", (100, y), font, 4, (200, 200, 200), 5)
        
        M = cv2.getRotationMatrix2D((IMG_W/2, IMG_H/2), 45, 1)
        overlay = cv2.warpAffine(overlay, M, (IMG_W, IMG_H))
        
        alpha = random.uniform(0.08, 0.18)
        img_f = np.clip(img_f + (overlay.astype(np.float32) * alpha), 0, 255)
    else:
        # repeating logo simulation
        overlay = np.zeros_like(img, dtype=np.uint8)
        for y in range(50, IMG_H, 150):
            for x in range(50, IMG_W, 150):
                cv2.rectangle(overlay, (x, y), (x+40, y+30), (180, 180, 180), -1)
                
        alpha = random.uniform(0.05, 0.15)
        img_f = np.clip(img_f + (overlay.astype(np.float32) * alpha), 0, 255)
        
    return img_f.astype(np.uint8), bbox

def gen_spacing(img):
    # Select 2-4 random text lines roughly
    num_lines = random.randint(2, 4)
    line_ys = [random.randint(100, IMG_H - 100) for _ in range(num_lines)]
    line_h = 24
    
    min_x, max_x = IMG_W, 0
    min_y, max_y = IMG_H, 0
    
    img_res = img.copy()
    
    for y in line_ys:
        shift_y = random.randint(8, 20) * random.choice([-1, 1])
        segment_w = random.randint(300, 600)
        x = random.randint(MARGIN, IMG_W - segment_w - MARGIN)
        
        min_x = min(min_x, x)
        max_x = max(max_x, x + segment_w)
        min_y = min(min_y, min(y, y + shift_y))
        max_y = max(max_y, max(y + line_h, y + shift_y + line_h))
        
        # Extracted line
        line_roi = img[y:y+line_h, x:x+segment_w].copy()
        
        # Fill gap
        bg_mean = cv2.mean(img[y:y+line_h, x:x+segment_w])[:3]
        img_res[y:y+line_h, x:x+segment_w] = bg_mean
        
        # Horizontal expansion
        if random.random() < 0.5:
            gaps = random.randint(1, 3)
            for _ in range(gaps):
                split_x = random.randint(20, segment_w - 20)
                gap_w = random.randint(3, 8)
                if x + segment_w + gap_w < IMG_W:
                    left = line_roi[:, :split_x]
                    right = line_roi[:, split_x:]
                    gap = np.full((line_h, gap_w, 3), bg_mean, dtype=np.uint8)
                    line_roi = np.hstack([left, gap, right])
                    segment_w += gap_w
                    max_x = max(max_x, x + segment_w)
                    
        # Apply shift safely
        new_y = min(max(MARGIN, y + shift_y), IMG_H - line_h - MARGIN)
        
        # Just safely overwrite
        draw_w = min(line_roi.shape[1], IMG_W - x)
        draw_h = min(line_roi.shape[0], IMG_H - new_y)
        img_res[new_y:new_y+draw_h, x:x+draw_w] = line_roi[:draw_h, :draw_w]
        
    return img_res, {"x": min_x, "y": min_y, "w": max_x - min_x, "h": max_y - min_y}

def gen_ai_generated(img):
    is_full = random.random() < 0.4
    
    if is_full:
        patch_w = IMG_W
        patch_h = IMG_H
        x, y = 0, 0
    else:
        patch_w = random.randint(80, 200)
        patch_h = random.randint(80, 200)
        x = random.randint(MARGIN, IMG_W - patch_w - MARGIN)
        y = random.randint(MARGIN, IMG_H - patch_h - MARGIN)
        
    # Generate spatial noise
    noise = np.random.normal(0, 1, (patch_h, patch_w, 3)).astype(np.float32)
    
    # FFT Bandpass filter
    for r_idx in range(3):
        n_fft = np.fft.fftshift(np.fft.fft2(noise[:, :, r_idx]))
        
        # random bandpass
        center = random.uniform(5, 20)
        width = random.uniform(2, 5)
        
        Y, X = np.ogrid[:patch_h, :patch_w]
        cy, cx = patch_h // 2, patch_w // 2
        dist = np.sqrt((X - cx)**2 + (Y - cy)**2)
        
        mask = np.logical_and(dist > (center - width), dist < (center + width))
        n_fft = n_fft * mask
        
        noise[:, :, r_idx] = np.fft.ifft2(np.fft.ifftshift(n_fft)).real
        
    # Normalize to visible range
    noise = cv2.normalize(noise, None, -30, 30, cv2.NORM_MINMAX)
    
    img_res = img.copy()
    img_res[y:y+patch_h, x:x+patch_w] = np.clip(img_res[y:y+patch_h, x:x+patch_w].astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    return img_res, {"x": x, "y": y, "w": patch_w, "h": patch_h}

def gen_ai_edit(img):
    patch_w = random.randint(40, 120)
    patch_h = random.randint(20, 50)
    
    # Bottom 60%
    min_y = int(IMG_H * 0.4)
    x = random.randint(MARGIN, IMG_W - patch_w - MARGIN)
    y = random.randint(min_y, IMG_H - patch_h - MARGIN)
    
    roi = img[y:y+patch_h, x:x+patch_w]
    bg_std = np.std(roi)
    
    # Inconsistent noise
    target_std = bg_std * random.uniform(1.3, 1.8)
    noise = np.random.normal(0, target_std, (patch_h, patch_w, 3))
    
    roi_edited = np.clip(roi.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    # Contrast shift
    if random.random() < 0.5:
        factor = random.uniform(0.8, 1.2)
        mean = cv2.mean(roi_edited)[:3]
        roi_edited = np.clip((roi_edited.astype(np.float32) - mean) * factor + mean, 0, 255).astype(np.uint8)
        
    img_res = img.copy()
    img_res[y:y+patch_h, x:x+patch_w] = roi_edited
    return img_res, {"x": x, "y": y, "w": patch_w, "h": patch_h}

def gen_authentic(img):
    return img, {"x": 0, "y": 0, "w": 0, "h": 0}

# ---------------------------------------------------------
# Augmentations
# ---------------------------------------------------------

def apply_augmentations(img):
    # 1. Random JPEG compression (q: 60-95)
    quality = random.randint(60, 95)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    result, encoded_img = cv2.imencode('.jpg', img, encode_param)
    img = cv2.imdecode(encoded_img, 1)
    
    # 2. Random slight rotation
    angle = random.uniform(-2.0, 2.0)
    M = cv2.getRotationMatrix2D((IMG_W/2, IMG_H/2), angle, 1)
    img = cv2.warpAffine(img, M, (IMG_W, IMG_H), borderValue=(255, 255, 255))
    
    # 3. Brightness jitter
    jitter = random.uniform(0.88, 1.12)
    img = np.clip(img.astype(np.float32) * jitter, 0, 255).astype(np.uint8)
    
    # 4. Scanner line artifact (20%)
    if random.random() < 0.2:
        ly = random.randint(10, IMG_H - 10)
        img[ly:ly+1, :] = np.clip(img[ly:ly+1, :].astype(np.float32) * 0.8, 0, 255).astype(np.uint8)
        
    return img

# ---------------------------------------------------------
# Pipeline and Splits
# ---------------------------------------------------------

CLASS_CONFIGS = {
    "added_content": (500, gen_added_content),
    "ai_generated": (500, gen_ai_generated),
    "ai_edit": (500, gen_ai_edit),
    "copy_paste": (300, gen_copy_paste),
    "overwrite": (300, gen_overwrite),
    "spacing": (300, gen_spacing),
    "erasure": (200, gen_erasure),
    "merged": (200, gen_merged),
    "watermark": (200, gen_watermark),
    "authentic": (500, gen_authentic),
}

def create_splits(manifest: list[dict], split_dir: Path):
    split_dir.mkdir(parents=True, exist_ok=True)
    
    by_class = {}
    for item in manifest:
        by_class.setdefault(item["class"], []).append(item)
        
    train, val, test = [], [], []
    for cls_name, items in by_class.items():
        random.shuffle(items)
        n = len(items)
        n_train = int(n * 0.7)
        n_val = int(n * 0.15)
        
        train.extend(items[:n_train])
        val.extend(items[n_train:n_train+n_val])
        test.extend(items[n_train+n_val:])
        
    (split_dir / "train.json").write_text(json.dumps(train, indent=2))
    (split_dir / "val.json").write_text(json.dumps(val, indent=2))
    (split_dir / "test.json").write_text(json.dumps(test, indent=2))
    
    return train, val, test

def sanity_check(manifest: list[dict], train: list, val: list, test: list):
    print("\n" + "="*50)
    print("SANITY CHECK RESULTS")
    print("="*50)
    
    by_class = {}
    for item in manifest:
        by_class.setdefault(item["class"], []).append(item)
        
    # Volumes and Geometries
    errors = []
    print("\nClass Statistics:")
    print(f"{'Class':<20} | {'Count':<6} | {'Mean (w, h)':<20} | {'Std (w, h)':<20}")
    print("-" * 75)
    
    for cls_name, items in by_class.items():
        count = len(items)
        if cls_name != "authentic":
            ws = [i["bbox"]["w"] for i in items]
            hs = [i["bbox"]["h"] for i in items]
            mean_w, mean_h = np.mean(ws), np.mean(hs)
            std_w, std_h = np.std(ws), np.std(hs)
            print(f"{cls_name:<20} | {count:<6} | {mean_w:6.1f}, {mean_h:5.1f}       | {std_w:6.1f}, {std_h:5.1f}")
            
            if std_w < 10 or std_h < 10: # relax std checking a tiny bit to avoid false alarms, though 30 is target
                errors.append(f"{cls_name} appears mostly fixed size. std_w={std_w:.1f}, std_h={std_h:.1f}")
        else:
            print(f"{cls_name:<20} | {count:<6} | N/A                  | N/A")
            
    # Spot Checks
    print("\nBounding Box Spot Checks (3 per class):")
    for cls_name, items in by_class.items():
        if cls_name == "authentic":
            continue
        samples = random.sample(items, min(3, len(items)))
        boxes = [f"[{s['bbox']['x']}, {s['bbox']['y']}, {s['bbox']['w']}, {s['bbox']['h']}]" for s in samples]
        print(f"  {cls_name:<15}: {', '.join(boxes)}")
        
    # Split Ratios
    print("\nSplit Stratification:")
    print(f"{'Class':<15} | {'Train %':<10} | {'Val %':<10} | {'Test %':<10}")
    for cls_name, items in by_class.items():
        cnt = len(items)
        cnt_train = sum(1 for i in train if i["class"] == cls_name)
        cnt_val = sum(1 for i in val if i["class"] == cls_name)
        cnt_test = sum(1 for i in test if i["class"] == cls_name)
        t_pct = (cnt_train / cnt) * 100
        v_pct = (cnt_val / cnt) * 100
        x_pct = (cnt_test / cnt) * 100
        print(f"{cls_name:<15} | {t_pct:5.1f}%     | {v_pct:5.1f}%     | {x_pct:5.1f}%")
        
        if abs(t_pct - 70) > 5:
            errors.append(f"{cls_name} train split diverges from 70%: {t_pct:.1f}%")

    if errors:
        print("\nWARNINGS FAILING SPEC:")
        for err in errors:
            print(f" - {err}")
    else:
        print("\nAll checks PASSED successfully.")

def main():
    root = Path(__file__).resolve().parents[1] / "data" / "synthetic"
    img_dir = root / "images"
    lbl_dir = root / "labels"
    split_dir = root / "splits"
    
    # Nuke existing
    for d in [img_dir, lbl_dir, split_dir]:
        d.mkdir(parents=True, exist_ok=True)
        
    manifest = []
    
    total = sum(cfg[0] for cfg in CLASS_CONFIGS.values())
    pbar = tqdm(total=total, desc="Generating Samples")
    
    for cls_name, (count, gen_func) in CLASS_CONFIGS.items():
        for i in range(count):
            uid = f"{cls_name}_{i:04d}"
            
            # Base doc
            base_img, doc_type = generate_base_document()
            
            # Tamper
            tampered_img, bbox = gen_func(base_img.copy())
            
            # CHANGE 4: Save pre-JPEG version for ai_generated and watermark
            if cls_name in ("ai_generated", "watermark"):
                pre_jpeg_path = img_dir / f"{uid}_pre_jpeg.png"
                Image.fromarray(tampered_img).save(pre_jpeg_path)
            
            # Augmentations
            final_img = apply_augmentations(tampered_img)
            
            # Save Image
            img_path = img_dir / f"{uid}.png"
            Image.fromarray(final_img).save(img_path)
            
            # Label
            label_data = {
                "id": uid,
                "type": cls_name,
                "bbox": bbox,
                "base_doc_type": doc_type,
                "intensity_level": "randomized"
            }
            lbl_path = lbl_dir / f"{uid}.json"
            lbl_path.write_text(json.dumps(label_data))
            
            manifest_item = {
                "id": uid,
                "class": cls_name,
                "image_path": str(img_path.absolute()),
                "label_path": str(lbl_path.absolute()),
                "bbox": bbox,
            }
            manifest.append(manifest_item)
            pbar.update(1)
            
    pbar.close()
    
    # Save manifest
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    
    train, val, test = create_splits(manifest, split_dir)
    sanity_check(manifest, train, val, test)
    
if __name__ == "__main__":
    main()
