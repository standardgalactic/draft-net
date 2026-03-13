from __future__ import annotations

from typing import List, Tuple


def dyadic_targets(num_states: int, level: int) -> List[Tuple[float, int]]:
    if num_states < 3 or level < 1:
        return []
    max_index = num_states - 1
    denom = 2 ** level
    out: list[tuple[float, int]] = []
    for k in range(1, denom):
        pos = round(k * max_index / denom)
        if 0 < pos < max_index:
            out.append((k / denom, pos))
    return sorted(set(out), key=lambda pair: pair[1])
