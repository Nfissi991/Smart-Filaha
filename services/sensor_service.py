# services/sensor_service.py
from datetime import datetime
from database.db import SessionLocal
from database.models import Sensor, SensorReading


def get_my_sensors(owner_id):
    db = SessionLocal()
    try:
        return db.query(Sensor).filter(Sensor.owner_id == owner_id).order_by(Sensor.created_at.desc()).all()
    finally:
        db.close()


def get_sensor(sensor_id, owner_id):
    db = SessionLocal()
    try:
        return db.query(Sensor).filter(Sensor.id == sensor_id, Sensor.owner_id == owner_id).first()
    finally:
        db.close()


def create_sensor(owner_id, name, device_uid, sensor_type="multi", parcel_id=None):
    db = SessionLocal()
    try:
        sensor = Sensor(
            owner_id=owner_id, name=name, device_uid=device_uid, sensor_type=sensor_type,
            parcel_id=parcel_id, is_active=True, battery_level=100, last_seen=datetime.utcnow(),
        )
        db.add(sensor)
        db.commit()
        db.refresh(sensor)
        return sensor
    finally:
        db.close()


def add_reading(sensor_id, soil_moisture=None, temperature=None, air_humidity=None, ph=None):
    db = SessionLocal()
    try:
        reading = SensorReading(
            sensor_id=sensor_id, soil_moisture=soil_moisture, temperature=temperature,
            air_humidity=air_humidity, ph=ph, recorded_at=datetime.utcnow(),
        )
        db.add(reading)
        sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
        if sensor:
            sensor.last_seen = datetime.utcnow()
        db.commit()
        db.refresh(reading)
        return reading
    finally:
        db.close()


def get_readings(sensor_id, limit=50):
    db = SessionLocal()
    try:
        return (db.query(SensorReading)
                .filter(SensorReading.sensor_id == sensor_id)
                .order_by(SensorReading.recorded_at.desc()).limit(limit).all())
    finally:
        db.close()