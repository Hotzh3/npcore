from __future__ import annotations


class BaseModule:
    """
    Base class for environment modules.
    """

    def before_step(self, env) -> None:
        """
        Hook called before each environment step.
        """
        pass

    def after_step(self, env, results: list[tuple[str, str]]) -> None:
        """
        Hook called after each environment step.
        """
        pass

    def on_event(self, env, event: dict) -> None:
        """
        Hook called whenever an event is triggered.
        """
        pass


class StepCounterModule(BaseModule):
    """
    Example module that counts how many times the environment stepped.
    """

    def __init__(self) -> None:
        self.before_calls = 0
        self.after_calls = 0

    def before_step(self, env) -> None:
        self.before_calls += 1

    def after_step(self, env, results: list[tuple[str, str]]) -> None:
        self.after_calls += 1
        