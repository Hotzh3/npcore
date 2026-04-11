from npcore.environment import Environment
from npcore.npc import NPC
from npcore.brain import Brain

brain = Brain()

def idle_rule(context):
    return {"wait": 1.0}

brain.add_rule("idle", idle_rule)

env = Environment()

npc1 = NPC("Guard", brain)
npc2 = NPC("Villager", brain)

npc1.set_position(0, 0)
npc2.set_position(2, 1)

env.add_npc(npc1)
env.add_npc(npc2)

env.render_matplotlib()

## corre esto en terminal: PYTHONPATH=src python examples/demo_visualization.py
