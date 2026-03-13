from __future__ import annotations

import math
import re
from collections import Counter

import numpy as np

from draftnet.encoders.base import BaseEncoder
from draftnet.encoders.rsvp_features import rsvp_features

WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)


class TextStatsEncoder(BaseEncoder):
    def __init__(self, embedding_dim: int = 256):
        self.embedding_dim = embedding_dim

    def _hashed_bow(self, text: str) -> np.ndarray:
        vec = np.zeros(self.embedding_dim, dtype=float)
        tokens = WORD_RE.findall(text.lower())
        counts = Counter(tokens)
        for token, count in counts.items():
            idx = hash(token) % self.embedding_dim
            vec[idx] += 1.0 + math.log1p(count)
        norm = np.linalg.norm(vec) + 1e-12
        return vec / norm

    def encode(self, content: str) -> list[float]:
        bow = self._hashed_bow(content)
        feats = rsvp_features(content)
        feature_tail = np.array([feats["phi"], feats["v"], feats["s"]], dtype=float)
        feature_tail = feature_tail / (np.linalg.norm(feature_tail) + 1e-12)
        merged = bow.copy()
        merged[:3] = feature_tail
        return merged.astype(float).tolist()
