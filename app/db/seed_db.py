"""
Mock data seeder for local dev/testing.

Populates every table in the schema: all 13 lookup tables, a handful of
`items`, a spread of `price_comps` against them (varied quality/craftable/
australium/killstreak/wear/unusual/paint/war-paint/botkiller/festivized
combinations, at different ages), and their spell/strange-part junctions.

Idempotent: safe to re-run. Lookups are matched by name (or by explicit id
for `qualities`, which must match Valve's real quality enum - see note
below). price_comps are matched by external_id so re-running never creates
duplicates.

Usage (from the project root, with your venv active and .env configured):
    python -m app.db.seed_db
"""
from datetime import datetime, timezone, timedelta

from app.db.session import SessionLocal
from app.db.models import (
    Quality, KillstreakTier, Sheen, Killstreaker, UnusualEffect, Grade,
    Paint, Collection, BotkillerTier, HolidayRestriction, WarPaint,
    Spell, StrangePart, Item, PriceComp,
)

# ======================================================================
# 1. LOOKUP TABLE DATA
# ======================================================================

# Valve's actual TF2 quality enum (confirmed against the official schema -
# https://wiki.teamfortress.com/wiki/WebAPI/GetSchema). These IDs are
# load-bearing: app/main.py's ValuationRequest defaults quality_id=6
# ("Unique") and its docstring assumes 11=Strange, 5=Unusual. Do NOT let
# these be auto-increment - they must be inserted with explicit ids.
QUALITIES = [
    (0, "Normal"), (1, "Genuine"), (3, "Vintage"), (5, "Unusual"),
    (6, "Unique"), (7, "Community"), (8, "Valve"), (9, "Self-Made"),
    (11, "Strange"), (13, "Haunted"), (14, "Collector's"),
    (15, "Decorated Weapon"),
]

# Order matters here only insofar as rag_pipeline_test.py's existing mock
# data assumes 1=Killstreak, 2=Specialized, 3=Professional - keep this order.
KILLSTREAK_TIERS = ["Killstreak", "Specialized Killstreak", "Professional Killstreak"]

SHEENS = [
    "Team Shine", "Deadly Daffodil", "Manndarin", "Mean Green",
    "Agonizing Emerald", "Villainous Violet", "Hot Rod",
]

KILLSTREAKERS = [
    "Fire Horns", "Cerebral Discharge", "Tornado", "Flames",
    "Singularity", "Incinerator", "Hypno-Beam",
]

# Representative subset of real Unusual effects - TF2 has 100+, this is
# nowhere near exhaustive. Fine for pipeline testing; expand later if you
# need broader Unusual coverage.
UNUSUAL_EFFECTS = [
    "Burning Flames", "Scorching Flames", "Cloud 9", "Sunbeams",
    "Circling Peace Sign", "Massed Flies", "Tesla Coil", "Green Confetti",
    "Purple Confetti", "Haunted Ghosts", "Green Energy", "Purple Energy",
    "Circling TF Logo", "Vivid Plasma", "Stormy Storm", "Nuts n' Bolts",
]

# Real Collector's item grades, in ascending rarity order.
GRADES = ["Civilian", "Freelance", "Mercenary", "Commando", "Assassin", "Elite"]

PAINTS = [
    "A Color Similar to Slate", "A Deep Commitment to Purple", "A Distinctive Lack of Hue",
    "A Mann's Mint", "After Eight", "Aged Moustache Grey", "An Air of Debonair",
    "An Extraordinary Abundance of Tinge", "Australium Gold", "Balaclavas Are Forever",
    "Color No. 216-190-216", "Cream Spirit", "Dark Salmon Injustice", "Indubitably Green",
    "Mann Co. Orange", "Mocha Drop", "Muskelmannbraun", "Noble Hatter's Violet",
    "Operator's Overalls", "Peculiarly Drab Tincture", "Pink as Hell", "Radigan Conagher Brown",
    "Team Spirit", "The Bitter Taste of Defeat and Lime", "The Color of a Gentlemann's Business Pant",
    "The Value of Teamwork", "Waterlogged Lab Coat", "Ye Olde Rustic Colour", "Zepheniah's Greed",
]

COLLECTIONS = [
    "The Concealed Killer Collection", "The Craftsman Collection", "The Teufort Collection",
    "The Pyroland Collection", "The Warbird Collection", "The Gentlemann's Collection",
    "The Harvest Collection", "The Macabre Web Collection", "The Gargoyle Collection",
    "The Mayflower Collection", "The Jungle Jackpot Collection", "The Infernal Reward Collection",
    "The Decorated Tanker Collection", "The Contract Campaigner Collection", "The Saxton Select Collection",
    "The Scream Fortress IX Collection", "The Jungle Inferno Collection", "The Winter 2017 Collection",
    "The Scream Fortress X Collection", "The Winter 2019 Collection", "The Scream Fortress XII Collection",
    "The Winter 2020 Collection",
]

# All six real Botkiller tiers (confirmed - wiki.teamfortress.com/wiki/Botkiller_weapons).
BOTKILLER_TIERS = ["Silver", "Gold", "Rust", "Blood", "Carbonado", "Diamond"]

# The 4 real holiday restrictions used in the schema.
HOLIDAY_RESTRICTIONS = ["Halloween", "Christmas", "Full Moon", "Birthday"]

WAR_PAINTS = [
    "Macabre Web", "Nutcracker", "Autumn", "Bovine Blazemaker", "Night Owl", "Civic Duty",
    "Miami Element", "Jazzy", "Hazard Warning", "Coffin Nail", "High Roller's", "Warhawk",
    "Blitzkrieg", "Corsair", "Airwolf", "Bomber Soul", "Uranium", "Roar", "Backwoods Boomstick",
    "Iron Wood", "Plaid Potshotter", "Shot in the Dark", "Alien Tech", "Dragon Slayer",
    "Park Pigmented", "Sax Wax", "Yeti Coated", "Crocodile Munitions", "Macaw Masked",
    "Piñata", "Star Crossed", "Clover Camo'd", "Kill Covered", "Fire Glazed", "Blood Swept",
    "Night Terror", "Woodsy Widowmaker", "Woodland Warrior", "Wrapped Reviver", "Forest Fire",
]

SPELLS = [
    "Halloween Fire", "Pumpkin Bombs", "Exorcism", "Voices From Below",
    "Team Spirit Footprints", "Gangreen Footprints", "Corpse Gray Footprints",
    "Violent Violet Footprints", "Rotten Orange Footprints", "Bruised Purple Footprints",
    "Headless Horseshoes",
]

STRANGE_PARTS = [
    "Kills", "Damage Dealt", "Kills While Explosive-Jumping", "Full Health Kills",
    "Point Blank Kills", "Long-Distance Kills", "Kills While Low Health",
    "Robots Destroyed", "Giant Robots Destroyed", "Tanks Destroyed",
    "Sappers Destroyed", "Buildings Destroyed", "Critical Kills",
    "Domination Kills", "Revenges", "Posthumous Kills", "Teammates Extinguished",
    "Assists", "Sentries Destroyed", "Cloaked Spies Killed",
]


# ======================================================================
# 2. HELPERS (idempotent get-or-create)
# ======================================================================

def _get_or_create_quality(session, qid, name):
    obj = session.get(Quality, qid)
    if obj:
        return obj
    obj = Quality(id=qid, name=name)
    session.add(obj)
    session.flush()
    return obj


def _get_or_create_by_name(session, model, name):
    obj = session.query(model).filter_by(name=name).first()
    if obj:
        return obj
    obj = model(name=name)
    session.add(obj)
    session.flush()
    return obj


def _get_or_create_item(session, defindex, base_name, item_class):
    obj = session.query(Item).filter_by(defindex=defindex).first()
    if obj:
        return obj
    obj = Item(defindex=defindex, base_name=base_name, item_class=item_class)
    session.add(obj)
    session.flush()
    return obj


def _get_or_create_comp(session, external_id, **kwargs):
    """Returns (comp, created_bool) so callers know whether to attach
    many-to-many relationships (only needed the first time)."""
    existing = session.query(PriceComp).filter_by(external_id=external_id).first()
    if existing:
        return existing, False
    comp = PriceComp(external_id=external_id, **kwargs)
    session.add(comp)
    session.flush()
    return comp, True


def _days_ago_ts(now, n_days):
    return int((now - timedelta(days=n_days)).timestamp())


# ======================================================================
# 3. SEED LOOKUP TABLES
# ======================================================================

def seed_lookups(session):
    lookups = {
        "qualities": {name: _get_or_create_quality(session, qid, name) for qid, name in QUALITIES},
        "killstreak_tiers": {n: _get_or_create_by_name(session, KillstreakTier, n) for n in KILLSTREAK_TIERS},
        "sheens": {n: _get_or_create_by_name(session, Sheen, n) for n in SHEENS},
        "killstreakers": {n: _get_or_create_by_name(session, Killstreaker, n) for n in KILLSTREAKERS},
        "unusual_effects": {n: _get_or_create_by_name(session, UnusualEffect, n) for n in UNUSUAL_EFFECTS},
        "grades": {n: _get_or_create_by_name(session, Grade, n) for n in GRADES},
        "paints": {n: _get_or_create_by_name(session, Paint, n) for n in PAINTS},
        "collections": {n: _get_or_create_by_name(session, Collection, n) for n in COLLECTIONS},
        "botkiller_tiers": {n: _get_or_create_by_name(session, BotkillerTier, n) for n in BOTKILLER_TIERS},
        "holiday_restrictions": {n: _get_or_create_by_name(session, HolidayRestriction, n) for n in HOLIDAY_RESTRICTIONS},
        "war_paints": {n: _get_or_create_by_name(session, WarPaint, n) for n in WAR_PAINTS},
        "spells": {n: _get_or_create_by_name(session, Spell, n) for n in SPELLS},
        "strange_parts": {n: _get_or_create_by_name(session, StrangePart, n) for n in STRANGE_PARTS},
    }
    session.commit()
    return lookups


# ======================================================================
# 4. SEED ITEMS + PRICE_COMPS
# ======================================================================

def seed_items_and_comps(session, lu):
    now = datetime.now(timezone.utc)
    q = lu["qualities"]
    kt = lu["killstreak_tiers"]
    sheen = lu["sheens"]
    killstreaker = lu["killstreakers"]
    effect = lu["unusual_effects"]
    grade = lu["grades"]
    war_paint = lu["war_paints"]
    botkiller = lu["botkiller_tiers"]
    spell = lu["spells"]
    part = lu["strange_parts"]

    # --- Items ---
    # defindex 18 and 13 are confirmed real TF2 item defindexes.
    rocket_launcher = _get_or_create_item(session, 18, "Rocket Launcher", "weapon")
    scattergun = _get_or_create_item(session, 13, "Scattergun", "weapon")

    # NOTE: the three defindexes below are ILLUSTRATIVE PLACEHOLDERS, not
    # verified against the real TF2 schema. They exist so the mock data can
    # exercise unusual/war-paint/botkiller scoring dimensions end-to-end.
    # Replace with real defindexes (e.g. from backpack.tf's schema dump)
    # before this data means anything beyond "does the pipeline run".
    team_captain = _get_or_create_item(session, 90378, "Team Captain", "cosmetic")
    civic_duty_rl = _get_or_create_item(session, 90101, "Civic Duty Rocket Launcher", "weapon")
    botkiller_minigun = _get_or_create_item(session, 90448, "Silver Botkiller Minigun Mk.I", "weapon")

    # --- PriceComps ---
    # All prices/ages below are fabricated for pipeline testing, not real
    # market data - don't read anything into the actual ref/key numbers.
    comps = [
        # Rocket Launcher / Unique / craftable bucket (4 comps -> exercises
        # the full compute_confidence() path, not the comp_count<=2 shortcut)
        dict(external_id="mock_rl_001", item_id=rocket_launcher.id, quality_id=q["Unique"].id,
             is_craftable=True, is_australium=False,
             price_keys=2.0, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 1),
             listing_type="sell", source="backpack.tf"),
        dict(external_id="mock_rl_002", item_id=rocket_launcher.id, quality_id=q["Unique"].id,
             is_craftable=True, is_australium=False,
             killstreak_tier_id=kt["Specialized Killstreak"].id, sheen_id=sheen["Team Shine"].id,
             wear_float=0.15,
             price_keys=3.0, price_metal=10.0, transaction_timestamp=_days_ago_ts(now, 10),
             listing_type="sell", source="backpack.tf"),
        dict(external_id="mock_rl_003", item_id=rocket_launcher.id, quality_id=q["Unique"].id,
             is_craftable=True, is_australium=False,
             killstreak_tier_id=kt["Professional Killstreak"].id, sheen_id=sheen["Hot Rod"].id,
             killstreaker_id=killstreaker["Tornado"].id,
             price_keys=5.0, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 20),
             listing_type="sell", source="backpack.tf"),
        dict(external_id="mock_rl_004", item_id=rocket_launcher.id, quality_id=q["Unique"].id,
             is_craftable=True, is_australium=False, is_festivized=True,
             price_keys=2.5, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 6),
             listing_type="sell", source="backpack.tf"),

        # Rocket Launcher / Strange / craftable (separate hard-filter bucket, 1 comp
        # -> exercises the comp_count<=2 "Low confidence" shortcut). Has strange_parts.
        dict(external_id="mock_rl_005", item_id=rocket_launcher.id, quality_id=q["Strange"].id,
             is_craftable=True, is_australium=False,
             price_keys=1.5, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 5),
             listing_type="sell", source="backpack.tf",
             _spells=[], _strange_parts=["Kills", "Damage Dealt"]),

        # Rocket Launcher / Unique / NOT craftable (separate bucket, tests is_craftable hard filter)
        dict(external_id="mock_rl_006", item_id=rocket_launcher.id, quality_id=q["Unique"].id,
             is_craftable=False, is_australium=False,
             price_keys=1.0, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 45),
             listing_type="sell", source="backpack.tf"),

        # Australium Rocket Launcher - SAME item_id as base Rocket Launcher,
        # differentiated only by is_australium (per the design principle that
        # Australiums don't get a separate item row). Strange quality, typical
        # for Australiums earned via MvM.
        dict(external_id="mock_rl_007", item_id=rocket_launcher.id, quality_id=q["Strange"].id,
             is_craftable=True, is_australium=True,
             price_keys=30.0, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 3),
             listing_type="sell", source="backpack.tf"),

        # Scattergun / Unique / craftable, with spells attached
        dict(external_id="mock_sg_001", item_id=scattergun.id, quality_id=q["Unique"].id,
             is_craftable=True, is_australium=False,
             price_keys=0.0, price_metal=4.0, transaction_timestamp=_days_ago_ts(now, 3),
             listing_type="sell", source="backpack.tf",
             _spells=["Halloween Fire", "Pumpkin Bombs"], _strange_parts=[]),
        dict(external_id="mock_sg_002", item_id=scattergun.id, quality_id=q["Unique"].id,
             is_craftable=True, is_australium=False,
             price_keys=0.0, price_metal=3.0, transaction_timestamp=_days_ago_ts(now, 60),
             listing_type="sell", source="backpack.tf"),

        # Team Captain / Unusual, 3 comps -> tests unusual_effect_id scoring
        dict(external_id="mock_tc_001", item_id=team_captain.id, quality_id=q["Unusual"].id,
             is_craftable=True, is_australium=False,
             unusual_effect_id=effect["Burning Flames"].id,
             price_keys=400.0, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 1),
             listing_type="sell", source="backpack.tf"),
        dict(external_id="mock_tc_002", item_id=team_captain.id, quality_id=q["Unusual"].id,
             is_craftable=True, is_australium=False,
             unusual_effect_id=effect["Scorching Flames"].id,
             price_keys=380.0, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 15),
             listing_type="sell", source="backpack.tf"),
        dict(external_id="mock_tc_003", item_id=team_captain.id, quality_id=q["Unusual"].id,
             is_craftable=True, is_australium=False,
             unusual_effect_id=effect["Burning Flames"].id,
             price_keys=410.0, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 40),
             listing_type="sell", source="backpack.tf"),

        # Civic Duty Rocket Launcher / Decorated Weapon, tests war_paint_id + wear_float + pattern_seed + grade_id
        dict(external_id="mock_cd_001", item_id=civic_duty_rl.id, quality_id=q["Decorated Weapon"].id,
             is_craftable=True, is_australium=False,
             war_paint_id=war_paint["Civic Duty"].id, wear_float=0.02, pattern_seed=123456,
             grade_id=grade["Mercenary"].id,
             price_keys=20.0, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 2),
             listing_type="sell", source="backpack.tf"),
        dict(external_id="mock_cd_002", item_id=civic_duty_rl.id, quality_id=q["Decorated Weapon"].id,
             is_craftable=True, is_australium=False,
             war_paint_id=war_paint["Civic Duty"].id, wear_float=0.35, pattern_seed=654321,
             grade_id=grade["Mercenary"].id,
             price_keys=12.0, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 8),
             listing_type="sell", source="backpack.tf"),

        # Silver/Gold Botkiller Minigun / Strange (Botkillers are always Strange quality),
        # tests botkiller_tier_id scoring
        dict(external_id="mock_bk_001", item_id=botkiller_minigun.id, quality_id=q["Strange"].id,
             is_craftable=True, is_australium=False,
             botkiller_tier_id=botkiller["Silver"].id,
             price_keys=3.0, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 5),
             listing_type="sell", source="backpack.tf"),
        dict(external_id="mock_bk_002", item_id=botkiller_minigun.id, quality_id=q["Strange"].id,
             is_craftable=True, is_australium=False,
             botkiller_tier_id=botkiller["Gold"].id,
             price_keys=6.0, price_metal=0.0, transaction_timestamp=_days_ago_ts(now, 12),
             listing_type="sell", source="backpack.tf"),
    ]

    created_count = 0
    for spec in comps:
        spell_names = spec.pop("_spells", [])
        part_names = spec.pop("_strange_parts", [])
        comp, created = _get_or_create_comp(session, spec.pop("external_id"), **spec)
        if created:
            created_count += 1
            for name in spell_names:
                comp.spells.append(spell[name])
            for name in part_names:
                comp.strange_parts.append(part[name])

    session.commit()
    return created_count


# ======================================================================
# 5. MAIN
# ======================================================================

def main():
    session = SessionLocal()
    try:
        lookups = seed_lookups(session)
        lookup_counts = {name: len(d) for name, d in lookups.items()}
        created_comps = seed_items_and_comps(session, lookups)

        print("Seeded lookup tables (existing rows kept, new rows added):")
        for name, count in lookup_counts.items():
            print(f"  {name}: {count} rows available")
        print(f"price_comps: {created_comps} new rows created this run")
        print("\nDone. Re-run any time - this script is idempotent.")
    finally:
        session.close()


if __name__ == "__main__":
    main()