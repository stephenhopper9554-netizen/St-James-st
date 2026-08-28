"""
Database configuration and utilities
"""
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import os
from models import Base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/stjames"
)


def init_db(engine):
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting DB session"""
    from main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
