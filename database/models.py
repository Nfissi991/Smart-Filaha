# database/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)  # user | conseiller | admin
    language = Column(String(20), default="Français")
    is_approved = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    analyses = relationship("Analysis", back_populates="user")
    parcels = relationship("Parcel", back_populates="owner", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    disease_key = Column(String(100))
    disease_name = Column(String(200))
    plant_type = Column(String(100))
    confidence = Column(Float)
    severity = Column(String(20))
    language = Column(String(20))
    source = Column(String(20), default="image")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analyses")
    feedbacks = relationship("Feedback", back_populates="analysis", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    is_correct = Column(Boolean)
    correct_label = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="feedbacks")


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    conseiller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, default=0)
    stock = Column(Integer, default=0)
    image_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Publication(Base):
    __tablename__ = "publications"
    id = Column(Integer, primary_key=True)
    conseiller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    publication_type = Column(String(30), default="conseil")  # conseil|article|annonce|produit
    image_path = Column(String(500), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    status = Column(String(20), default="published")  # draft|published|hidden
    created_at = Column(DateTime, default=datetime.utcnow)


class Parcel(Base):
    __tablename__ = "parcels"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(150), nullable=False)
    location = Column(String(255), nullable=True)
    surface_ha = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="parcels")
    crops = relationship("Crop", back_populates="parcel", cascade="all, delete-orphan")
    sensors = relationship("Sensor", back_populates="parcel", cascade="all, delete-orphan")


class Crop(Base):
    __tablename__ = "crops"
    id = Column(Integer, primary_key=True)
    parcel_id = Column(Integer, ForeignKey("parcels.id"), nullable=False)
    name = Column(String(100), nullable=False)
    variety = Column(String(100), nullable=True)
    health_status = Column(String(30), default="Bonne")
    planted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    parcel = relationship("Parcel", back_populates="crops")


class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parcel_id = Column(Integer, ForeignKey("parcels.id"), nullable=True)
    name = Column(String(100), nullable=False)
    device_uid = Column(String(100), unique=True, nullable=False)
    sensor_type = Column(String(30), default="multi")  # soil|weather|multi
    is_active = Column(Boolean, default=True)
    battery_level = Column(Float, default=100)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    parcel = relationship("Parcel", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    soil_moisture = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    air_humidity = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    sensor = relationship("Sensor", back_populates="readings")