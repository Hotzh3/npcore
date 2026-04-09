from __future__ import annotations

from typing import Dict


def normalize_utilities(utilities: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize utilities into probabilities.
    """
    total = sum(utilities.values())

    if total <= 0:
        return dict(utilities)

    return {k: v / total for k, v in utilities.items()}


def softmax(utilities: Dict[str, float], temperature: float = 1.0) -> Dict[str, float]:
    """
    Convert utilities into probabilities using softmax.
    """
    import math

    exp_values = {
        k: math.exp(v / temperature) for k, v in utilities.items()
    }

    total = sum(exp_values.values())

    return {k: v / total for k, v in exp_values.items()}


def pick_best(utilities: Dict[str, float]) -> str:
    """
    Deterministic: choose the highest utility.
    """
    return max(utilities, key=utilities.get)
