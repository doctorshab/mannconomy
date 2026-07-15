# Relative weights for soft-scored attributes used by score_comp().
# These do NOT gate the candidate pool (see hard filters: item_id, quality_id,
# is_australium, is_craftable) — they only affect ranking within it.
#
# Weights sum to 100 so a comp's total score can be read as "% attribute match"
# against the requested item. Relative ordering matters more than exact values:
# unusual_effect / paint / war_paint / botkiller_tier are the biggest price
# drivers in practice, spells / strange_parts / collection move price the least.
#
# Note: sheen_id only applies when killstreak_tier_id is Specialized+, and
# killstreaker_id only when it's Professional. Both sides will naturally be
# null (and therefore "match") on comps where killstreak_tier_id is None.

WEIGHTS = {
    "unusual_effect_id": 16,#
    "paint_id": 16,#
    "war_paint_id": 12,#
    "botkiller_tier_id": 12,
    "wear_float": 10, #
    "pattern_seed": 4,
    "killstreak_tier_id": 6,#
    "sheen_id": 5,
    "killstreaker_id": 5,
    "grade_id": 5,
    "is_festivized": 3,
    "holiday_restriction_id": 3,
    "collection_id": 1,
    "spells": 1,#
    "strange_parts": 1,#
}