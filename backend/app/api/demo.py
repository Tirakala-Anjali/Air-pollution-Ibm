"""
POST /api/demo
──────────────
Load the bundled synthetic sample dataset and run it through the
EXISTING pipeline (preprocess → Isolation Forest → event detection →
explanation → database) without requiring a manual file upload.

This endpoint is purely a convenience for demonstration purposes.
It re-uses every existing service and ML module — no logic is duplicated.

The dataset is clearly labelled as synthetic demo data throughout.
"""

import io
import os
import uuid
import logging

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.preprocessing import preprocess
from app.ml.anomaly_detector import detect_anomalies
from app.ml.event_detector import detect_events
from app.services.explanation import generate_explanation
from app.models.air_quality import AirQualityRecord
from app.models.pollution_event import PollutionEvent

router = APIRouter()
logger = logging.getLogger(__name__)

# Locate the sample CSV relative to this file's position in the project tree.
# backend/app/api/demo.py  →  ../../..  →  airguard/data/sample_air_quality.csv
_HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE_CSV_PATH = os.path.normpath(
    os.path.join(_HERE, "..", "..", "..", "data", "sample_air_quality.csv")
)


@router.post("/demo")
def load_demo(db: Session = Depends(get_db)):
    """
    Load the included synthetic demo dataset and run the full AI pipeline.

    Returns the same structure as POST /api/analyze so the frontend can
    treat both responses identically.
    """
    # ── Verify the sample file exists ──────────────────────────────────────
    if not os.path.isfile(SAMPLE_CSV_PATH):
        raise HTTPException(
            status_code=404,
            detail=(
                "Demo dataset not found on the server. "
                f"Expected at: {SAMPLE_CSV_PATH}"
            ),
        )

    # ── Read CSV ────────────────────────────────────────────────────────────
    try:
        raw_df = pd.read_csv(SAMPLE_CSV_PATH)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read demo dataset: {exc}",
        )

    if raw_df.empty:
        raise HTTPException(status_code=500, detail="Demo dataset is empty.")

    session_id = str(uuid.uuid4())
    logger.info("Demo session %s: loaded %d rows from %s", session_id, len(raw_df), SAMPLE_CSV_PATH)

    # ── Preprocess (existing service, no duplication) ───────────────────────
    try:
        clean_df, preprocess_report = preprocess(raw_df)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # ── Clear any stale data for this session ───────────────────────────────
    db.query(AirQualityRecord).filter(AirQualityRecord.session_id == session_id).delete()
    db.query(PollutionEvent).filter(PollutionEvent.session_id == session_id).delete()

    # ── Anomaly detection (existing ML module, no duplication) ─────────────
    try:
        result_df, model_info = detect_anomalies(clean_df, contamination=0.05)
    except Exception as exc:
        logger.exception("Demo: anomaly detection failed")
        raise HTTPException(status_code=500, detail=f"ML error: {exc}")

    # ── Persist air-quality records ─────────────────────────────────────────
    def _safe(row, col: str):
        val = row.get(col)
        if val is None:
            return None
        try:
            f = float(val)
            return None if np.isnan(f) else f
        except (TypeError, ValueError):
            return None

    records_to_insert = []
    for _, row in result_df.iterrows():
        records_to_insert.append(AirQualityRecord(
            session_id    = session_id,
            timestamp     = row["timestamp"],
            location      = row.get("location"),
            pm25          = _safe(row, "pm25"),
            pm10          = _safe(row, "pm10"),
            no2           = _safe(row, "no2"),
            co            = _safe(row, "co"),
            so2           = _safe(row, "so2"),
            o3            = _safe(row, "o3"),
            temperature   = _safe(row, "temperature"),
            humidity      = _safe(row, "humidity"),
            wind_speed    = _safe(row, "wind_speed"),
            anomaly_score = float(row["anomaly_score"]),
            is_anomaly    = bool(row["is_anomaly"]),
        ))

    db.bulk_save_objects(records_to_insert)
    db.flush()

    # ── Event detection (existing module, no duplication) ───────────────────
    events_data = detect_events(result_df)

    event_objects = []
    for ev in events_data:
        event_objects.append(PollutionEvent(
            session_id       = session_id,
            start_time       = ev["start_time"],
            end_time         = ev["end_time"],
            duration_minutes = ev["duration_minutes"],
            severity         = ev["severity"],
            max_pm25         = ev.get("max_pm25"),
            max_pm10         = ev.get("max_pm10"),
            max_no2          = ev.get("max_no2"),
            max_co           = ev.get("max_co"),
            avg_pm25         = ev.get("avg_pm25"),
            avg_pm10         = ev.get("avg_pm10"),
            anomaly_score    = ev.get("anomaly_score"),
            anomaly_count    = ev.get("anomaly_count"),
            explanation      = generate_explanation(ev),
        ))

    db.bulk_save_objects(event_objects)
    db.commit()

    logger.info(
        "Demo session %s complete: %d anomalies, %d events",
        session_id, model_info["anomalies_detected"], len(events_data),
    )

    return {
        "session_id":      session_id,
        "is_demo":         True,
        "demo_label":      "Synthetic Demo Data — not real-world measurements",
        "preprocessing":   preprocess_report,
        "model_info":      model_info,
        "events_detected": len(events_data),
        "message": (
            f"Demo analysis complete. "
            f"{model_info['anomalies_detected']} anomalous records "
            f"grouped into {len(events_data)} pollution event(s). "
            f"Dataset: Synthetic Demo Data."
        ),
    }
