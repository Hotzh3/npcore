from __future__ import annotations

from typing import Callable, Dict

from npcore.probability import weighted_choice


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

    def decide(self, state: str, context: dict, npc=None) -> str:
        """
        Decide an action based on state and context.

        Parameters
        ----------
        state:
            Current state of the NPC.
        context:
            Context dictionary used by the rule.
        npc:
            Optional NPC instance. If provided, rules may use it to access
            memory, goals, inventory, group information, etc.
        """
        if state not in self.rules:
            raise ValueError(f"No rule defined for state '{state}'")

        rule = self.rules[state]

        if npc is None:
            probabilities = rule(context)
        else:
            try:
                probabilities = rule(npc, context)
            except TypeError:
                probabilities = rule(context)

        return weighted_choice(probabilities)
    