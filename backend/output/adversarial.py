from __future__ import annotations

import numpy as np


def apply_attack(image: np.ndarray, attack_type: str) -> np.ndarray:
    attacked = image.astype(np.float32).copy()

    if attack_type == 'jpeg_recompress':
        # Approximate recompression by quantization and dequantization.
        attacked = np.round(attacked / 12.0) * 12.0
    elif attack_type == 'gaussian_noise':
        noise = np.random.normal(0, 9.0, attacked.shape)
        attacked = attacked + noise
    elif attack_type == 'geometric_warp':
        try:
            import cv2

            h, w = attacked.shape[:2]
            matrix = cv2.getRotationMatrix2D((w / 2, h / 2), 1.8, 1.0)
            attacked = cv2.warpAffine(attacked, matrix, (w, h), borderMode=cv2.BORDER_REFLECT)
        except Exception:
            attacked = np.roll(attacked, shift=2, axis=0)
    elif attack_type == 'downsample_upsample':
        try:
            import cv2

            h, w = attacked.shape[:2]
            small = cv2.resize(attacked, (max(32, w // 2), max(32, h // 2)), interpolation=cv2.INTER_AREA)
            attacked = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
        except Exception:
            attacked = attacked[::2, ::2]
            attacked = np.repeat(np.repeat(attacked, 2, axis=0), 2, axis=1)[: image.shape[0], : image.shape[1]]
    elif attack_type == 'color_jitter':
        attacked = attacked * 1.06 + 8.0
    else:
        return image

    attacked = np.clip(attacked, 0, 255)
    return attacked.astype(image.dtype)
