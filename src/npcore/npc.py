from __future__ import annotations

from npcore.brain import Brain

class NPC:
    def __init__(self, name, brain):
        self.name = name
        self.brain = brain

        # estado actual
        self.state = None
        self.context = {}

        # --- NUEVA BASE DEL AGENTE ---

        # memoria (simple por ahora)
        self.memory = {}

        # objetivos y prioridades
        self.goal = None
        self.priorities = {}

        # inventario
        self.inventory = []

        # posición en el entorno
        self.position = None  # (x, y)

        # estructura social
        self.group = None
        self.rank = None
        self.reputation = {}

    def set_state(self, state: str) -> None:
        self.state = state

    def update_context(self, **kwargs) -> None:
        self.context.update(kwargs)

    def act(self) -> str:
        """
        Decide and return an action based on current state and context.
        """
        return self.brain.decide(self.state, self.context)
    