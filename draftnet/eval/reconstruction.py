from __future__ import annotations

from typing import Iterable

import numpy as np


def mse(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    return float(np.mean((a - b) ** 2))


def mae(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    return float(np.mean(np.abs(a - b)))


def average_reconstruction_error(pairs: Iterable[tuple[np.ndarray, np.ndarray]]) -> dict:
    mses = []
    maes = []
    for pred, target in pairs:
        mses.append(mse(pred, target))
        maes.append(mae(pred, target))
    if not mses:
        return {'mse': 0.0, 'mae': 0.0}
    return {'mse': float(np.mean(mses)), 'mae': float(np.mean(maes))}
