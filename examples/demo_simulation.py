from npcore.brain import Brain
from npcore.npc import NPC
from npcore.environment import Environment
from npcore.story_engine import StoryEngine


def build_brain() -> Brain:
    brain = Brain()

    def leader_rule(npc, context):
        env = context.get("environment")
        nearby = context.get("nearby", [])
        events = context.get("events", [])

        if any(event["type"] == "danger" for event in events):
            npc.set_goal("survive")
            npc.set_priorities({"run": 3.0, "follow": 2.0, "wait": 1.0})
            npc.pursue_goal_in_environment(env)
            npc.share_goal_with_allies(nearby)
            npc.share_priorities_with_allies(nearby)
            npc.share_destination_with_allies(nearby)
            npc.share_event_with_allies(nearby, event_type="danger", detail="enemy nearby")
            npc.issue_order_to_allies(nearby, order_type="retreat")
            return {"run": 1.0, "signal": 1.0}

        return {"wait": 1.0}

    def guard_rule(npc, context):
        nearby = context.get("nearby", [])
        env = context.get("environment")
        events = context.get("events", [])

        if npc.get_latest_order() == "retreat":
            npc.pursue_goal_in_environment(env)
            return {"run": 1.0, "follow": 1.0}

        if any(event["type"] == "danger" for event in events) or npc.has_memory_event("danger"):
            target = npc.follow_group_leader(nearby)
            if target is not None:
                return {"follow": 1.0, "defend": 1.0}
            return {"run": 1.0}

        return {"wait": 1.0}

    def scout_rule(npc, context):
        env = context.get("environment")
        events = context.get("events", [])

        if any(event["type"] == "danger" for event in events) or npc.has_memory_event("danger"):
            npc.pursue_goal_in_environment(env)
            return {"run": 1.0, "explore": 0.5}

        return {"explore": 1.0, "wait": 0.5}

    def villager_rule(npc, context):
        env = context.get("environment")
        events = context.get("events", [])

        if any(event["type"] == "danger" for event in events):
            npc.set_goal("survive")
            npc.pursue_goal_in_environment(env)
            return {"run": 1.0}

        return {"wait": 1.0}

    brain.add_rule("leader", leader_rule)
    brain.add_rule("guard", guard_rule)
    brain.add_rule("scout", scout_rule)
    brain.add_rule("villager", villager_rule)
    return brain


def apply_action_effects(env: Environment, results: list[tuple[str, str]]) -> None:
    npc_by_name = {npc.name: npc for npc in env.npcs}

    for actor, action in results:
        if actor == "message":
            continue

        npc = npc_by_name[actor]

        if action in {"run", "follow", "explore", "move"}:
            npc.move_smart(env)


def print_step(step_number: int, env: Environment, results: list[tuple[str, str]]) -> None:
    print(f"\n=== Tick {step_number} Decisions ===")

    actions = [(actor, action) for actor, action in results if actor != "message"]
    messages = [(actor, action) for actor, action in results if actor == "message"]

    print("Actions:")
    for actor, action in actions:
        print(f"- {actor}: {action}")

    if messages:
        print("Social messages:")
        for _, message in messages:
            print(f"- {message}")

    print()
    print(env.render_grid())


def main() -> None:
    brain = build_brain()

    env = Environment(width=8, height=6)
    env.add_zone("safe_house", [(6, 4), (6, 5), (7, 4), (7, 5)])
    env.add_zone("danger_zone", [(2, 1), (2, 2), (3, 2), (4, 2)])
    env.apply_zone_cost("danger_zone", 8)

    env.add_block(3, 1)
    env.add_block(3, 3)
    env.add_block(4, 3)

    captain = NPC("Captain", brain)
    captain.set_state("leader")
    captain.set_group("guards")
    captain.set_rank("leader")
    captain.set_role("leader")
    captain.set_position(1, 1)
    captain.set_goal("survive")
    captain.set_destination(6, 4)
    captain.set_personality_trait("loyalty", 1.0)

    guard = NPC("Guard", brain)
    guard.set_state("guard")
    guard.set_group("guards")
    guard.set_role("guard")
    guard.set_position(1, 2)
    guard.set_personality_trait("loyalty", 1.0)
    guard.set_emotion("fear", 0.4)

    scout = NPC("Scout", brain)
    scout.set_state("scout")
    scout.set_group("guards")
    scout.set_role("scout")
    scout.set_position(0, 1)
    scout.set_personality_trait("fearfulness", 0.3)

    villager = NPC("Villager", brain)
    villager.set_state("villager")
    villager.set_group("villagers")
    villager.set_role("civilian")
    villager.set_goal("survive")
    villager.set_position(5, 1)

    env.add_npc(captain)
    env.add_npc(guard)
    env.add_npc(scout)
    env.add_npc(villager)

    print("=== Initial World ===")
    print(env.render_grid())
    print()
    print("=== Event Triggered: danger ===")
    env.trigger_event("danger")

    history: list[list[tuple[str, str]]] = []
    for tick in range(1, 6):
        for npc in env.npcs:
            npc.update_context(
                environment=env,
                events=list(env.events),
                nearby=env.get_nearby(npc, radius=3),
            )

        results = env.step()
        apply_action_effects(env, results)
        history.append(results)
        print_step(tick, env, results)

    print("\n=== Final Positions ===")
    for npc in env.npcs:
        print(f"- {npc.name}: position={npc.position}, destination={npc.destination}")

    print("\n=== Summary ===")
    print(env.summary())

    print("\n=== Narrative ===")
    story = StoryEngine().generate(history)
    for line in story:
        print(line)


if __name__ == "__main__":
    main()