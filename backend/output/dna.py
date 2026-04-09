from __future__ import annotations

from hashlib import sha256

import numpy as np


def hash_payload(payload: bytes) -> str:
    return sha256(payload).hexdigest()


def scanner_profile_from_image(image: np.ndarray) -> str:
    arr = image.astype(np.float32)
    if arr.ndim == 3:
        arr = np.mean(arr, axis=2)

    h, w = arr.shape
    margin_h = max(4, h // 12)
    margin_w = max(4, w // 12)

    border = np.concatenate(
        [
            arr[:margin_h, :].ravel(),
            arr[-margin_h:, :].ravel(),
            arr[:, :margin_w].ravel(),
            arr[:, -margin_w:].ravel(),
        ]
    )
    noise = float(np.std(border))
    return f'noise-profile-{noise:.2f}'


def build_dna_id(digest: str) -> str:
    return f'DNA-{digest[:8].upper()}'
