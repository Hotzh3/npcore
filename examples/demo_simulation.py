from npcore.brain import Brain
from npcore.npc import NPC
from npcore.environment import Environment


brain = Brain()


def idle_rule(context):
    return {"wait": 1.0}


def react_rule(npc, context):
    events = context.get("events", [])

    if "danger" in events:
        return {"run": 3.0, "defend": 1.0}

    return {"wait": 1.0}


brain.add_rule("idle", idle_rule)
brain.add_rule("react", react_rule)


guard = NPC("Guard", brain)
guard.set_state("react")
guard.set_group("guards")
guard.set_rank("leader")
guard.set_position(0, 0)
guard.set_goal("survive")
guard.set_emotion("fear", 0.5)

villager = NPC("Villager", brain)
villager.set_state("idle")
villager.set_group("villagers")
villager.set_position(1, 0)

scout = NPC("Scout", brain)
scout.set_state("react")
scout.set_group("guards")
scout.set_position(0, 1)
scout.set_emotion("fear", 0.2)

env = Environment()
env.add_npc(guard)
env.add_npc(villager)
env.add_npc(scout)

env.trigger_event("danger")

print("=== Simulation start ===")
history = env.run(5)

for i, step in enumerate(history, start=1):
    print(f"Step {i}: {step}")

print("\n=== Summary ===")
print(env.summary())