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
    