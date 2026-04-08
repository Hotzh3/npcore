
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
        self.global_state = {}
        self.events = []

    def add_npc(self, npc: NPC) -> None:
        self.npcs.append(npc)

    def trigger_event(self, event: str) -> None:
        self.events.append(event)

    def get_nearby(self, npc: NPC, radius: int = 1) -> list[NPC]:
        """
        Return nearby NPCs based on Manhattan distance.
        """
        if npc.position is None:
            return []

        x1, y1 = npc.position
        nearby = []

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
            action = npc.act()
            results.append((npc.name, action))

        self.tick_count += 1
        return results

    def run(self, steps: int) -> list[list[tuple[str, str]]]:
        """
        Run multiple steps.
        """
        history = []
        for _ in range(steps):
            history.append(self.step())
        return history