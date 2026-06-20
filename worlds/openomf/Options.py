from dataclasses import dataclass
from Options import Choice, Range, Toggle, PerGameCommonOptions


class GoalTournament(Choice):
    """Which tournament must be won to complete the seed."""
    display_name = "Goal Tournament"
    option_north_american_open  = 0
    option_katushai_challenge   = 1
    option_war_invitational     = 2
    option_world_championship   = 3
    option_all_tournaments      = 4
    default = 3


class StartingHAR(Choice):
    """Which HAR the player begins with. Random picks one of the 11 at generation time."""
    display_name = "Starting HAR"
    option_jaguar   = 0
    option_shadow   = 1
    option_thorn    = 2
    option_pyros    = 3
    option_electra  = 4
    option_katana   = 5
    option_shredder = 6
    option_flail    = 7
    option_gargoyle = 8
    option_chronos  = 9
    option_nova            = 10
    option_random_selection = 11
    default = 11


class HARStatMax(Range):
    """Maximum upgrade level for each HAR stat. Vanilla = 9."""
    display_name = "HAR Stat Max"
    range_start = 4
    range_end   = 20
    default     = 9


class PilotStatMax(Range):
    """Maximum upgrade level for each pilot stat. Vanilla = 25."""
    display_name = "Pilot Stat Max"
    range_start = 1
    range_end   = 50
    default     = 25


class AvailableHARs(Range):
    """How many of the 11 HARs are included in the multiworld. Chosen randomly at generation,
    always including the starting HAR. 11 = all HARs (default). Minimum 1."""
    display_name = "Available HARs"
    range_start = 1
    range_end   = 11
    default     = 11


class BuyCostFactor(Range):
    """cost multiplier of vanilla Mechlab prices (divide by 100 for precentage). 
    100 = vanilla prices. 200 = 2x prices Range 1–1000 (0.01×–10×)."""
    display_name = "Buy Cost Factor"
    range_start = 1
    range_end   = 1000
    default     = 10


class MoneySmallValue(Range):
    """Base credit value for a Money (Small) item. The game further multiplies this
    by a per-tournament prize modifier (1×/2×/3×/6× for NAO/Katushai/WAR/World)."""
    display_name = "Money (Small) Value"
    range_start = 100
    range_end   = 50000
    default     = 3000


class MoneyLargeValue(Range):
    """Base credit value for a Money (Large) item. The game further multiplies this
    by a per-tournament prize modifier (1×/2×/3×/6× for NAO/Katushai/WAR/World)."""
    display_name = "Money (Large) Value"
    range_start = 500
    range_end   = 100000
    default     = 15000


class ShopHints(Toggle):
    """When enabled, focusing a shop upgrade button broadcasts a hint to the AP server
    so all players can see what item is at that location. When disabled, the item name
    is still shown in-game but no hint is sent to the server."""
    display_name = "Shop Hints"
    default = 0


class Difficulty(Choice):
    """AI difficulty for tournament opponents. Matches the four OMF difficulty tiers."""
    display_name = "Difficulty"
    option_aluminium = 0
    option_iron      = 1
    option_steel     = 2
    option_heavy     = 3
    default = 1


@dataclass
class OMFOptions(PerGameCommonOptions):
    goal_tournament:       GoalTournament
    starting_har:          StartingHAR
    available_hars:        AvailableHARs
    har_stat_max:          HARStatMax
    pilot_stat_max:        PilotStatMax
    buy_cost_factor:       BuyCostFactor
    money_small_value:     MoneySmallValue
    money_large_value:     MoneyLargeValue
    shop_hints:            ShopHints
    difficulty:            Difficulty
