# database/migrate.py

from sqlalchemy import inspect, text

from database.db import engine, Base

# Import all models
from database.models import (
    User,
    Analysis,
    Feedback,
    Message,
    Product,
    Publication,
    Parcel,
    Crop,
    Sensor,
    SensorReading,
)


def column_exists(table_name, column_name):

    inspector = inspect(engine)

    columns = inspector.get_columns(
        table_name
    )

    return any(
        column["name"] == column_name
        for column in columns
    )


def migrate():

    # Create new tables
    Base.metadata.create_all(
        bind=engine
    )

    # Existing products table may already exist.
    # create_all DOES NOT add new columns.

    if not column_exists(
        "products",
        "image_path"
    ):

        with engine.begin() as conn:

            conn.execute(
                text(
                    "ALTER TABLE products "
                    "ADD COLUMN image_path VARCHAR(500)"
                )
            )

    if not column_exists(
        "products",
        "is_active"
    ):

        with engine.begin() as conn:

            conn.execute(
                text(
                    "ALTER TABLE products "
                    "ADD COLUMN is_active BOOLEAN DEFAULT 1"
                )
            )

    print("Database migration completed.")


if __name__ == "__main__":
    migrate()