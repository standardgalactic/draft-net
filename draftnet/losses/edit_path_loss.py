from __future__ import annotations

from draftnet.eval.edit_distance import edit_distance


def edit_path_loss(predicted_texts: list[str], target_texts: list[str]) -> float:
    if not predicted_texts or not target_texts:
        return 0.0
    total = 0.0
    count = 0
    for pred, target in zip(predicted_texts, target_texts):
        total += edit_distance(pred, target)
        count += 1
    return total / max(count, 1)
