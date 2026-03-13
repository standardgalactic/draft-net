from __future__ import annotations

from typing import Iterable

import numpy as np


def cosine_distance(a: Iterable[float], b: Iterable[float]) -> float:
    av = np.asarray(list(a), dtype=float)
    bv = np.asarray(list(b), dtype=float)
    denom = (np.linalg.norm(av) * np.linalg.norm(bv)) + 1e-12
    return float(1.0 - np.dot(av, bv) / denom)


def l2_distance(a: Iterable[float], b: Iterable[float]) -> float:
    av = np.asarray(list(a), dtype=float)
    bv = np.asarray(list(b), dtype=float)
    return float(np.linalg.norm(av - bv))
