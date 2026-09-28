# database/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config.settings import DB_URL

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from database.models import (
        User, Analysis, Feedback, Message, Product,
        Publication, Parcel, Crop, Sensor, SensorReading,
    )
    Base.metadata.create_all(bind=engine)