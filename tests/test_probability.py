from npcore.probability import (
    normalize_probabilities,
    validate_probabilities,
    weighted_choice,
)


def test_validate_probabilities_accepts_valid_data():
    options = {"attack": 0.6, "defend": 0.3, "flee": 0.1}
    validate_probabilities(options)


def test_normalize_probabilities_sums_to_one():
    options = {"attack": 2, "defend": 1, "flee": 1}
    normalized = normalize_probabilities(options)
    assert abs(sum(normalized.values()) - 1.0) < 1e-9


def test_weighted_choice_returns_valid_action():
    options = {"attack": 0.6, "defend": 0.3, "flee": 0.1}
    result = weighted_choice(options)
    assert result in options
    