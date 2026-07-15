from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, JSON, Boolean, DateTime, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

# ==========================================
# 1. FIXED-SET LOOKUP TABLES
# ==========================================
class Quality(Base):
    __tablename__ = "qualities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class KillstreakTier(Base):
    __tablename__ = "killstreak_tiers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class Sheen(Base):
    __tablename__ = "sheens"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class Killstreaker(Base):
    __tablename__ = "killstreakers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class UnusualEffect(Base):
    __tablename__ = "unusual_effects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class Grade(Base):
    __tablename__ = "grades"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class Paint(Base):
    __tablename__ = "paints"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class Collection(Base):
    __tablename__ = "collections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

class BotkillerTier(Base):
    __tablename__ = "botkiller_tiers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class HolidayRestriction(Base):
    __tablename__ = "holiday_restrictions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

class WarPaint(Base):
    __tablename__ = "war_paints"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

class Spell(Base):
    __tablename__ = "spells"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

class StrangePart(Base):
    __tablename__ = "strange_parts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)


# ==========================================
# 2. JUNCTION TABLES (Many-to-Many)
# ==========================================
# SQLAlchemy handles pure junction tables slightly differently using `Table` 
# rather than a full class, to make the many-to-many relationship seamless.
comp_spells = Table(
    "comp_spells",
    Base.metadata,
    Column("comp_id", Integer, ForeignKey("price_comps.id"), primary_key=True),
    Column("spell_id", Integer, ForeignKey("spells.id"), primary_key=True),
)

comp_strange_parts = Table(
    "comp_strange_parts",
    Base.metadata,
    Column("comp_id", Integer, ForeignKey("price_comps.id"), primary_key=True),
    Column("strange_part_id", Integer, ForeignKey("strange_parts.id"), primary_key=True),
)


# ==========================================
# 3. CORE FACT TABLES
# ==========================================
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    base_name = Column(String(255), nullable=False)
    item_class = Column(String(100), nullable=False)
    defindex = Column(Integer, unique=True, nullable=True)

class PriceComp(Base):
    __tablename__ = "price_comps"
    id = Column(Integer, primary_key=True, index=True)

    
    # Core Item Link
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    item = relationship("Item",back_populates="price_comps")
    
    # FK Lookups
    quality_id = Column(Integer, ForeignKey("qualities.id"), nullable=False)
    killstreak_tier_id = Column(Integer, ForeignKey("killstreak_tiers.id"))
    sheen_id = Column(Integer, ForeignKey("sheens.id"))
    killstreaker_id = Column(Integer, ForeignKey("killstreakers.id"))
    unusual_effect_id = Column(Integer, ForeignKey("unusual_effects.id"))
    grade_id = Column(Integer, ForeignKey("grades.id"))
    paint_id = Column(Integer, ForeignKey("paints.id"))
    collection_id = Column(Integer, ForeignKey("collections.id"))
    botkiller_tier_id = Column(Integer, ForeignKey("botkiller_tiers.id"))
    holiday_restriction_id = Column(Integer, ForeignKey("holiday_restrictions.id"))
    war_paint_id = Column(Integer, ForeignKey("war_paints.id"))
    # relationships
    quality = relationship("Quality")
    killstreak_tier = relationship("KillstreakTier")
    sheen = relationship("Sheen")
    killstreaker = relationship("Killstreaker")
    unusual_effect = relationship("UnusualEffect")
    grade = relationship("Grade")
    paint = relationship("Paint")
    collection = relationship("Collection")
    botkiller_tier = relationship("BotkillerTier")
    holiday_restriction = relationship("HolidayRestriction")
    war_paint = relationship("WarPaint")
    
    # Direct Attributes
    wear_float = Column(Numeric(6, 5))
    pattern_seed = Column(Integer)
    is_craftable = Column(Boolean, nullable=False, default=True)
    is_festivized = Column(Boolean, nullable=False, default=False)
    is_australium = Column(Boolean, nullable=False, default=False)
    
    # Pricing & Metadata
    transaction_timestamp = Column(Integer, nullable=False, index=True)
    listing_type = Column(String(50), nullable=False)                 # Added length
    external_id = Column(String(100), unique=True, nullable=True)     # Added length
    price_keys = Column(Numeric(10, 2))
    price_metal = Column(Numeric(10, 2))
    source = Column(String(100), nullable=False)
    recorded_at = Column(DateTime, default=func.now())

    # Many-to-Many Relationships
    spells = relationship("Spell", secondary=comp_spells)
    strange_parts = relationship("StrangePart", secondary=comp_strange_parts)
    __table_args__ = (
        UniqueConstraint(
            'item_id', 
            'transaction_timestamp', 
            'listing_type', 
            name='uix_item_timestamp_type'
        ),
    )


# ==========================================
# 4. AUDIT & LOGIC TABLES (Your work!)
# ==========================================
class Valuation(Base):
    __tablename__ = "valuations"
    id = Column(Integer, primary_key=True, index=True)
    
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    item = relationship("Item")
    
    requested_item = Column(JSON, nullable=False)
    retrieved_comps = Column(JSON, nullable=False)
    ai_response = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())

class LowballCheck(Base):
    __tablename__ = "lowball_checks"
    id = Column(Integer, primary_key=True, index=True)
    
    valuation_id = Column(Integer, ForeignKey("valuations.id"), nullable=False)
    valuation = relationship("Valuation") # Corrected from "valuations"
    
    user_offer_keys = Column(Numeric(10, 2))
    user_offer_metal = Column(Numeric(10, 2))
    exchange_rate_used = Column(Numeric(10, 4))
    discount_percentage = Column(Numeric(5, 2), nullable=False)
    is_lowball = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=func.now())