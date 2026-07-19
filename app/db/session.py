from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from typing import Optional
from pydantic import BaseModel

# ... the rest of your existing imports and session code

# The engine establishes the core connection to MySQL
# app/main.py

class ValuationRequest(BaseModel):
    item_id: int
    # Add defaults for keys your Phase 2 matcher expects so it doesn't crash
    is_australium: bool = False
    is_unusual: bool = False
    quality: Optional[str] = "Unique"
    particle_effect_id: Optional[int] = None
    user_offer: Optional[float] = None

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Pings connection before handing it out to prevent crashes
    pool_recycle=3600,   # Proactively recycles connections older than an hour
)

# SessionLocal is the factory that will spawn individual database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This dependency yields a secure session and guarantees it closes when finished
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()