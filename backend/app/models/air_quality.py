"""
ORM model for individual air-quality records.
One row = one timestamped measurement from the uploaded CSV.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database.connection import Base


class AirQualityRecord(Base):
    __tablename__ = "air_quality_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(64), index=True, nullable=False)   # ties rows to an upload session
    timestamp = Column(DateTime, nullable=False, index=True)
    location = Column(String(128), nullable=True)

    # Pollutants (µg/m³ unless noted)
    pm25 = Column(Float, nullable=True)   # PM2.5
    pm10 = Column(Float, nullable=True)   # PM10
    no2  = Column(Float, nullable=True)   # NO2
    co   = Column(Float, nullable=True)   # CO (mg/m³)
    so2  = Column(Float, nullable=True)   # SO2
    o3   = Column(Float, nullable=True)   # Ozone

    # Meteorological (optional)
    temperature  = Column(Float, nullable=True)  # °C
    humidity     = Column(Float, nullable=True)  # %
    wind_speed   = Column(Float, nullable=True)  # m/s

    # ML output
    anomaly_score = Column(Float, nullable=True)       # raw Isolation Forest score
    is_anomaly    = Column(Boolean, nullable=True, default=False)

    created_at = Column(DateTime, server_default=func.now())
