from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# The engine establishes the core connection to MySQL
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