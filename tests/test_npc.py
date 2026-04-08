from npcore.brain import Brain
from npcore.npc import NPC


def test_npc_can_act():
    brain = Brain()

    def idle_rule(context):
        return {"walk": 0.5, "rest": 0.5}

    brain.add_rule("idle", idle_rule)

    npc = NPC(name="Guard", brain=brain)
    npc.set_state("idle")

    action = npc.act()

    assert action in {"walk", "rest"}
    
    
def test_npc_memory_remember_and_recall():
    brain = Brain()

    def idle_rule(context):
        return {"walk": 0.5, "rest": 0.5}

    brain.add_rule("idle", idle_rule)

    npc = NPC(name="Guard", brain=brain)
    npc.remember("last_action", "walk")

    assert npc.recall("last_action") == "walk"


def test_npc_memory_forget():
    brain = Brain()

    def idle_rule(context):
        return {"walk": 0.5, "rest": 0.5}

    brain.add_rule("idle", idle_rule)

    npc = NPC(name="Guard", brain=brain)
    npc.remember("last_action", "walk")
    npc.forget("last_action")

    assert npc.recall("last_action") is None
    