"""Pydantic response/request schemas for air-quality data."""

from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class AirQualityRecordOut(BaseModel):
    id:            int
    session_id:    str
    timestamp:     datetime
    location:      Optional[str] = None
    pm25:          Optional[float] = None
    pm10:          Optional[float] = None
    no2:           Optional[float] = None
    co:            Optional[float] = None
    so2:           Optional[float] = None
    o3:            Optional[float] = None
    temperature:   Optional[float] = None
    humidity:      Optional[float] = None
    wind_speed:    Optional[float] = None
    anomaly_score: Optional[float] = None
    is_anomaly:    Optional[bool]  = None

    model_config = {"from_attributes": True}


class TrendPoint(BaseModel):
    timestamp:     datetime
    value:         Optional[float] = None
    is_anomaly:    Optional[bool]  = False
    anomaly_score: Optional[float] = None


class TrendsResponse(BaseModel):
    pollutant: str
    data:      List[TrendPoint]
    session_id: str


class DashboardStats(BaseModel):
    session_id:       str
    total_records:    int
    events_detected:  int
    high_severity:    int   # HIGH + SEVERE
    current_status:   str   # severity label of the most recent event or NORMAL
    highest_pm25:     Optional[float] = None
    highest_pm10:     Optional[float] = None
    avg_pm25:         Optional[float] = None
    avg_pm10:         Optional[float] = None
    anomaly_rate_pct: float
    date_range:       dict
    model_info:       dict
