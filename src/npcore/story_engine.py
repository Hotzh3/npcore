from __future__ import annotations


class StoryEngine:
    """
    Generate simple narrative summaries from simulation history.
    """

    def generate(self, history: list[list[tuple[str, str]]]) -> list[str]:
        """
        Convert simulation history into a list of narrative sentences.
        """
        story: list[str] = []

        for step in history:
            for actor, action in step:
                if actor == "message":
                    continue

                sentence = self._describe_action(actor, action)
                story.append(sentence)

        return story

    def _describe_action(self, actor: str, action: str) -> str:
        """
        Convert one action into a simple narrative sentence.
        """
        action_map = {
            "run": f"{actor} ran during the simulation.",
            "wait": f"{actor} waited during the simulation.",
            "walk": f"{actor} walked during the simulation.",
            "rest": f"{actor} rested during the simulation.",
            "attack": f"{actor} attacked during the simulation.",
            "defend": f"{actor} defended during the simulation.",
            "follow": f"{actor} followed someone during the simulation.",
            "help": f"{actor} helped someone during the simulation.",
            "ignore": f"{actor} ignored someone during the simulation.",
        }

        return action_map.get(action, f"{actor} performed action '{action}'.")