from __future__ import annotations

from typing import List

import numpy as np

from draftnet.utils.image_ops import coarse_to_fine_pyramid, spectral_band_energies


def spectral_summary(image: np.ndarray, bands: int = 4) -> dict:
    return {
        'band_energies': spectral_band_energies(image, bands=bands),
        'pyramid_means': [float(level.mean()) for level in coarse_to_fine_pyramid(image, levels=bands)],
    }


def reverse_spectral_plan(image: np.ndarray, levels: int = 4) -> List[np.ndarray]:
    pyramid = coarse_to_fine_pyramid(image, levels=levels)
    stages: List[np.ndarray] = []
    for i in range(levels):
        radius = max(levels - i, 1)
        stages.append(pyramid[i])
    return stages
