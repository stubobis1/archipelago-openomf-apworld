if False:
    from . import OMFWorld  # type hint only


def set_rules(world: "OMFWorld") -> None:
    player   = world.player
    goal_idx = world.options.goal_tournament.value
    goal_all = goal_idx == 4

    # HAR buy location access rules are set by the connection rules in Regions.py.
    # Tournament region access is gated by Progressive Tournament Access count in Regions.py.
    # No additional per-location rules needed here.

    if goal_all:
        from .data.tournaments import TOURNAMENTS
        world.multiworld.completion_condition[player] = lambda state: all(
            state.can_reach(f"Win {t['name']} (1)", "Location", player)
            for t in TOURNAMENTS
        )
    else:
        world.multiworld.completion_condition[player] = lambda state: state.has("Victory", player)
