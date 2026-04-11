from npcore import npc
from npcore.brain import Brain
from npcore.npc import NPC
from npcore.environment import Environment
from npcore.story_engine import StoryEngine
from npcore.modules import StepCounterModule, BaseModule



def test_environment_runs():
    brain = Brain()

    def idle_rule(context):
        return {"walk": 0.5, "rest": 0.5}

    brain.add_rule("idle", idle_rule)

    npc = NPC("Guard", brain)
    npc.set_state("idle")

    env = Environment()
    env.add_npc(npc)

    results = env.step()

    assert len(results) == 1
    assert results[0][0] == "Guard"
    assert results[0][1] in {"walk", "rest"}


def test_npc_proximity_message():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    npc1 = NPC("Guard", brain)
    npc2 = NPC("Villager", brain)

    npc1.set_state("idle")
    npc2.set_state("idle")

    npc1.set_position(0, 0)
    npc2.set_position(1, 0)

    env = Environment()
    env.add_npc(npc1)
    env.add_npc(npc2)

    results = env.step()

    messages = [r for r in results if r[0] == "message"]

    assert len(messages) > 0


def test_environment_event_propagation():
    brain = Brain()

    def danger_rule(npc, context):
        events = context.get("events", [])

        if any(event["type"] == "danger" for event in events):
            return {"run": 1.0}

        return {"idle": 1.0}

    brain.add_rule("react", danger_rule)

    npc = NPC("Guard", brain)
    npc.set_state("react")

    env = Environment()
    env.add_npc(npc)

    env.trigger_event("danger")

    results = env.step()

    assert results[0][1] == "run"
    
    
def test_environment_tracks_history():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    npc = NPC("Guard", brain)
    npc.set_state("idle")

    env = Environment()
    env.add_npc(npc)

    env.run(3)

    assert len(env.history) == 3
    assert env.tick_count == 3
    
def test_environment_summary_contains_action_counts():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    npc = NPC("Guard", brain)
    npc.set_state("idle")

    env = Environment()
    env.add_npc(npc)

    env.run(2)

    summary = env.summary()

    assert summary["ticks"] == 2
    assert summary["npcs"] == 1
    assert summary["history_length"] == 2
    assert summary["action_counts"]["wait"] == 2
    
def test_trigger_event_converts_string_to_structured_event():
    env = Environment()

    env.trigger_event("danger")

    assert len(env.events) == 1
    assert env.events[0]["type"] == "danger"
    assert env.events[0]["severity"] == 1
    
def test_trigger_event_accepts_structured_event():
    env = Environment()

    env.trigger_event(
        {
            "type": "danger",
            "source": "enemy",
            "target": "Guard",
            "detail": "enemy nearby",
            "severity": 3,
        }
    )

    assert len(env.events) == 1
    assert env.events[0]["type"] == "danger"
    assert env.events[0]["source"] == "enemy"
    assert env.events[0]["severity"] == 3
    
def test_npc_receives_structured_events_in_context():
    brain = Brain()

    def inspect_rule(npc, context):
        events = context.get("events", [])

        if events and events[0]["type"] == "danger":
            return {"run": 1.0}

        return {"wait": 1.0}

    brain.add_rule("react", inspect_rule)

    npc = NPC("Guard", brain)
    npc.set_state("react")

    env = Environment()
    env.add_npc(npc)

    env.trigger_event(
        {
            "type": "danger",
            "source": "enemy",
            "detail": "close threat",
            "severity": 2,
        }
    )

    results = env.step()

    assert results[0][1] == "run"
    
def test_story_engine_generates_sentences_from_history():
    story_engine = StoryEngine()

    history = [
        [("Guard", "run"), ("Villager", "wait")],
        [("Scout", "defend")],
    ]

    story = story_engine.generate(history)

    assert len(story) == 3
    assert "Guard ran during the simulation." in story
    assert "Villager waited during the simulation." in story
    assert "Scout defended during the simulation." in story
    
def test_story_engine_ignores_message_entries():
    story_engine = StoryEngine()

    history = [
        [("Guard", "run"), ("message", "Guard says hello to Villager")],
    ]

    story = story_engine.generate(history)

    assert len(story) == 1
    assert story[0] == "Guard ran during the simulation."
    
def test_story_engine_handles_unknown_actions():
    story_engine = StoryEngine()

    history = [
        [("Guard", "trade")],
    ]

    story = story_engine.generate(history)

    assert story[0] == "Guard performed action 'trade'."

def test_render_grid_shows_npc_positions():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    guard = NPC("Guard", brain)
    villager = NPC("Villager", brain)

    guard.set_position(0, 0)
    villager.set_position(2, 0)

    env = Environment()
    env.add_npc(guard)
    env.add_npc(villager)

    grid = env.render_grid(width=3, height=2)

    assert "0 | G | . | V |" in grid
    assert "Legend:" in grid
    assert "G = Guard" in grid
    assert "V = Villager" in grid

def test_render_grid_ignores_npcs_without_position():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    guard = NPC("Guard", brain)
    villager = NPC("Villager", brain)

    guard.set_position(1, 0)

    env = Environment()
    env.add_npc(guard)
    env.add_npc(villager)

    grid = env.render_grid(width=3, height=2)

    assert "0 | . | G | . |" in grid
    assert "G = Guard" in grid
    assert "V = Villager" not in grid
    
def test_render_grid_ignores_npcs_outside_bounds():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    guard = NPC("Guard", brain)
    scout = NPC("Scout", brain)

    guard.set_position(0, 0)
    scout.set_position(5, 5)

    env = Environment()
    env.add_npc(guard)
    env.add_npc(scout)

    grid = env.render_grid(width=2, height=2)

    assert "0 | G | . |" in grid
    assert "G = Guard" in grid
    assert "S = Scout" not in grid
    
def test_environment_can_register_module():
    env = Environment()
    module = StepCounterModule()

    env.add_module(module)

    assert len(env.modules) == 1
    assert env.modules[0] is module
    
def test_module_hooks_run_during_step():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    npc = NPC("Guard", brain)
    npc.set_state("idle")

    env = Environment()
    env.add_npc(npc)

    module = StepCounterModule()
    env.add_module(module)

    env.step()

    assert module.before_calls == 1
    assert module.after_calls == 1
    
def test_module_on_event_hook_runs():
    class EventRecorderModule(BaseModule):
        def __init__(self) -> None:
            self.events_seen = []

        def on_event(self, env, event: dict) -> None:
            self.events_seen.append(event)

    env = Environment()
    module = EventRecorderModule()
    env.add_module(module)

    env.trigger_event("danger")

    assert len(module.events_seen) == 1
    assert module.events_seen[0]["type"] == "danger"
    
def test_environment_stores_world_dimensions():
    env = Environment(width=8, height=6)

    assert env.width == 8
    assert env.height == 6
    
def test_environment_can_register_zones():
    env = Environment(width=5, height=5)

    env.add_zone("safe_house", [(4, 4), (4, 3)])

    assert env.zones["safe_house"] == [(4, 4), (4, 3)]
    
def test_environment_can_find_zone_at_position():
    env = Environment(width=5, height=5)

    env.add_zone("market", [(1, 1), (1, 2)])

    assert env.get_zone_at(1, 1) == "market"
    assert env.get_zone_at(0, 0) is None
    
def test_environment_checks_bounds():
    env = Environment(width=3, height=3)

    assert env.is_within_bounds(0, 0) is True
    assert env.is_within_bounds(2, 2) is True
    assert env.is_within_bounds(3, 0) is False
    assert env.is_within_bounds(-1, 1) is False
    
def test_environment_can_return_zone_cells():
    env = Environment(width=5, height=5)
    env.add_zone("safe_house", [(4, 4), (4, 3)])

    cells = env.get_zone_cells("safe_house")

    assert cells == [(4, 4), (4, 3)]
    
def test_npc_can_choose_safe_zone_when_danger_exists():
    brain = Brain()

    def danger_rule(npc, context):
        events = context.get("events", [])
        env = context.get("environment")

        if any(event["type"] == "danger" for event in events):
            target = npc.flee_to_zone(env, "safe_house")
            if target is not None:
                return {"run": 1.0}

        return {"wait": 1.0}

    brain.add_rule("react", danger_rule)

    npc = NPC("Guard", brain)
    npc.set_state("react")
    npc.set_position(1, 1)

    env = Environment(width=5, height=5)
    env.add_zone("safe_house", [(4, 4), (2, 1)])
    env.add_npc(npc)

    env.trigger_event("danger")
    npc.update_context(environment=env, events=list(env.events))

    result = npc.act()

    assert result == "run"
    assert npc.destination == (2, 1)
    
def test_npc_waits_if_danger_exists_but_no_safe_zone():
    brain = Brain()

    def danger_rule(npc, context):
        events = context.get("events", [])
        env = context.get("environment")

        if any(event["type"] == "danger" for event in events):
            target = npc.flee_to_zone(env, "safe_house")
            if target is not None:
                return {"run": 1.0}

        return {"wait": 1.0}

    brain.add_rule("react", danger_rule)

    npc = NPC("Guard", brain)
    npc.set_state("react")
    npc.set_position(1, 1)

    env = Environment(width=5, height=5)
    env.add_npc(npc)

    env.trigger_event("danger")
    npc.update_context(environment=env, events=list(env.events))

    result = npc.act()

    assert result == "wait"
    assert npc.destination is None
    
def test_npc_can_choose_market_when_trade_goal_exists():
    brain = Brain()

    def trade_rule(npc, context):
        env = context.get("environment")
        target = npc.pursue_goal_in_environment(env)

        if target is not None:
            return {"move": 1.0}

        return {"wait": 1.0}

    brain.add_rule("trade", trade_rule)

    npc = NPC("Trader", brain)
    npc.set_state("trade")
    npc.set_goal("trade")
    npc.set_position(1, 1)

    env = Environment(width=5, height=5)
    env.add_zone("market", [(4, 4), (2, 1)])
    env.add_npc(npc)

    npc.update_context(environment=env)

    result = npc.act()

    assert result == "move"
    assert npc.destination == (2, 1)
    
def test_environment_can_add_blocked_cell():
    env = Environment(width=5, height=5)

    env.add_block(2, 2)

    assert env.is_blocked(2, 2) is True
    
def test_environment_can_remove_blocked_cell():
    env = Environment(width=5, height=5)

    env.add_block(2, 2)
    env.remove_block(2, 2)

    assert env.is_blocked(2, 2) is False        
    
def test_render_grid_shows_blocked_cells():
    env = Environment(width=3, height=2)
    env.add_block(1, 0)

    grid = env.render_grid()

    assert "0 | . | # | . |" in grid
    assert "# = blocked cell" in grid
    
def test_render_grid_shows_destination():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    npc = NPC("Guard", brain)
    npc.set_destination(2, 1)

    env = Environment(width=3, height=2)
    env.add_npc(npc)

    grid = env.render_grid()

    assert "1 | . | . | D |" in grid
    assert "D = destination" in grid
    
def test_render_grid_prioritizes_npc_over_destination():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    npc = NPC("Guard", brain)
    npc.set_position(2, 1)
    npc.set_destination(2, 1)

    env = Environment(width=3, height=2)
    env.add_npc(npc)

    grid = env.render_grid()

    assert "1 | . | . | G |" in grid
    assert "G = Guard" in grid
    
def test_environment_can_store_cell_cost():
    env = Environment(width=5, height=5)

    env.set_cell_cost(2, 2, 5)

    assert env.get_cell_cost(2, 2) == 5
    
def test_environment_cell_cost_defaults_to_one():
    env = Environment(width=5, height=5)

    assert env.get_cell_cost(0, 0) == 1
    
def test_environment_can_apply_zone_cost():
    env = Environment(width=5, height=5)
    env.add_zone("danger_zone", [(1, 1), (1, 2)])

    env.apply_zone_cost("danger_zone", 7)

    assert env.get_cell_cost(1, 1) == 7
    assert env.get_cell_cost(1, 2) == 7
    
def test_environment_can_clear_zone_cost():
    env = Environment(width=5, height=5)
    env.add_zone("danger_zone", [(1, 1), (1, 2)])

    env.apply_zone_cost("danger_zone", 7)
    env.clear_zone_cost("danger_zone")

    assert env.get_cell_cost(1, 1) == 1
    assert env.get_cell_cost(1, 2) == 1
    
def test_environment_can_measure_local_risk():
    env = Environment(width=5, height=5)
    env.set_cell_cost(1, 1, 5)
    env.set_cell_cost(2, 1, 3)

    risk = env.get_local_risk(1, 1, radius=1)

    assert risk >= 8    
    
def test_fearful_npc_prefers_run_when_local_risk_is_high():
    brain = Brain()

    def risk_rule(npc, context):
        env = context.get("environment")
        risk = npc.assess_local_risk(env)

        if risk is not None and risk >= 10:
            return {"run": 2.0, "wait": 1.0}

        return {"wait": 1.0}

    brain.add_rule("react", risk_rule)

    npc = NPC("Guard", brain)
    npc.set_state("react")
    npc.set_position(1, 1)
    npc.set_personality_trait("fearfulness", 1.0)

    env = Environment(width=5, height=5)
    env.set_cell_cost(1, 1, 5)
    env.set_cell_cost(2, 1, 5)
    env.add_npc(npc)

    npc.update_context(environment=env)

    results = [npc.act() for _ in range(100)]

    assert results.count("run") > results.count("wait")