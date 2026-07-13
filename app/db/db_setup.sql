-- The Base Catalog
CREATE TABLE items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    base_name VARCHAR(255) NOT NULL,
    item_class VARCHAR(100) NOT NULL, -- e.g., 'weapon', 'cosmetic', 'taunt'
    UNIQUE (base_name, item_class)
);

-- Core Quality (12-value strict enum)
CREATE TABLE qualities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- Normal, Unique, Vintage, Genuine, Strange, Unusual, Haunted, Collector's, Decorated, Community, Self-Made, Valve
);

-- Modifier Lookups
CREATE TABLE killstreak_tiers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- None, Killstreak, Specialized, Professional
);

CREATE TABLE sheens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- Team Shine, Hot Rod, Manndarin...
);

CREATE TABLE killstreakers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- Fire Horns, Tornado, Hypno-Beam...
);

CREATE TABLE unusual_effects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- Burning Flames, Scorching Flames...
);

CREATE TABLE grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- Civilian, Freelance, Mercenary...
);

CREATE TABLE paints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- Zepheniah's Greed, Australium Gold...
);

CREATE TABLE collections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE -- Concealed Killer Collection...
);

CREATE TABLE botkiller_tiers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- Rustproof, Silver, Gold, Champion...
);

CREATE TABLE holiday_restrictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE -- Halloween, Christmas, Full Moon, Birthday
);

CREATE TABLE war_paints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE -- Warhawk, Coffin Nail, Cool Bikini...
);

-- Many-to-Many Lookups
CREATE TABLE spells (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE -- Exorcism, Pumpkin Bombs, Halloween Fire, Voices From Below, Footprints (Green/Purple)
);

CREATE TABLE strange_parts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE -- Kills While Explosive Jumping, Damage Dealt...
);
CREATE TABLE price_comps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,
    quality_id INT NOT NULL,
    killstreak_tier_id INT NULL,
    sheen_id INT NULL,
    killstreaker_id INT NULL,
    unusual_effect_id INT NULL,
    grade_id INT NULL,
    paint_id INT NULL,
    collection_id INT NULL,
    botkiller_tier_id INT NULL,
    holiday_restriction_id INT NULL,
    war_paint_id INT NULL,
    wear_float DECIMAL(6, 5) NULL,      -- 0.00000–1.00000
    pattern_seed INT NULL,
    is_craftable BOOLEAN NOT NULL DEFAULT TRUE,
    is_festivized BOOLEAN NOT NULL DEFAULT FALSE,
    is_australium BOOLEAN NOT NULL DEFAULT FALSE,
    price_keys DECIMAL(10, 2) NULL,
    price_metal DECIMAL(10, 2) NULL,
    source VARCHAR(100) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (quality_id) REFERENCES qualities(id),
    FOREIGN KEY (killstreak_tier_id) REFERENCES killstreak_tiers(id),
    FOREIGN KEY (sheen_id) REFERENCES sheens(id),
    FOREIGN KEY (killstreaker_id) REFERENCES killstreakers(id),
    FOREIGN KEY (unusual_effect_id) REFERENCES unusual_effects(id),
    FOREIGN KEY (grade_id) REFERENCES grades(id),
    FOREIGN KEY (paint_id) REFERENCES paints(id),
    FOREIGN KEY (collection_id) REFERENCES collections(id),
    FOREIGN KEY (botkiller_tier_id) REFERENCES botkiller_tiers(id),
    FOREIGN KEY (holiday_restriction_id) REFERENCES holiday_restrictions(id),
    FOREIGN KEY (war_paint_id) REFERENCES war_paints(id),
    
    CHECK (price_keys IS NULL OR price_keys >= 0),
    CHECK (price_metal IS NULL OR price_metal >= 0),
    CHECK (wear_float IS NULL OR (wear_float >= 0 AND wear_float <= 1)),
    
    INDEX idx_matching (item_id, quality_id, killstreak_tier_id),
    INDEX idx_recency (item_id, recorded_at)
);

CREATE TABLE comp_spells (
    comp_id INT NOT NULL,
    spell_id INT NOT NULL,
    PRIMARY KEY (comp_id, spell_id),
    FOREIGN KEY (comp_id) REFERENCES price_comps(id),
    FOREIGN KEY (spell_id) REFERENCES spells(id)
);

CREATE TABLE comp_strange_parts (
    comp_id INT NOT NULL,
    strange_part_id INT NOT NULL,
    PRIMARY KEY (comp_id, strange_part_id),
    FOREIGN KEY (comp_id) REFERENCES price_comps(id),
    FOREIGN KEY (strange_part_id) REFERENCES strange_parts(id)
);

CREATE TABLE valuations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT NOT NULL,                  -- Indexed for fast lookups without parsing JSON
    requested_item JSON NOT NULL,          -- What the user built on the frontend
    retrieved_comps JSON NOT NULL,         -- The matches we pulled from price_comps
    ai_response JSON NOT NULL,             -- The AI's structured pricing and reasoning
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE lowball_checks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    valuation_id INT NOT NULL,
    user_offer_keys DECIMAL(10, 2) DEFAULT 0.00,
    user_offer_metal DECIMAL(10, 2) DEFAULT 0.00,
    exchange_rate_used DECIMAL(10, 4) NULL,  -- Records Key->Metal rate at time of check
    discount_percentage DECIMAL(5, 2) NOT NULL,  -- e.g. -12.50 = 12.5% under estimate
    is_lowball BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (valuation_id) REFERENCES valuations(id)
);