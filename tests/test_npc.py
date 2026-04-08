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
    
def test_npc_goal_setting():
    brain = Brain()

    def idle_rule(context):
        return {"walk": 0.5, "rest": 0.5}

    brain.add_rule("idle", idle_rule)

    npc = NPC(name="Guard", brain=brain)
    npc.set_goal("survive")

    assert npc.goal == "survive"


def test_npc_priorities_setting():
    brain = Brain()

    def idle_rule(context):
        return {"walk": 0.5, "rest": 0.5}

    brain.add_rule("idle", idle_rule)

    npc = NPC(name="Guard", brain=brain)

    priorities = {"survival": 0.9, "combat": 0.3}
    npc.set_priorities(priorities)

    assert npc.priorities == priorities

def test_npc_group_setting():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    npc = NPC(name="Guard", brain=brain)
    npc.set_group("guards")

    assert npc.group == "guards"


def test_npc_rank_setting():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    npc = NPC(name="Guard", brain=brain)
    npc.set_rank("leader")

    assert npc.rank == "leader"

def test_social_influence_counts():
    brain = Brain()

    def idle_rule(context):
        return {"wait": 1.0}

    brain.add_rule("idle", idle_rule)

    npc = NPC("A", brain)
    npc.set_group("guards")

    leader = NPC("Leader", brain)
    leader.set_group("guards")
    leader.set_rank("leader")

    ally = NPC("Ally", brain)
    ally.set_group("guards")

    outsider = NPC("Stranger", brain)
    outsider.set_group("villagers")

    influence = npc.get_social_influence([leader, ally, outsider])

    assert influence["leaders"] == 1
    assert influence["allies"] == 2
    assert influence["others"] == 1

def social_rule(npc, context):
    nearby = context.get("nearby", [])
    influence = npc.get_social_influence(nearby)

    if influence["leaders"] > 0:
        return {"follow": 0.8, "wait": 0.2}

    if influence["others"] > 0:
        return {"defend": 0.7, "observe": 0.3}

    return {"idle": 1.0}

def test_npc_decision_with_social_influence():
    brain = Brain()

    def social_rule(npc, context):
        nearby = context.get("nearby", [])
        influence = npc.get_social_influence(nearby)

        if influence["leaders"] > 0:
            return {"follow": 1.0}

        return {"idle": 1.0}

    brain.add_rule("social", social_rule)

    npc = NPC("A", brain)
    npc.set_state("social")
    npc.set_group("guards")

    leader = NPC("Leader", brain)
    leader.set_group("guards")
    leader.set_rank("leader")

    npc.update_context(nearby=[leader])

    action = npc.act()

    assert action == "follow"