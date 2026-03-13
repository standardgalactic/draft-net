from __future__ import annotations

import numpy as np

from draftnet.encoders.base import BaseEncoder
from draftnet.utils.image_ops import edge_magnitude, luminance, segmentation_mask, spectral_band_energies


class ImageStatsEncoder(BaseEncoder):
    def __init__(self, embedding_dim: int = 256, bands: int = 4):
        self.embedding_dim = embedding_dim
        self.bands = bands

    def encode(self, content: np.ndarray) -> list[float]:
        image = np.asarray(content, dtype=np.float32)
        if image.ndim == 2:
            image = np.stack([image, image, image], axis=-1)
        gray = luminance(image)
        edges = edge_magnitude(image)
        mask = segmentation_mask(image)
        band_energies = spectral_band_energies(image, bands=self.bands)

        summary = np.array([
            float(image[..., 0].mean()),
            float(image[..., 1].mean()),
            float(image[..., 2].mean()),
            float(gray.mean()),
            float(gray.std()),
            float(edges.mean()),
            float(edges.std()),
            float(mask.mean()),
        ] + band_energies, dtype=np.float32)

        vec = np.zeros(self.embedding_dim, dtype=np.float32)
        used = min(len(summary), self.embedding_dim)
        vec[:used] = summary[:used]
        norm = np.linalg.norm(vec) + 1e-12
        return (vec / norm).astype(float).tolist()
