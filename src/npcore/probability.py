from __future__ import annotations

import random


def validate_probabilities(options: dict[str, float]) -> None:
    """
    Validate that a probability dictionary is usable.

    Rules:
    - must not be empty
    - all values must be numeric
    - no value can be negative
    - total must be greater than 0
    """
    if not options:
        raise ValueError("Options dictionary cannot be empty.")

    total = 0.0
    for action, weight in options.items():
        if not isinstance(weight, (int, float)):
            raise TypeError(f"Weight for '{action}' must be numeric.")
        if weight < 0:
            raise ValueError(f"Weight for '{action}' cannot be negative.")
        total += float(weight)

    if total <= 0:
        raise ValueError("Total probability weight must be greater than 0.")


def normalize_probabilities(options: dict[str, float]) -> dict[str, float]:
    """
    Convert raw weights into normalized probabilities that sum to 1.
    """
    validate_probabilities(options)
    total = sum(float(weight) for weight in options.values())
    return {action: float(weight) / total for action, weight in options.items()}


def weighted_choice(options: dict[str, float]) -> str:
    """
    Choose one action using weighted random selection.
    """
    validate_probabilities(options)
    actions = list(options.keys())
    weights = list(float(weight) for weight in options.values())
    return random.choices(actions, weights=weights, k=1)[0]