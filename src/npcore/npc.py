from __future__ import annotations

from npcore.brain import Brain


class NPC:
    """
    Represents a simple NPC with a state and a decision-making brain.
    """

    def __init__(self, name: str, brain: Brain) -> None:
        self.name = name
        self.brain = brain
        self.state = "idle"
        self.context: dict = {}

    def set_state(self, state: str) -> None:
        self.state = state

    def update_context(self, **kwargs) -> None:
        self.context.update(kwargs)

    def act(self) -> str:
        """
        Decide and return an action based on current state and context.
        """
        return self.brain.decide(self.state, self.context)
    