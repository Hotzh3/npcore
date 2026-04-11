from npcore import npc
from npcore.brain import Brain
from npcore.npc import NPC
from npcore.environment import Environment


def make_brain(action_map: dict[str, float] | None = None) -> Brain:
    """
    Build a simple brain for tests.
    """
    brain = Brain()

    if action_map is None:
        action_map = {"wait": 1.0}

    def idle_rule(context):
        return action_map

    brain.add_rule("idle", idle_rule)
    return brain


def test_npc_can_act():
    brain = make_brain({"walk": 0.5, "rest": 0.5})

    npc = NPC(name="Guard", brain=brain)
    npc.set_state("idle")

    action = npc.act()

    assert action in {"walk", "rest"}


def test_npc_goal_setting():
    brain = make_brain({"walk": 0.5, "rest": 0.5})

    npc = NPC(name="Guard", brain=brain)
    npc.set_goal("survive")

    assert npc.goal == "survive"


def test_npc_priorities_setting():
    brain = make_brain({"walk": 0.5, "rest": 0.5})

    npc = NPC(name="Guard", brain=brain)
    priorities = {"survival": 0.9, "combat": 0.3}
    npc.set_priorities(priorities)

    assert npc.priorities == priorities


def test_npc_group_setting():
    brain = make_brain()

    npc = NPC(name="Guard", brain=brain)
    npc.set_group("guards")

    assert npc.group == "guards"


def test_npc_rank_setting():
    brain = make_brain()

    npc = NPC(name="Guard", brain=brain)
    npc.set_rank("leader")

    assert npc.rank == "leader"


def test_social_influence_counts():
    brain = make_brain()

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

    assert influence == {"leaders": 1, "allies": 2, "others": 1}


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

def test_utility_weights_favor_higher_score():
    brain = Brain()

    def rule(context):
        return {"run": 3.0, "walk": 1.0}

    brain.add_rule("idle", rule)

    npc = NPC("Guard", brain)
    npc.set_state("idle")

    results = [npc.act() for _ in range(200)]

    assert results.count("run") > results.count("walk")
    
def test_npc_can_record_action_outcome():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.record_outcome("run", True)
    npc.record_outcome("run", False)

    assert npc.get_action_history("run") == [True, False]


def test_npc_action_success_rate():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.record_outcome("run", True)
    npc.record_outcome("run", True)
    npc.record_outcome("run", False)

    assert npc.get_action_success_rate("run") == 2 / 3
    
def test_learning_increases_previously_successful_action():
    brain = Brain()

    def rule(context):
        return {"run": 1.0, "walk": 1.0}

    brain.add_rule("idle", rule)

    npc = NPC("Guard", brain)
    npc.set_state("idle")

    npc.record_outcome("run", True)
    npc.record_outcome("run", True)
    npc.record_outcome("run", True)

    results = [npc.act() for _ in range(100)]

    assert results.count("run") > results.count("walk")
    
def test_learning_does_not_boost_action_without_history():
    brain = Brain()

    def rule(context):
        return {"run": 1.0, "walk": 1.0}

    brain.add_rule("idle", rule)

    npc = NPC("Guard", brain)
    npc.set_state("idle")

    npc.record_outcome("run", True)

    history_run = npc.get_action_success_rate("run")
    history_walk = npc.get_action_success_rate("walk")

    assert history_run > history_walk
    
def test_npc_can_set_relationship():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.set_relationship("Villager", 0.8)

    assert npc.get_relationship("Villager") == 0.8


def test_npc_can_change_relationship():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.set_relationship("Villager", 0.5)
    npc.change_relationship("Villager", 0.2)

    assert npc.get_relationship("Villager") == 0.7


def test_npc_relationship_defaults_to_zero():
    brain = make_brain()

    npc = NPC("Guard", brain)

    assert npc.get_relationship("Unknown") == 0.0
    
def test_relationship_can_influence_decision():
    brain = Brain()

    def social_rule(npc, context):
        target = context.get("target")

        if target is None:
            return {"wait": 1.0}

        relationship = npc.get_relationship(target.name)

        if relationship > 0.5:
            return {"help": 1.0}

        return {"ignore": 1.0}

    brain.add_rule("social", social_rule)

    guard = NPC("Guard", brain)
    villager = NPC("Villager", brain)

    guard.set_state("social")
    guard.set_relationship("Villager", 0.9)
    guard.update_context(target=villager)

    action = guard.act()

    assert action == "help"
    
def test_npc_can_set_personality_trait():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.set_personality_trait("aggression", 0.8)

    assert npc.get_personality_trait("aggression") == 0.8

def test_npc_personality_trait_defaults_to_zero():
    brain = make_brain()

    npc = NPC("Guard", brain)

    assert npc.get_personality_trait("curiosity") == 0.0
    
def test_aggressive_personality_favors_attack():
    brain = Brain()

    def rule(context):
        return {"attack": 1.0, "wait": 1.0}

    brain.add_rule("idle", rule)

    npc = NPC("Guard", brain)
    npc.set_state("idle")
    npc.set_personality_trait("aggression", 1.0)

    results = [npc.act() for _ in range(100)]

    assert results.count("attack") > results.count("wait")
    
def test_fearful_personality_favors_run():
    brain = Brain()

    def rule(context):
        return {"run": 1.0, "wait": 1.0}

    brain.add_rule("idle", rule)

    npc = NPC("Guard", brain)
    npc.set_state("idle")
    npc.set_personality_trait("fearfulness", 1.0)

    results = [npc.act() for _ in range(100)]

    assert results.count("run") > results.count("wait")
    
    
def test_npc_can_remember_structured_event():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.remember_event(
        event_type="danger",
        source="Scout",
        target="Guard",
        detail="enemy nearby",
    )

    memory_log = npc.get_memory_log()

    assert len(memory_log) == 1
    assert memory_log[0]["type"] == "danger"
    assert memory_log[0]["source"] == "Scout"
    
def test_npc_can_recall_last_event():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.remember_event("danger", source="Scout")
    npc.remember_event("help", source="Villager")

    last_event = npc.recall_last_event()

    assert last_event is not None
    assert last_event["type"] == "help"
    assert last_event["source"] == "Villager"
    
def test_npc_can_recall_events_by_type():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.remember_event("danger", source="Scout")
    npc.remember_event("danger", source="Enemy")
    npc.remember_event("help", source="Villager")

    danger_events = npc.recall_events_by_type("danger")

    assert len(danger_events) == 2
    assert all(event["type"] == "danger" for event in danger_events)

def test_recall_last_event_returns_none_when_empty():
    brain = make_brain()

    npc = NPC("Guard", brain)

    assert npc.recall_last_event() is None
    
def test_learning_weight_defaults_to_one_without_history():
    brain = make_brain()

    npc = NPC("Guard", brain)

    assert npc.get_learning_weight("run") == 1.0

def test_learning_weight_increases_with_success():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.record_outcome("run", True)
    npc.record_outcome("run", True)
    npc.record_outcome("run", False)

    assert npc.get_learning_weight("run") > 1.0 
    
def test_learning_favors_action_with_better_history():
    brain = Brain()

    def rule(context):
        return {"run": 1.0, "walk": 1.0}

    brain.add_rule("idle", rule)

    npc = NPC("Guard", brain)
    npc.set_state("idle")

    npc.record_outcome("run", True)
    npc.record_outcome("run", True)
    npc.record_outcome("run", True)

    npc.record_outcome("walk", False)
    
    utilities = {"run": 1.0, "walk": 1.0}
    adjusted = brain._apply_learning(utilities, npc)

    assert adjusted["run"] > adjusted["walk"]
    
def test_npc_can_set_destination():
    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_destination(4, 4)

    assert npc.destination == (4, 4)
    
def test_npc_can_clear_destination():
    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_destination(4, 4)
    npc.clear_destination()

    assert npc.destination is None
    
def test_npc_moves_toward_destination_on_x_axis():
    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_position(0, 0)
    npc.set_destination(2, 0)

    new_position = npc.move_toward_destination()

    assert new_position == (1, 0)
    
def test_npc_moves_toward_destination_on_y_axis():
    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_position(2, 0)
    npc.set_destination(2, 2)

    new_position = npc.move_toward_destination()

    assert new_position == (2, 1)
    
def test_npc_does_not_move_without_position():
    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_destination(2, 2)

    assert npc.move_toward_destination() is None
    
def test_npc_can_measure_distance_to_cell():
    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_position(1, 1)

    assert npc.distance_to(3, 2) == 3
    
def test_npc_can_choose_nearest_cell():
    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_position(1, 1)

    nearest = npc.choose_nearest_cell([(4, 4), (2, 1), (0, 0)])

    assert nearest == (2, 1)
    
def test_npc_returns_none_for_nearest_cell_without_position():
    brain = make_brain()
    npc = NPC("Guard", brain)

    nearest = npc.choose_nearest_cell([(4, 4), (2, 1)])

    assert nearest is None
    
def test_npc_can_flee_to_zone():
    brain = make_brain()
    npc = NPC("Guard", brain)
    npc.set_position(1, 1)

    env = Environment(width=5, height=5)
    env.add_zone("safe_house", [(4, 4), (2, 1), (3, 3)])

    target = npc.flee_to_zone(env, "safe_house")

    assert target == (2, 1)
    assert npc.destination == (2, 1)
    
def test_npc_flee_to_zone_returns_none_when_zone_missing():
    brain = make_brain()
    npc = NPC("Guard", brain)
    npc.set_position(1, 1)

    env = Environment(width=5, height=5)

    target = npc.flee_to_zone(env, "safe_house")

    assert target is None
    assert npc.destination is None
    
def test_npc_can_go_to_zone():
    brain = make_brain()
    npc = NPC("Guard", brain)
    npc.set_position(1, 1)

    env = Environment(width=5, height=5)
    env.add_zone("market", [(4, 4), (2, 1), (3, 3)])

    target = npc.go_to_zone(env, "market")

    assert target == (2, 1)
    assert npc.destination == (2, 1)
    
def test_npc_go_to_zone_returns_none_when_zone_missing():
    brain = make_brain()
    npc = NPC("Guard", brain)
    npc.set_position(1, 1)

    env = Environment(width=5, height=5)

    target = npc.go_to_zone(env, "market")

    assert target is None
    assert npc.destination is None

def test_npc_can_pursue_trade_goal_in_environment():
    brain = make_brain()
    npc = NPC("Trader", brain)
    npc.set_position(1, 1)
    npc.set_goal("trade")

    env = Environment(width=5, height=5)
    env.add_zone("market", [(4, 4), (2, 1)])

    target = npc.pursue_goal_in_environment(env)

    assert target == (2, 1)
    assert npc.destination == (2, 1)
    
def test_npc_can_pursue_survive_goal_in_environment():
    brain = make_brain()
    npc = NPC("Guard", brain)
    npc.set_position(1, 1)
    npc.set_goal("survive")

    env = Environment(width=5, height=5)
    env.add_zone("safe_house", [(4, 4), (3, 1)])

    target = npc.pursue_goal_in_environment(env)

    assert target == (3, 1)
    assert npc.destination == (3, 1)
    
def test_npc_pursue_goal_returns_none_when_goal_has_no_zone():
    brain = make_brain()
    npc = NPC("Guard", brain)
    npc.set_position(1, 1)
    npc.set_goal("attack")

    env = Environment(width=5, height=5)
    env.add_zone("market", [(2, 2)])

    target = npc.pursue_goal_in_environment(env)

    assert target is None
    assert npc.destination is None      


def test_learning_increases_run_utility_directly():
    brain = Brain()

    def rule(context):
        return {"run": 1.0, "walk": 1.0}

    brain.add_rule("idle", rule)

    npc = NPC("Guard", brain)
    npc.record_outcome("run", True)
    npc.record_outcome("run", True)
    npc.record_outcome("run", True)

    utilities = {"run": 1.0, "walk": 1.0}
    adjusted = brain._apply_learning(utilities, npc)

    assert adjusted["run"] > adjusted["walk"]
    
def test_npc_moves_using_pathfinding():
    from npcore.environment import Environment

    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_position(0, 0)
    npc.set_destination(2, 0)

    env = Environment(width=5, height=5)

    new_pos = npc.move_smart(env)

    assert new_pos == (1, 0)
    
def test_npc_flee_sets_destination():
    from npcore.environment import Environment

    brain = make_brain()
    npc = NPC("Guard", brain)
    npc.set_position(1, 1)

    env = Environment(width=5, height=5)
    env.add_zone("safe_house", [(4, 4), (2, 1)])

    target = npc.flee_to_zone(env, "safe_house")

    assert target in [(4, 4), (2, 1)]
    assert npc.destination == target
    
def test_npc_pursues_goal():
    from npcore.environment import Environment

    brain = make_brain()
    npc = NPC("Guard", brain)
    npc.set_position(0, 0)
    npc.set_goal("survive")

    env = Environment(width=5, height=5)
    env.add_zone("safe_house", [(4, 4)])

    target = npc.pursue_goal_in_environment(env)

    assert target == (4, 4)
    
def test_npc_move_smart_avoids_blocked_cell():
    from npcore.environment import Environment

    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_position(0, 0)
    npc.set_destination(2, 0)

    env = Environment(width=5, height=5)
    env.add_block(1, 0)

    new_pos = npc.move_smart(env)

    assert new_pos != (1, 0)
    assert new_pos in {(0, 1)}
    
def test_npc_move_smart_returns_same_position_if_path_blocked():
    from npcore.environment import Environment

    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_position(0, 0)
    npc.set_destination(1, 1)

    env = Environment(width=2, height=2)
    env.add_block(1, 0)
    env.add_block(0, 1)

    new_pos = npc.move_smart(env)

    assert new_pos == (0, 0)
    
def test_npc_move_smart_avoids_high_cost_cell():
    from npcore.environment import Environment

    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_position(0, 0)
    npc.set_destination(2, 0)

    env = Environment(width=3, height=2)
    env.set_cell_cost(1, 0, 10)

    new_pos = npc.move_smart(env)

    assert new_pos == (0, 1)
    
    
def test_npc_move_smart_avoids_danger_zone_cost():
    from npcore.environment import Environment

    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_position(0, 0)
    npc.set_destination(2, 0)

    env = Environment(width=3, height=2)
    env.add_zone("danger_zone", [(1, 0)])
    env.apply_zone_cost("danger_zone", 10)

    new_pos = npc.move_smart(env)

    assert new_pos == (0, 1)
    
def test_npc_can_assess_local_risk():
    from npcore.environment import Environment

    brain = make_brain()
    npc = NPC("Guard", brain)
    npc.set_position(1, 1)

    env = Environment(width=5, height=5)
    env.set_cell_cost(1, 1, 5)
    env.set_cell_cost(2, 1, 3)

    risk = npc.assess_local_risk(env)

    assert risk is not None
    assert risk >= 8    
    
def test_npc_can_detect_allies_nearby():
    brain = make_brain()

    guard = NPC("Guard", brain)
    ally = NPC("Scout", brain)
    outsider = NPC("Villager", brain)

    guard.set_group("guards")
    ally.set_group("guards")
    outsider.set_group("villagers")

    nearby = guard.get_allies_nearby([ally, outsider])

    assert ally in nearby
    assert outsider not in nearby   
    
def test_npc_can_regroup_with_allies():
    brain = make_brain()

    guard = NPC("Guard", brain)
    scout = NPC("Scout", brain)

    guard.set_group("guards")
    scout.set_group("guards")

    guard.set_position(0, 0)
    scout.set_position(2, 1)

    destination = guard.regroup_with_allies([scout])

    assert destination == (2, 1)
    assert guard.destination == (2, 1)
    
def test_npc_regroup_returns_none_without_allies():
    brain = make_brain()

    guard = NPC("Guard", brain)
    villager = NPC("Villager", brain)

    guard.set_group("guards")
    villager.set_group("villagers")

    guard.set_position(0, 0)
    villager.set_position(2, 1)

    destination = guard.regroup_with_allies([villager])

    assert destination is None
    assert guard.destination is None    
    
def test_npc_can_follow_group_leader():
    brain = make_brain()

    guard = NPC("Guard", brain)
    leader = NPC("Captain", brain)

    guard.set_group("guards")
    leader.set_group("guards")
    leader.set_rank("leader")

    guard.set_position(0, 0)
    leader.set_position(3, 0)

    destination = guard.follow_group_leader([leader])

    assert destination == (3, 0)
    assert guard.destination == (3, 0)
    
def test_npc_follow_group_leader_returns_none_without_leader():
    brain = make_brain()

    guard = NPC("Guard", brain)
    ally = NPC("Scout", brain)

    guard.set_group("guards")
    ally.set_group("guards")

    guard.set_position(0, 0)
    ally.set_position(3, 0)

    destination = guard.follow_group_leader([ally])

    assert destination is None
    assert guard.destination is None    
def test_npc_can_share_destination_with_allies():
    brain = make_brain()

    leader = NPC("Captain", brain)
    ally1 = NPC("Guard", brain)
    ally2 = NPC("Scout", brain)

    leader.set_group("guards")
    ally1.set_group("guards")
    ally2.set_group("guards")

    leader.set_destination(4, 4)

    updated = leader.share_destination_with_allies([ally1, ally2])

    assert updated == 2
    assert ally1.destination == (4, 4)
    assert ally2.destination == (4, 4)
    
def test_npc_does_not_share_destination_without_group():
    brain = make_brain()

    npc = NPC("Wanderer", brain)
    other = NPC("Guard", brain)

    npc.set_destination(4, 4)

    updated = npc.share_destination_with_allies([other])

    assert updated == 0
    assert other.destination is None
    
def test_npc_can_receive_shared_destination():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.receive_shared_destination((3, 2))

    assert npc.destination == (3, 2)

def test_npc_can_share_event_with_allies():
    brain = make_brain()

    leader = NPC("Captain", brain)
    ally1 = NPC("Guard", brain)
    ally2 = NPC("Scout", brain)

    leader.set_group("guards")
    ally1.set_group("guards")
    ally2.set_group("guards")

    updated = leader.share_event_with_allies(
        [ally1, ally2],
        event_type="danger",
        detail="enemy nearby",
    )

    assert updated == 2
    assert ally1.has_memory_event("danger") is True
    assert ally2.has_memory_event("danger") is True
    
def test_npc_does_not_share_event_without_group():
    brain = make_brain()

    npc = NPC("Wanderer", brain)
    other = NPC("Guard", brain)

    updated = npc.share_event_with_allies(
        [other],
        event_type="danger",
        detail="enemy nearby",
    )

    assert updated == 0
    assert other.has_memory_event("danger") is False    
    
def test_npc_can_detect_memory_event():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.remember_event("danger", source="Scout")

    assert npc.has_memory_event("danger") is True
    assert npc.has_memory_event("help") is False
    
def test_npc_can_share_goal_with_allies():
    brain = make_brain()

    leader = NPC("Captain", brain)
    ally1 = NPC("Guard", brain)
    ally2 = NPC("Scout", brain)

    leader.set_group("guards")
    ally1.set_group("guards")
    ally2.set_group("guards")

    leader.set_goal("survive")

    updated = leader.share_goal_with_allies([ally1, ally2])

    assert updated == 2
    assert ally1.goal == "survive"
    assert ally2.goal == "survive"
    
def test_npc_can_share_priorities_with_allies():
    brain = make_brain()

    leader = NPC("Captain", brain)
    ally = NPC("Guard", brain)

    leader.set_group("guards")
    ally.set_group("guards")

    leader.set_priorities({"run": 3.0, "wait": 1.0})

    updated = leader.share_priorities_with_allies([ally])

    assert updated == 1
    assert ally.priorities == {"run": 3.0, "wait": 1.0}
    
def test_npc_does_not_share_goal_without_group():
    brain = make_brain()

    npc = NPC("Wanderer", brain)
    other = NPC("Guard", brain)

    npc.set_goal("survive")

    updated = npc.share_goal_with_allies([other])

    assert updated == 0
    assert other.goal is None
    
def test_npc_does_not_share_priorities_without_data():
    brain = make_brain()

    npc = NPC("Wanderer", brain)
    other = NPC("Guard", brain)

    npc.set_group("guards")
    other.set_group("guards")

    updated = npc.share_priorities_with_allies([other])

    assert updated == 0
    assert other.priorities == {}
    
def test_npc_can_have_role():
    brain = make_brain()
    npc = NPC("Guard", brain)

    npc.set_role("guard")

    assert npc.get_role() == "guard"
    
def test_guard_prefers_follow_when_leader_present():
    brain = Brain()

    def rule(npc, context):
        nearby = context.get("nearby", [])

        if npc.get_role() == "guard":
            if any(o.rank == "leader" for o in nearby):
                return {"follow": 1.0}

        return {"wait": 1.0}

    brain.add_rule("group", rule)

    leader = NPC("Captain", brain)
    leader.set_rank("leader")

    guard = NPC("Guard", brain)
    guard.set_role("guard")
    guard.set_state("group")

    guard.update_context(nearby=[leader])

    result = guard.act()

    assert result == "follow"
    
def test_scout_prefers_exploration():
    brain = Brain()

    def rule(npc, context):
        if npc.get_role() == "scout":
            return {"explore": 1.0}

        return {"wait": 1.0}

    brain.add_rule("idle", rule)

    scout = NPC("Scout", brain)
    scout.set_role("scout")
    scout.set_state("idle")

    result = scout.act()

    assert result == "explore"
    
def test_npc_can_issue_order_to_allies():
    brain = make_brain()

    leader = NPC("Captain", brain)
    ally = NPC("Guard", brain)

    leader.set_group("guards")
    ally.set_group("guards")

    updated = leader.issue_order_to_allies([ally], order_type="follow_me")

    assert updated == 1
    assert ally.has_memory_event("order") is True
    
def test_npc_can_read_latest_order():
    brain = make_brain()

    npc = NPC("Guard", brain)
    npc.remember_event("order", source="Captain", detail="follow_me")

    assert npc.get_latest_order() == "follow_me"
    
def test_npc_does_not_issue_order_without_group():
    brain = make_brain()

    leader = NPC("Captain", brain)
    ally = NPC("Guard", brain)

    updated = leader.issue_order_to_allies([ally], order_type="retreat")

    assert updated == 0
    assert ally.has_memory_event("order") is False