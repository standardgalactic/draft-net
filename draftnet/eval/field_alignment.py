from __future__ import annotations

from typing import Iterable, Mapping


def field_alignment(predicted: Iterable[Mapping[str, float]], target: Iterable[Mapping[str, float]]) -> dict[str, float]:
    totals = {"phi": 0.0, "v": 0.0, "s": 0.0}
    count = 0
    for p, t in zip(predicted, target):
        for key in totals:
            totals[key] += abs(float(p.get(key, 0.0)) - float(t.get(key, 0.0)))
        count += 1
    if count == 0:
        return {"phi_mae": 0.0, "v_mae": 0.0, "s_mae": 0.0}
    return {f"{k}_mae": v / count for k, v in totals.items()}
