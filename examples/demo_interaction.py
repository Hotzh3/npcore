from npcore.brain import Brain
from npcore.npc import NPC
from npcore.environment import Environment

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

print(env.step())