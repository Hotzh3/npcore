from __future__ import annotations

from typing import Callable, Dict

from npcore.probability import weighted_choice
from npcore.utility import normalize_utilities


class Brain:
    """
    Decision engine for NPCs.

    Each state is associated with a rule function that returns
    action scores/utilities.

    Rules can work in two ways:
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

    def _resolve_utilities(self, state: str, context: dict, npc=None) -> dict[str, float]:
        """
        Resolve raw action utilities returned by a rule.
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

    def _apply_priority_weights(self, utilities: dict[str, float], npc=None) -> dict[str, float]:
        """
        Apply NPC priorities as multiplicative weights.
        """
        if npc is None or not npc.priorities:
            return dict(utilities)

        adjusted = dict(utilities)

        for action, value in adjusted.items():
            weight = npc.priorities.get(action, 1.0)
            adjusted[action] = value * weight

        return adjusted

    def _apply_emotions(self, utilities: dict[str, float], npc=None) -> dict[str, float]:
        """
        Adjust action utilities using NPC emotions.
        """
        if npc is None:
            return dict(utilities)

        adjusted = dict(utilities)

        fear = npc.get_emotion("fear")
        aggression = npc.get_emotion("aggression")

        for action, value in adjusted.items():
            if action in {"run", "hide"}:
                adjusted[action] = value * (1 + fear)

            if action in {"attack", "defend"}:
                adjusted[action] = value * (1 + aggression)

        return adjusted

    def _apply_goal(self, utilities: dict[str, float], npc=None) -> dict[str, float]:
        if npc is None or not npc.goal:
            return dict(utilities)

        adjusted = dict(utilities)
        goal = npc.goal

        for action, value in adjusted.items():
            if goal == "survive" and action in {"run", "hide"}:
                adjusted[action] = value * 2

            if goal == "attack" and action == "attack":
                adjusted[action] = value * 2

        return adjusted


    def _apply_learning(self, utilities: dict[str, float], npc=None) -> dict[str, float]:
        """
        Adjust action utilities according to past success rates.
        """
        if npc is None:
            return dict(utilities)

        adjusted = dict(utilities)

        for action, value in adjusted.items():
            learning_weight = npc.get_learning_weight(action)
            adjusted[action] = value * learning_weight

        return adjusted

    def _apply_personality(self, utilities: dict[str, float], npc=None) -> dict[str, float]:
        """
        Adjust action utilities according to stable personality traits.
        """
        if npc is None:
            return dict(utilities)

        adjusted = dict(utilities)

        aggression = npc.get_personality_trait("aggression")
        sociability = npc.get_personality_trait("sociability")
        fearfulness = npc.get_personality_trait("fearfulness")
        loyalty = npc.get_personality_trait("loyalty")

        for action, value in adjusted.items():
            if action in {"attack", "defend"}:
                adjusted[action] = value * (1 + aggression)

            if action in {"talk", "help", "follow"}:
                adjusted[action] = adjusted[action] * (1 + sociability)

            if action in {"run", "hide"}:
                adjusted[action] = adjusted[action] * (1 + fearfulness)

            if action in {"help", "follow", "defend"}:
                adjusted[action] = adjusted[action] * (1 + loyalty)

        return adjusted

    def decide(self, state: str, context: dict, npc=None) -> str:
        """
        Decide an action based on state, context and optional NPC traits.
        """
        utilities = self._resolve_utilities(state, context, npc)
        utilities = self._apply_priority_weights(utilities, npc)
        utilities = self._apply_emotions(utilities, npc)
        utilities = self._apply_goal(utilities, npc)
        utilities = self._apply_learning(utilities, npc)
        utilities = self._apply_personality(utilities, npc)
        utilities = self._apply_internal_conflicts(utilities, npc)

        probabilities = normalize_utilities(utilities)

        return weighted_choice(probabilities)
    
    def _apply_internal_conflicts(self, utilities: dict[str, float], npc=None) -> dict[str, float]:
        """
        Adjust utilities when internal drives conflict.
        """
        if npc is None:
            return dict(utilities)

        adjusted = dict(utilities)

        fear = npc.get_emotion("fear") + npc.get_personality_trait("fearfulness")
        loyalty = npc.get_personality_trait("loyalty")
        aggression = npc.get_emotion("aggression") + npc.get_personality_trait("aggression")

        for action, value in adjusted.items():
            if action == "run":
                adjusted[action] = value * (1 + fear)

            if action in {"follow", "defend", "help"}:
                adjusted[action] = value * (1 + loyalty)

            if action == "attack":
                adjusted[action] = value * (1 + aggression)

        return adjusted