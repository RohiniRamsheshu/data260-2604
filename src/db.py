"""
HW4 - Database connection setup.
Connects to MySQL database s2604_rel via SQLAlchemy + PyMySQL driver.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USER = "appuser"
DB_PASSWORD = "AppUser2604!Secure"  # move to env var for real deployments
DB_HOST = "localhost"
DB_NAME = "s2604_rel"

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False)

# Required variable name per assignment instructions
db_session_basede26 = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session, closes it after the request."""
    db = db_session_basede26()
    try:
        yield db
    finally:
        db.close()
