from __future__ import annotations

from typing import Iterable

import numpy as np


def path_error(predicted: Iterable[Iterable[float]], target: Iterable[Iterable[float]]) -> float:
    total = 0.0
    count = 0
    for p, t in zip(predicted, target):
        pv = np.asarray(list(p), dtype=float)
        tv = np.asarray(list(t), dtype=float)
        total += float(np.linalg.norm(pv - tv) ** 2)
        count += 1
    return total / max(count, 1)
