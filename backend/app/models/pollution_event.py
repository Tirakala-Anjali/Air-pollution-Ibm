"""
ORM model for detected pollution events.
An event is a contiguous block of anomalous records grouped together.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from sqlalchemy.sql import func
from app.database.connection import Base


class PollutionEvent(Base):
    __tablename__ = "pollution_events"

    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id  = Column(String(64), index=True, nullable=False)

    start_time  = Column(DateTime, nullable=False)
    end_time    = Column(DateTime, nullable=False)
    duration_minutes = Column(Float, nullable=False)

    # Severity: NORMAL | MODERATE | HIGH | SEVERE
    severity    = Column(String(16), nullable=False, default="MODERATE")

    # Peak pollutant values during the event
    max_pm25    = Column(Float, nullable=True)
    max_pm10    = Column(Float, nullable=True)
    max_no2     = Column(Float, nullable=True)
    max_co      = Column(Float, nullable=True)

    # Average pollutant values during the event
    avg_pm25    = Column(Float, nullable=True)
    avg_pm10    = Column(Float, nullable=True)

    anomaly_score        = Column(Float, nullable=True)  # average anomaly score for the event
    anomaly_count        = Column(Integer, nullable=True) # number of anomalous records in event

    # Human-readable AI explanation
    explanation = Column(Text, nullable=True)

    created_at  = Column(DateTime, server_default=func.now())
