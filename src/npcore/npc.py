from __future__ import annotations
from npcore.pathfinding import a_star
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
        self.memory_log: list[dict] = []

        # objetivos y prioridades
        self.goal: str | None = None
        self.priorities: dict[str, float] = {}

        # inventario
        self.inventory: list = []

        # posición en el entorno
        self.position: tuple[int, int] | None = None
        
        self.destination: tuple[int, int] | None = None

        # estructura social
        self.group: str | None = None
        self.rank: str | None = None
        self.reputation: dict[str, float] = {}

        # relaciones con otros NPCs
        self.relationships: dict[str, float] = {}
                
        # personalidad estable
        self.personality: dict[str, float] = {
            "aggression": 0.0,
            "sociability": 0.0,
            "fearfulness": 0.0,
            "loyalty": 0.0,
        }
        
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
            
    def remember_event(
        self,
        event_type: str,
        source: str | None = None,
        target: str | None = None,
        detail: str | None = None,
    ) -> None:
        """
        Store a structured event in memory.
        """
        event = {
            "type": event_type,
            "source": source,
            "target": target,
            "detail": detail,
        }
        self.memory_log.append(event)

    def get_memory_log(self) -> list[dict]:
        """
        Return the full structured memory log.
        """
        return self.memory_log

    def recall_last_event(self) -> dict | None:
        """
        Return the most recent structured memory event.
        """
        if not self.memory_log:
            return None
        return self.memory_log[-1]

    def recall_events_by_type(self, event_type: str) -> list[dict]:
        """
        Return structured memory events filtered by type.
        """
        return [event for event in self.memory_log if event["type"] == event_type]

    def set_goal(self, goal: str) -> None:
        self.goal = goal

    def set_priorities(self, priorities: dict[str, float]) -> None:
        self.priorities = priorities

    def set_position(self, x: int, y: int) -> None:
        self.position = (x, y)
        
        
    def set_destination(self, x: int, y: int) -> None:
        """
        Set a spatial destination for the NPC.
        """
        self.destination = (x, y)

    def clear_destination(self) -> None:
        """
        Clear the current destination.
        """
        self.destination = None

    def move_toward_destination(self) -> tuple[int, int] | None:
        """
        Move one step toward the current destination using simple axis-based movement.
        """
        if self.position is None or self.destination is None:
            return self.position

        x, y = self.position
        dx, dy = self.destination

        if x < dx:
            x += 1
        elif x > dx:
            x -= 1
        elif y < dy:
            y += 1
        elif y > dy:
            y -= 1

        self.position = (x, y)
        return self.position




    def move_smart(self, env):
        if self.position is None or self.destination is None:
            return self.position

        path = a_star(self.position, self.destination, env)

        if not path:
            return self.position

        self.position = path[0]
        return self.position
    
    def distance_to(self, x: int, y: int) -> int | None:
        """
        Return Manhattan distance from current position to a target cell.
        """
        if self.position is None:
            return None

        px, py = self.position
        return abs(px - x) + abs(py - y)

    def set_group(self, group: str) -> None:
        self.group = group

    def set_rank(self, rank: str) -> None:
        self.rank = rank

    def set_relationship(self, other_name: str, value: float) -> None:
        """
        Set relationship value with another NPC.
        """
        self.relationships[other_name] = value

    def change_relationship(self, other_name: str, delta: float) -> None:
        """
        Increase or decrease relationship value with another NPC.
        """
        current = self.relationships.get(other_name, 0.0)
        self.relationships[other_name] = current + delta

    def get_relationship(self, other_name: str) -> float:
        """
        Get relationship value with another NPC.
        """
        return self.relationships.get(other_name, 0.0)


    def set_personality_trait(self, trait: str, value: float) -> None:
        """
        Set a personality trait value.
        """
        self.personality[trait] = value

    def get_personality_trait(self, trait: str) -> float:
        """
        Get a personality trait value.
        """
        return self.personality.get(trait, 0.0)


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
    
    def get_learning_weight(self, action: str) -> float:
        """
        Convert past action success into a multiplicative learning weight.
        """
        success_rate = self.get_action_success_rate(action)

        if success_rate == 0.0:
            return 1.0

        return 1.0 + success_rate
    
    def choose_nearest_cell(self, cells: list[tuple[int, int]]) -> tuple[int, int] | None:
        """
        Choose the nearest cell from a list of positions.
        """
        if self.position is None or not cells:
            return None

        nearest = min(
            cells,
            key=lambda cell: abs(self.position[0] - cell[0]) + abs(self.position[1] - cell[1]),
        )
        return nearest
    
    def flee_to_zone(self, env, zone_name: str) -> tuple[int, int] | None:
        """
        Select the nearest cell in a zone and set it as destination.
        """
        zone_cells = env.get_zone_cells(zone_name)
        target = self.choose_nearest_cell(zone_cells)

        if target is None:
            return None

        self.destination = target
        return target
    
    def go_to_zone(self, env, zone_name: str) -> tuple[int, int] | None:
        """
        Select the nearest cell in a zone and set it as destination.
        """
        zone_cells = env.get_zone_cells(zone_name)
        target = self.choose_nearest_cell(zone_cells)

        if target is None:
            return None

        self.destination = target
        return target
    
    def pursue_goal_in_environment(self, env) -> tuple[int, int] | None:
        """
        Choose a destination zone based on the current goal.
        """
        if self.goal is None:
            return None

        goal_to_zone = {
            "trade": "market",
            "survive": "safe_house",
            "rest": "home",
        }

        zone_name = goal_to_zone.get(self.goal)
        if zone_name is None:
            return None

        return self.go_to_zone(env, zone_name)