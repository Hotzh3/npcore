from __future__ import annotations

from typing import Callable, Dict

from npcore.probability import weighted_choice


class Brain:
    """
    Simple decision engine for NPCs.

    It maps a 'state' to possible actions with probabilities.
    """

    def __init__(self) -> None:
        self.rules: Dict[str, Callable[[dict], dict[str, float]]] = {}

    def add_rule(self, state: str, func: Callable[[dict], dict[str, float]]) -> None:
        """
        Add a rule that maps context -> action probabilities.
        """
        self.rules[state] = func

    def decide(self, state: str, context: dict) -> str:
        """
        Decide an action based on state and context.
        """
        if state not in self.rules:
            raise ValueError(f"No rule defined for state '{state}'")

        probabilities = self.rules[state](context)
        return weighted_choice(probabilities)
    