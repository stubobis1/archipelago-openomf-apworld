from BaseClasses import Region, ItemClassification
from .data.tournaments import TOURNAMENTS, HAR_NAMES, HAR_STAT_NAMES, PILOT_STAT_NAMES
from .Items import OMFItem
from .Locations import (
    OMFLocation, match_location_id, tournament_win_id,
    har_buy_location_id, pilot_buy_location_id,
)

if False:
    from . import OMFWorld  # type hint only

# NAO is always accessible; each Progressive Tournament Access unlocks the next tournament
# in registration-fee order: Katushai (1), WAR (2), World Championship (3).
_TRN_ACCESS_REQUIRED = [0, 1, 2, 3]  # how many Progressive Tournament Access items each tournament needs


# (tier_start_lvl, next_tier_start_or_None, trn_req, region_label)
_HAR_STAT_TIERS   = [(1, 3, 0, ""), (3, 5, 1, " Lv3"), (5, 8, 2, " Lv5"), (8, None, 3, " Lv8")]
_PILOT_STAT_TIERS = [(1, 7, 0, ""), (7, 13, 1, " Lv7"), (13, 19, 2, " Lv13"), (19, None, 3, " Lv19")]


def create_regions(world: "OMFWorld") -> None:
    player         = world.player
    mw             = world.multiworld
    har_stat_max   = world.options.har_stat_max.value
    pilot_stat_max = world.options.pilot_stat_max.value
    include_buy    = bool(world.options.include_buy_locations.value)
    goal_idx       = world.options.goal_tournament.value

    menu = Region("Menu", player, mw)
    mw.regions.append(menu)

    # Tournament regions — gated by Progressive Tournament Access count.
    match_idx = 0
    for ti, t in enumerate(TOURNAMENTS):
        region = Region(t["name"], player, mw)

        for pilot_name, _, restricted in t["pilots"]:
            if not restricted:
                loc = OMFLocation(player, f"{t['name']} - Beat {pilot_name}",
                                  match_location_id(match_idx), region)
                region.locations.append(loc)
            match_idx += 1

        for ri in range(3):
            win_loc = OMFLocation(player, f"Win {t['name']} ({ri + 1})",
                                  tournament_win_id(ti, ri), region)
            region.locations.append(win_loc)

        mw.regions.append(region)
        required = _TRN_ACCESS_REQUIRED[ti]
        if required == 0:
            menu.connect(region)
        else:
            menu.connect(
                region,
                rule=lambda state, req=required: state.count("Progressive Tournament Access", player) >= req,
            )

    # HAR buy regions — tiered sub-regions per HAR gated by HAR unlock + TRN count.
    # Base region ({har} Mechlab) holds lv1-2; sub-regions branch off it for higher tiers.
    if include_buy:
        for hi, har in enumerate(HAR_NAMES):
            base_region = None
            for (t_start, t_next, trn_req, label) in _HAR_STAT_TIERS:
                lvl_end = (t_next - 1) if t_next is not None else har_stat_max
                lvl_end = min(lvl_end, har_stat_max)
                if t_start > har_stat_max:
                    break
                region = Region(f"{har} Mechlab{label}", player, mw)
                for si, stat in enumerate(HAR_STAT_NAMES):
                    for lvl in range(t_start, lvl_end + 1):
                        loc = OMFLocation(
                            player, f"Buy {har} {stat} Upgrade {lvl}",
                            har_buy_location_id(hi, si, lvl), region,
                        )
                        region.locations.append(loc)
                mw.regions.append(region)
                if trn_req == 0:
                    # Base tier: gate on HAR unlock from Menu
                    menu.connect(region, rule=lambda state, h=har: state.has(f"{h} Unlock", player))
                    base_region = region
                else:
                    # Higher tiers: branch from base with TRN count rule
                    base_region.connect(
                        region,
                        rule=lambda state, r=trn_req: state.count("Progressive Tournament Access", player) >= r,
                    )

        # Pilot training — tiered sub-regions gated only by TRN count.
        pilot_base = None
        for (t_start, t_next, trn_req, label) in _PILOT_STAT_TIERS:
            lvl_end = (t_next - 1) if t_next is not None else pilot_stat_max
            lvl_end = min(lvl_end, pilot_stat_max)
            if t_start > pilot_stat_max:
                break
            region = Region(f"Pilot Training{label}", player, mw)
            for pi, stat in enumerate(PILOT_STAT_NAMES):
                for lvl in range(t_start, lvl_end + 1):
                    loc = OMFLocation(
                        player, f"Train {stat} Level {lvl}",
                        pilot_buy_location_id(pi, lvl), region,
                    )
                    region.locations.append(loc)
            mw.regions.append(region)
            if trn_req == 0:
                menu.connect(region)
                pilot_base = region
            else:
                pilot_base.connect(
                    region,
                    rule=lambda state, r=trn_req: state.count("Progressive Tournament Access", player) >= r,
                )

    # Victory event — separate event location (address=None) in the goal region.
    goal_all = goal_idx == 4
    if goal_all:
        goal_region_name = TOURNAMENTS[-1]["name"]
    else:
        goal_region_name = TOURNAMENTS[goal_idx]["name"]

    goal_region = mw.get_region(goal_region_name, player)
    victory_loc = OMFLocation(player, "Victory", None, goal_region)  # type: ignore[arg-type]
    victory_item = OMFItem("Victory", ItemClassification.progression, None, player)  # type: ignore[arg-type]
    victory_loc.place_locked_item(victory_item)
    goal_region.locations.append(victory_loc)
