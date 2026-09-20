"""
GET /api/dashboard?session_id=<uuid>
Returns aggregated statistics for the dashboard cards.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.air_quality import AirQualityRecord
from app.models.pollution_event import PollutionEvent
from app.schemas.air_quality import DashboardStats

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    session_id: str = Query(..., description="Session ID returned by /api/analyze"),
    db: Session = Depends(get_db),
):
    records = (
        db.query(AirQualityRecord)
        .filter(AirQualityRecord.session_id == session_id)
        .all()
    )
    if not records:
        raise HTTPException(
            status_code=404,
            detail="No data found for this session. Please upload and analyze a CSV first.",
        )

    events = (
        db.query(PollutionEvent)
        .filter(PollutionEvent.session_id == session_id)
        .all()
    )

    total    = len(records)
    anomaly_count = sum(1 for r in records if r.is_anomaly)

    pm25_vals = [r.pm25 for r in records if r.pm25 is not None]
    pm10_vals = [r.pm10 for r in records if r.pm10 is not None]

    high_severity = sum(1 for e in events if e.severity in ("HIGH", "SEVERE"))

    # Current status = severity of the most recent event, else NORMAL
    if events:
        latest_event = max(events, key=lambda e: e.end_time)
        current_status = latest_event.severity
    else:
        current_status = "NORMAL"

    timestamps = [r.timestamp for r in records]

    return DashboardStats(
        session_id       = session_id,
        total_records    = total,
        events_detected  = len(events),
        high_severity    = high_severity,
        current_status   = current_status,
        highest_pm25     = round(max(pm25_vals), 2) if pm25_vals else None,
        highest_pm10     = round(max(pm10_vals), 2) if pm10_vals else None,
        avg_pm25         = round(sum(pm25_vals) / len(pm25_vals), 2) if pm25_vals else None,
        avg_pm10         = round(sum(pm10_vals) / len(pm10_vals), 2) if pm10_vals else None,
        anomaly_rate_pct = round(anomaly_count / total * 100, 2) if total else 0.0,
        date_range       = {
            "start": str(min(timestamps)),
            "end":   str(max(timestamps)),
        },
        model_info = {
            "algorithm": "Isolation Forest",
            "note": "Scores are relative, not official AQI values.",
        },
    )
