from typing import Any, Mapping

from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld, World
from Utils import visualize_regions

from .data.tournaments import TOURNAMENTS, HAR_NAMES, HAR_STAT_NAMES, PILOT_STAT_NAMES, HAR_ENHANCEMENT_COUNTS
from .Items import (
    OMFItem, ITEM_NAME_TO_ID, ITEM_GROUPS,
    create_item, get_filler_item_name,
    har_unlock_id,
)
from .Locations import LOCATION_NAME_TO_ID, LOCATION_GROUPS
from .Options import OMFOptions
from . import Regions, Rules


class OMFWebWorld(WebWorld):
    theme = "dirt"
    tutorials = [Tutorial(
        tutorial_name="Setup Guide",
        description="A guide to setting up One Must Fall: 2097 for Archipelago.",
        language="English",
        file_name="setup_en.md",
        link="setup_en/en",
        authors=["stubob"],
    )]
    bug_report_page = "https://github.com/stubobis1/archipelago-openomf/issues"


class OMFWorld(World):
    """One Must Fall: 2097 — a classic robot fighting tournament game.
    Enter the arena, unlock HARs, and upgrade your robot through Archipelago item randomization."""

    game = "One Must Fall: 2097"
    web  = OMFWebWorld()

    options_dataclass = OMFOptions
    options: OMFOptions

    item_name_to_id     = ITEM_NAME_TO_ID
    location_name_to_id = LOCATION_NAME_TO_ID
    item_name_groups    = ITEM_GROUPS
    location_name_groups = LOCATION_GROUPS

    _starting_har_idx: int        # set in generate_early
    _available_har_indices: list  # set in generate_early; sorted indices into HAR_NAMES

    def generate_early(self) -> None:
        idx             = self.options.starting_har.value
        available_count = self.options.available_hars.value

        all_indices = list(range(len(HAR_NAMES)))

        if available_count >= len(HAR_NAMES):
            self._available_har_indices = all_indices
            starting = self.random.randint(0, len(HAR_NAMES) - 1) if idx == 11 else idx
        else:
            starting = self.random.randint(0, len(HAR_NAMES) - 1) if idx == 11 else idx
            others   = [i for i in all_indices if i != starting]
            self.random.shuffle(others)
            self._available_har_indices = sorted([starting] + others[: available_count - 1])

        self._starting_har_idx = starting
        # Starting HAR is handed to the player at connect — no location needed.
        # Precollect the unlock so HAR-gated buy locations are accessible from the start.
        self.multiworld.push_precollected(create_item(self, f"{HAR_NAMES[self._starting_har_idx]} Unlock"))

    def create_regions(self) -> None:
        Regions.create_regions(self)

    def set_rules(self) -> None:
        Rules.set_rules(self)

    def create_items(self) -> None:
        har_stat_max   = self.options.har_stat_max.value
        pilot_stat_max = self.options.pilot_stat_max.value
        include_buy    = True

        pool: list[OMFItem] = []

        # HAR unlocks — one per available HAR except starting (precollected in generate_early)
        for i in self._available_har_indices:
            if i != self._starting_har_idx:
                pool.append(create_item(self, f"{HAR_NAMES[i]} Unlock"))

        # 3 Progressive Tournament Access items unlock Katushai, WAR, World in order
        for _ in range(3):
            pool.append(create_item(self, "Progressive Tournament Access"))

        # 3 HAR color unlocks (primary, secondary, tertiary)
        pool.append(create_item(self, "Main Body HAR Color"))
        pool.append(create_item(self, "Secondary color for robot"))
        pool.append(create_item(self, "Third body color for robot"))

        if include_buy:
            # HAR stat progressives: one item per level per stat per available HAR
            for i in self._available_har_indices:
                har = HAR_NAMES[i]
                for stat in HAR_STAT_NAMES:
                    for _ in range(har_stat_max):
                        pool.append(create_item(self, f"Progressive {har} {stat}"))
            # Pilot stat progressives: one item per level per stat
            for stat in PILOT_STAT_NAMES:
                for _ in range(pilot_stat_max):
                    pool.append(create_item(self, f"Progressive {stat}"))
            # HAR enhancement progressives: one item per enhancement level per available HAR
            for i in self._available_har_indices:
                for _ in range(HAR_ENHANCEMENT_COUNTS[i]):
                    pool.append(create_item(self, f"Progressive {HAR_NAMES[i]} Enhancement"))

        # Filler to fill remaining locations
        total_locations = len(self.multiworld.get_unfilled_locations(self.player))
        while len(pool) < total_locations:
            pool.append(create_item(self, get_filler_item_name(self)))

        self.multiworld.itempool += pool

    def create_item(self, name: str) -> OMFItem:
        return create_item(self, name)

    def get_filler_item_name(self) -> str:
        return get_filler_item_name(self)

    # TODO: set _debug = False before committing / submitting to AP repo
    _debug = True

    def generate_output(self, output_directory: str) -> None:
        if self._debug:
            import logging, os
            puml_dir = os.environ.get("OMF_PUML_DIR", output_directory)
            logging.getLogger(__name__).info(f"[OMF] generate_output called, writing puml to {puml_dir}")
            from BaseClasses import CollectionState
            local_state = CollectionState(self.multiworld)
            for item in self.multiworld.itempool:
                if item.player == self.player:
                    local_state.collect(item, prevent_sweep=True)
            local_state.sweep_for_advancements(locations=self.multiworld.get_locations(self.player))
            puml_path = os.path.join(puml_dir, f"OMF-Player{self.player}.puml")
            visualize_regions(
                self.multiworld.get_region(self.origin_region_name, self.player),
                puml_path,
                show_entrance_names=True,
                regions_to_highlight=local_state.reachable_regions[self.player],
            )
            logging.getLogger(__name__).info(f"[OMF] puml written to {puml_path}")

    def fill_slot_data(self) -> Mapping[str, Any]:
        return {
            "goal_tournament":   self.options.goal_tournament.value,
            "starting_har":      self._starting_har_idx,
            "available_hars":    self._available_har_indices,
            "har_stat_max":      self.options.har_stat_max.value,
            "pilot_stat_max":    self.options.pilot_stat_max.value,
            "include_buy":       True,
            "buy_cost_factor":   self.options.buy_cost_factor.value,
            "money_small_value": self.options.money_small_value.value,
            "money_large_value": self.options.money_large_value.value,
            "shop_hints":        bool(self.options.shop_hints.value),
            "difficulty":        self.options.difficulty.value,
        }
