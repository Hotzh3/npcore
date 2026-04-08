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

    def add_npc(self, npc: NPC) -> None:
        self.npcs.append(npc)

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
    