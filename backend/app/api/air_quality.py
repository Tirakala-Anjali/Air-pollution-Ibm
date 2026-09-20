"""
GET /api/air-quality          – paginated list of records
GET /api/air-quality/trends   – time-series data for a chosen pollutant
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.air_quality import AirQualityRecord
from app.schemas.air_quality import AirQualityRecordOut, TrendsResponse, TrendPoint

router = APIRouter()
logger = logging.getLogger(__name__)

VALID_POLLUTANTS = {"pm25", "pm10", "no2", "co", "so2", "o3",
                    "temperature", "humidity", "wind_speed"}


@router.get("/air-quality", response_model=List[AirQualityRecordOut])
def list_records(
    session_id: str   = Query(...),
    skip:       int   = Query(0,    ge=0),
    limit:      int   = Query(500,  ge=1, le=5000),
    anomaly_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    q = db.query(AirQualityRecord).filter(AirQualityRecord.session_id == session_id)
    if anomaly_only:
        q = q.filter(AirQualityRecord.is_anomaly == True)  # noqa: E712
    records = q.order_by(AirQualityRecord.timestamp).offset(skip).limit(limit).all()
    return records


@router.get("/air-quality/trends", response_model=TrendsResponse)
def get_trends(
    session_id: str = Query(...),
    pollutant:  str = Query("pm25", description="pm25|pm10|no2|co|so2|o3|temperature"),
    db: Session = Depends(get_db),
):
    if pollutant not in VALID_POLLUTANTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pollutant '{pollutant}'. Choose from: {', '.join(sorted(VALID_POLLUTANTS))}",
        )

    records = (
        db.query(AirQualityRecord)
        .filter(AirQualityRecord.session_id == session_id)
        .order_by(AirQualityRecord.timestamp)
        .all()
    )
    if not records:
        raise HTTPException(status_code=404, detail="No records found for this session.")

    points = []
    for r in records:
        value = getattr(r, pollutant, None)
        points.append(
            TrendPoint(
                timestamp     = r.timestamp,
                value         = value,
                is_anomaly    = r.is_anomaly,
                anomaly_score = r.anomaly_score,
            )
        )

    return TrendsResponse(pollutant=pollutant, data=points, session_id=session_id)
