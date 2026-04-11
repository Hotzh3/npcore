from __future__ import annotations

from typing import List

from npcore.npc import NPC


class Environment:
    """
    Simple simulation environment for NPCs.
    """

    def __init__(self) -> None:
        self.npcs: List[NPC] = []
        self.tick_count = 0
        self.global_state: dict = {}
        self.events: list[str] = []
        self.history: list[list[tuple[str, str]]] = []

    def add_npc(self, npc: NPC) -> None:
        self.npcs.append(npc)

    def trigger_event(self, event) -> None:
        """
        Register an environment event.

        Events can be passed as a simple string or as a structured dict.
        """
        if isinstance(event, str):
            structured_event = {
                "type": event,
                "source": None,
                "target": None,
                "detail": None,
                "severity": 1,
            }
        else:
            structured_event = {
                "type": event.get("type"),
                "source": event.get("source"),
                "target": event.get("target"),
                "detail": event.get("detail"),
                "severity": event.get("severity", 1),
            }

        self.events.append(structured_event)

    def get_nearby(self, npc: NPC, radius: int = 1) -> list[NPC]:
        """
        Return nearby NPCs based on Manhattan distance.
        """
        if npc.position is None:
            return []

        x1, y1 = npc.position
        nearby: list[NPC] = []

        for other in self.npcs:
            if other is npc or other.position is None:
                continue

            x2, y2 = other.position
            distance = abs(x1 - x2) + abs(y1 - y2)

            if distance <= radius:
                nearby.append(other)

        return nearby

    def step(self) -> list[tuple[str, str]]:
        """
        Run one simulation step.
        Returns list of (npc_name, action)
        """
        results = []

        for npc in self.npcs:
            npc.update_context(events=list(self.events))
            action = npc.act()
            results.append((npc.name, action))

            nearby = self.get_nearby(npc)
            for other in nearby:
                message = npc.greet(other)
                results.append(("message", message))

        self.tick_count += 1
        self.history.append(results)
        return results

    def run(self, steps: int) -> list[list[tuple[str, str]]]:
        """
        Run multiple steps.
        """
        history = []
        for _ in range(steps):
            history.append(self.step())
        return history

    def action_counts(self) -> dict[str, int]:
        """
        Count how many times each action appears in the environment history.
        """
        counts: dict[str, int] = {}

        for step_results in self.history:
            for actor, action in step_results:
                if actor == "message":
                    continue
                counts[action] = counts.get(action, 0) + 1

        return counts

    def summary(self) -> dict:
        """
        Return a summary of the simulation.
        """
        return {
            "ticks": self.tick_count,
            "npcs": len(self.npcs),
            "history_length": len(self.history),
            "action_counts": self.action_counts(),
        }