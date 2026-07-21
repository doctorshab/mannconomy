-- Auto-generated from app/db/models.py via SQLAlchemy metadata.
-- Regenerate any time models.py changes so this file never drifts again.

CREATE TABLE botkiller_tiers (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_botkiller_tiers_id ON botkiller_tiers (id);

CREATE TABLE collections (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_collections_id ON collections (id);

CREATE TABLE grades (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_grades_id ON grades (id);

CREATE TABLE holiday_restrictions (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_holiday_restrictions_id ON holiday_restrictions (id);

CREATE TABLE items (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	base_name VARCHAR(255) NOT NULL, 
	item_class VARCHAR(100) NOT NULL, 
	defindex INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (defindex)
);

CREATE INDEX ix_items_id ON items (id);

CREATE TABLE killstreak_tiers (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_killstreak_tiers_id ON killstreak_tiers (id);

CREATE TABLE killstreakers (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_killstreakers_id ON killstreakers (id);

CREATE TABLE paints (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_paints_id ON paints (id);

CREATE TABLE qualities (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_qualities_id ON qualities (id);

CREATE TABLE sheens (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_sheens_id ON sheens (id);

CREATE TABLE spells (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_spells_id ON spells (id);

CREATE TABLE strange_parts (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_strange_parts_id ON strange_parts (id);

CREATE TABLE unusual_effects (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_unusual_effects_id ON unusual_effects (id);

CREATE TABLE war_paints (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_war_paints_id ON war_paints (id);

CREATE TABLE price_comps (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	item_id INTEGER NOT NULL, 
	quality_id INTEGER NOT NULL, 
	killstreak_tier_id INTEGER, 
	sheen_id INTEGER, 
	killstreaker_id INTEGER, 
	unusual_effect_id INTEGER, 
	grade_id INTEGER, 
	paint_id INTEGER, 
	collection_id INTEGER, 
	botkiller_tier_id INTEGER, 
	holiday_restriction_id INTEGER, 
	war_paint_id INTEGER, 
	wear_float NUMERIC(6, 5), 
	pattern_seed INTEGER, 
	is_craftable BOOL NOT NULL, 
	is_festivized BOOL NOT NULL, 
	is_australium BOOL NOT NULL, 
	transaction_timestamp INTEGER NOT NULL, 
	listing_type VARCHAR(50) NOT NULL, 
	external_id VARCHAR(100), 
	price_keys NUMERIC(10, 2), 
	price_metal NUMERIC(10, 2), 
	source VARCHAR(100) NOT NULL, 
	recorded_at DATETIME, 
	PRIMARY KEY (id), 
	CONSTRAINT uix_item_timestamp_type UNIQUE (item_id, transaction_timestamp, listing_type), 
	CONSTRAINT ck_price_keys_nonneg CHECK (price_keys IS NULL OR price_keys >= 0), 
	CONSTRAINT ck_price_metal_nonneg CHECK (price_metal IS NULL OR price_metal >= 0), 
	CONSTRAINT ck_wear_float_range CHECK (wear_float IS NULL OR (wear_float >= 0 AND wear_float <= 1)), 
	FOREIGN KEY(item_id) REFERENCES items (id), 
	FOREIGN KEY(quality_id) REFERENCES qualities (id), 
	FOREIGN KEY(killstreak_tier_id) REFERENCES killstreak_tiers (id), 
	FOREIGN KEY(sheen_id) REFERENCES sheens (id), 
	FOREIGN KEY(killstreaker_id) REFERENCES killstreakers (id), 
	FOREIGN KEY(unusual_effect_id) REFERENCES unusual_effects (id), 
	FOREIGN KEY(grade_id) REFERENCES grades (id), 
	FOREIGN KEY(paint_id) REFERENCES paints (id), 
	FOREIGN KEY(collection_id) REFERENCES collections (id), 
	FOREIGN KEY(botkiller_tier_id) REFERENCES botkiller_tiers (id), 
	FOREIGN KEY(holiday_restriction_id) REFERENCES holiday_restrictions (id), 
	FOREIGN KEY(war_paint_id) REFERENCES war_paints (id), 
	UNIQUE (external_id)
);

CREATE INDEX idx_recency ON price_comps (item_id, recorded_at);
CREATE INDEX idx_matching ON price_comps (item_id, quality_id, killstreak_tier_id);
CREATE INDEX ix_price_comps_transaction_timestamp ON price_comps (transaction_timestamp);
CREATE INDEX ix_price_comps_id ON price_comps (id);

CREATE TABLE valuations (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	item_id INTEGER NOT NULL, 
	requested_item JSON NOT NULL, 
	retrieved_comps JSON NOT NULL, 
	ai_response JSON NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(item_id) REFERENCES items (id)
);

CREATE INDEX ix_valuations_id ON valuations (id);

CREATE TABLE comp_spells (
	comp_id INTEGER NOT NULL, 
	spell_id INTEGER NOT NULL, 
	PRIMARY KEY (comp_id, spell_id), 
	FOREIGN KEY(comp_id) REFERENCES price_comps (id), 
	FOREIGN KEY(spell_id) REFERENCES spells (id)
);

CREATE TABLE comp_strange_parts (
	comp_id INTEGER NOT NULL, 
	strange_part_id INTEGER NOT NULL, 
	PRIMARY KEY (comp_id, strange_part_id), 
	FOREIGN KEY(comp_id) REFERENCES price_comps (id), 
	FOREIGN KEY(strange_part_id) REFERENCES strange_parts (id)
);

CREATE TABLE lowball_checks (
	id INTEGER NOT NULL AUTO_INCREMENT, 
	valuation_id INTEGER NOT NULL, 
	user_offer_keys NUMERIC(10, 2), 
	user_offer_metal NUMERIC(10, 2), 
	exchange_rate_used NUMERIC(10, 4), 
	discount_percentage NUMERIC(5, 2) NOT NULL, 
	is_lowball BOOL NOT NULL, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(valuation_id) REFERENCES valuations (id)
);

CREATE INDEX ix_lowball_checks_id ON lowball_checks (id);