from __future__ import annotations

from npcore.brain import Brain


class NPC:
    def __init__(self, name, brain):
        self.name = name
        self.brain = brain

        # estado actual
        self.state = None
        self.context = {}

        # memoria
        self.memory = {}

        # objetivos y prioridades
        self.goal = None
        self.priorities = {}

        # inventario
        self.inventory = []

        # posición
        self.position = None  # (x, y)

        # estructura social
        self.group = None
        self.rank = None
        self.reputation = {}

    def set_state(self, state: str) -> None:
        self.state = state

    def update_context(self, **kwargs) -> None:
        self.context.update(kwargs)

    def remember(self, key: str, value) -> None:
        self.memory[key] = value

    def recall(self, key: str, default=None):
        return self.memory.get(key, default)

    def forget(self, key: str) -> None:
        if key in self.memory:
            del self.memory[key]

    def set_goal(self, goal: str) -> None:
        self.goal = goal

    def set_priorities(self, priorities: dict[str, float]) -> None:
        self.priorities = priorities

    def set_position(self, x: int, y: int) -> None:
        self.position = (x, y)

    def set_group(self, group: str) -> None:
        self.group = group

    def set_rank(self, rank: str) -> None:
        self.rank = rank

    def get_social_influence(self, others: list["NPC"]) -> dict:
        influence = {
            "leaders": 0,
            "allies": 0,
            "others": 0,
        }

        for other in others:
            if other.group == self.group:
                influence["allies"] += 1
                if other.rank == "leader":
                    influence["leaders"] += 1
            else:
                influence["others"] += 1

        return influence

    def greet(self, other: "NPC") -> str:
        return f"{self.name} says hello to {other.name}"

    def act(self) -> str:
        return self.brain.decide(self.state, self.context, self)
    