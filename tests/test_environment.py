from npcore.brain import Brain
from npcore.npc import NPC
from npcore.environment import Environment


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
    