from __future__ import annotations

from npcore.brain import Brain


class NPC:
    """
    Represents an NPC with internal state, memory, social attributes,
    emotions, and a decision-making brain.
    """

    def __init__(self, name: str, brain: Brain) -> None:
        self.name = name
        self.brain = brain

        # estado actual y contexto inmediato
        self.state = "idle"
        self.context: dict = {}

        # memoria
        self.memory: dict = {}

        # objetivos y prioridades
        self.goal: str | None = None
        self.priorities: dict[str, float] = {}

        # inventario
        self.inventory: list = []

        # posición en el entorno
        self.position: tuple[int, int] | None = None

        # estructura social
        self.group: str | None = None
        self.rank: str | None = None
        self.reputation: dict[str, float] = {}

        # emociones
        self.emotions: dict[str, float] = {
            "fear": 0.0,
            "trust": 0.0,
            "aggression": 0.0,
        }
        
        # aprendizaje simple
        self.action_history: dict[str, list[bool]] = {}

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

    def set_emotion(self, emotion: str, value: float) -> None:
        self.emotions[emotion] = value

    def get_emotion(self, emotion: str) -> float:
        return self.emotions.get(emotion, 0.0)

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
        """
        Decide and return an action based on current state and context.
        """
        return self.brain.decide(self.state, self.context, self)
    
    def record_outcome(self, action: str, success: bool) -> None:
        """
        Store the outcome of an action.
        """
        if action not in self.action_history:
            self.action_history[action] = []

        self.action_history[action].append(success)


    def get_action_history(self, action: str) -> list[bool]:
        """
        Return stored outcomes for an action.
        """
        return self.action_history.get(action, [])


    def get_action_success_rate(self, action: str) -> float:
        """
        Return success rate for an action.
        """
        history = self.get_action_history(action)

        if not history:
            return 0.0

        return sum(history) / len(history)