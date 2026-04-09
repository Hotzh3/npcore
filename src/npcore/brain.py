from __future__ import annotations

from typing import Callable, Dict

from npcore.probability import weighted_choice
from npcore.utility import normalize_utilities


class Brain:
    """
    Decision engine for NPCs.

    Each state is associated with a rule function that returns
    a dictionary of actions and their weights/probabilities.

    During this refactor stage, rules can work in two ways:
    1. Legacy style: rule(context)
    2. Extended style: rule(npc, context)
    """

    def __init__(self) -> None:
        self.rules: Dict[str, Callable[..., dict[str, float]]] = {}

    def add_rule(self, state: str, func: Callable[..., dict[str, float]]) -> None:
        """
        Register a rule for a given state.
        """
        self.rules[state] = func

    def _resolve_probabilities(self, state: str, context: dict, npc=None) -> dict[str, float]:
        """
        Resolve the raw probabilities returned by a rule.
        """
        if state not in self.rules:
            raise ValueError(f"No rule defined for state '{state}'")

        rule = self.rules[state]

        if npc is None:
            return rule(context)

        try:
            return rule(npc, context)
        except TypeError:
            return rule(context)

    def _apply_priority_weights(self, probabilities: dict[str, float], npc=None) -> dict[str, float]:
        """
        Apply NPC priorities as multiplicative weights.
        """
        if npc is None or not npc.priorities:
            return dict(probabilities)

        adjusted = dict(probabilities)

        for action, value in adjusted.items():
            weight = npc.priorities.get(action, 1.0)
            adjusted[action] = value * weight

        return adjusted

    def _apply_emotions(self, probabilities: dict[str, float], npc=None) -> dict[str, float]:
        """
        Adjust action weights using NPC emotions.
        """
        if npc is None:
            return dict(probabilities)

        adjusted = dict(probabilities)

        fear = npc.get_emotion("fear")
        aggression = npc.get_emotion("aggression")

        for action, value in adjusted.items():
            if action in {"run", "hide"}:
                adjusted[action] = value * (1 + fear)

            if action in {"attack", "defend"}:
                adjusted[action] = adjusted[action] * (1 + aggression)

        return adjusted

    def _apply_goal(self, probabilities: dict[str, float], npc=None) -> dict[str, float]:
        """
        Adjust action weights according to the NPC goal.
        """
        if npc is None or not npc.goal:
            return dict(probabilities)

        adjusted = dict(probabilities)
        goal = npc.goal

        for action, value in adjusted.items():
            if goal == "survive" and action in {"run", "hide"}:
                adjusted[action] = value * 2

            if goal == "attack" and action == "attack":
                adjusted[action] = value * 2

        return adjusted

    def decide(self, state: str, context: dict, npc=None) -> str:
        """
        Decide an action based on state, context and optional NPC traits.
        """
        utilities = self._resolve_probabilities(state, context, npc)
        utilities = self._apply_priority_weights(utilities, npc)
        utilities = self._apply_emotions(utilities, npc)
        utilities = self._apply_goal(utilities, npc)

        probabilities = normalize_utilities(utilities)

        return weighted_choice(probabilities)