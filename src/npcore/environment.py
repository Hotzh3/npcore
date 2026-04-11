from __future__ import annotations

from typing import List

from npcore.npc import NPC


class Environment:
    """
    Simple simulation environment for NPCs.
    """

    def __init__(self, width: int = 10, height: int = 10) -> None:
        self.npcs: List[NPC] = []
        self.tick_count = 0
        self.global_state: dict = {}
        self.events: list[str] = []
        self.history: list[list[tuple[str, str]]] = []
        self.modules: list = []
        self.width = width
        self.height = height
        self.zones: dict[str, list[tuple[int, int]]] = {}
        self.blocked_cells: set[tuple[int, int]] = set()

    def add_npc(self, npc: NPC) -> None:
        self.npcs.append(npc)
        
    def add_module(self, module) -> None:
        """
        Register an environment module.
        """
        self.modules.append(module)

    def add_zone(self, name: str, cells: list[tuple[int, int]]) -> None:
        """
        Register a named zone in the environment.
        """
        self.zones[name] = cells
        
    def get_zone_cells(self, name: str) -> list[tuple[int, int]]:
        """
        Return all cells belonging to a named zone.
        """
        return self.zones.get(name, [])

    def get_zone_at(self, x: int, y: int) -> str | None:
        """
        Return the name of the zone occupying a cell, if any.
        """
        for zone_name, cells in self.zones.items():
            if (x, y) in cells:
                return zone_name
        return None

    def is_within_bounds(self, x: int, y: int) -> bool:
        """
        Check whether a position is inside the world bounds.
        """
        return 0 <= x < self.width and 0 <= y < self.height


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
            
        for module in self.modules:
            module.on_event(self, structured_event)

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
        
        for module in self.modules:
            module.before_step(self)

        for npc in self.npcs:
            npc.update_context(events=list(self.events))
            action = npc.act()
            results.append((npc.name, action))

            nearby = self.get_nearby(npc)
            for other in nearby:
                message = npc.greet(other)
                results.append(("message", message))

        for module in self.modules:
            module.after_step(self, results)


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
        
    def render_grid(self, width: int, height: int) -> str:
        """
        Render NPC positions as a professional ASCII grid with coordinates and legend.
        """
        grid = [["." for _ in range(width)] for _ in range(height)]
        legend: dict[str, str] = {}

        for npc in self.npcs:
            if npc.position is None:
                continue

            x, y = npc.position

            if 0 <= x < width and 0 <= y < height:
                symbol = npc.name[0].upper()
                grid[y][x] = symbol
                legend[symbol] = npc.name

        header = "    " + "   ".join(str(x) for x in range(width))
        separator = "  +" + "+".join(["---"] * width) + "+"

        rows = [header, separator]

        for y, row in enumerate(grid):
            row_text = f"{y} | " + " | ".join(row) + " |"
            rows.append(row_text)
            rows.append(separator)

        if legend:
            rows.append("")
            rows.append("Legend:")
            for symbol, name in sorted(legend.items()):
                rows.append(f"{symbol} = {name}")

        return "\n".join(rows)
    
    def render_matplotlib(self):
        """
        Render NPC positions using matplotlib for a more professional visualization.
        """
        import matplotlib.pyplot as plt

        x_coords = []
        y_coords = []
        labels = []

        for npc in self.npcs:
            if npc.position is None:
                continue

            x, y = npc.position
            x_coords.append(x)
            y_coords.append(y)
            labels.append(npc.name)

        plt.figure()
        plt.scatter(x_coords, y_coords)

        for i, label in enumerate(labels):
            plt.text(x_coords[i], y_coords[i], label)

        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("NPC World Visualization")
        plt.grid()

        plt.show()
        
    def get_zone_cells(self, zone_name: str) -> list[tuple[int, int]]:
        return self.zones.get(zone_name, [])
    
    def add_block(self, x: int, y: int) -> None:
        """
        Mark a cell as blocked.
        """
        if self.is_within_bounds(x, y):
            self.blocked_cells.add((x, y))

    def remove_block(self, x: int, y: int) -> None:
        """
        Remove a blocked cell.
        """
        self.blocked_cells.discard((x, y))

    def is_blocked(self, x: int, y: int) -> bool:
        """
        Check whether a cell is blocked.
        """
        return (x, y) in self.blocked_cells