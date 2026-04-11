from npcore.brain import Brain
from npcore.npc import NPC
from npcore.environment import Environment
from npcore.story_engine import StoryEngine


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