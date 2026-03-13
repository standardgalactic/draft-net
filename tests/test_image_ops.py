from __future__ import annotations

import numpy as np

from draftnet.utils.image_ops import edge_magnitude, segmentation_mask, spectral_band_energies


def test_spectral_band_energies_normalize() -> None:
    image = np.zeros((8, 8, 3), dtype=np.float32)
    image[2:6, 2:6] = 1.0
    energies = spectral_band_energies(image, bands=4)
    assert len(energies) == 4
    assert abs(sum(energies) - 1.0) < 1e-5


def test_edge_magnitude_and_segmentation() -> None:
    image = np.zeros((8, 8, 3), dtype=np.float32)
    image[:, 4:] = 1.0
    edges = edge_magnitude(image)
    mask = segmentation_mask(image)
    assert float(edges.mean()) > 0.0
    assert 0.0 < float(mask.mean()) < 1.0
