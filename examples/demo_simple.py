from npcore.brain import Brain
from npcore.npc import NPC
from npcore.environment import Environment

brain = Brain()

def idle_rule(context):
    return {"walk": 0.5, "rest": 0.5}

brain.add_rule("idle", idle_rule)

npc = NPC("Guard", brain)
npc.set_state("idle")

env = Environment()
env.add_npc(npc)

print(env.step())