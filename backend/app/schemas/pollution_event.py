"""Pydantic schemas for pollution events."""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PollutionEventOut(BaseModel):
    id:               int
    session_id:       str
    start_time:       datetime
    end_time:         datetime
    duration_minutes: float
    severity:         str
    max_pm25:         Optional[float] = None
    max_pm10:         Optional[float] = None
    max_no2:          Optional[float] = None
    max_co:           Optional[float] = None
    avg_pm25:         Optional[float] = None
    avg_pm10:         Optional[float] = None
    anomaly_score:    Optional[float] = None
    anomaly_count:    Optional[int]   = None
    explanation:      Optional[str]   = None
    created_at:       Optional[datetime] = None

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
