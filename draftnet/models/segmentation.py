from __future__ import annotations

import numpy as np

from draftnet.utils.image_ops import apply_soft_foreground_blur, segmentation_mask


def estimate_foreground_mask(image: np.ndarray) -> np.ndarray:
    return segmentation_mask(image)


def early_stage_composite(image: np.ndarray, blur_radius: int = 4) -> tuple[np.ndarray, np.ndarray]:
    mask = estimate_foreground_mask(image)
    composite = apply_soft_foreground_blur(image, mask, radius=blur_radius)
    return composite, mask


def foreground_schedule(t: float, midpoint: float = 0.6, steepness: float = 10.0) -> float:
    t = float(t)
    return 1.0 / (1.0 + np.exp(-steepness * (t - midpoint)))
