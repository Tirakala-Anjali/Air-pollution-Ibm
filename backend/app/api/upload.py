"""
POST /api/upload  – Accept a CSV file, validate it, and return a session_id.
POST /api/analyze – Run preprocessing + ML on a previously uploaded session.
"""

import io
import uuid
import logging

import numpy as np
import pandas as pd
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.preprocessing import preprocess
from app.ml.anomaly_detector import detect_anomalies
from app.ml.event_detector import detect_events
from app.services.explanation import generate_explanation
from app.models.air_quality import AirQualityRecord
from app.models.pollution_event import PollutionEvent
from app.utils.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Validate and parse an uploaded CSV.
    Returns a session_id and a data preview.
    Does NOT run ML yet – call /analyze next.
    """
    # ── File type guard ───────────────────────────────────────────────────────
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported. Please upload a .csv file.",
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(content) > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    # ── Parse CSV ─────────────────────────────────────────────────────────────
    try:
        raw_df = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not parse CSV: {exc}. Please verify the file is valid CSV.",
        )

    if raw_df.empty:
        raise HTTPException(
            status_code=400,
            detail="The CSV file contains no data rows.",
        )

    session_id = str(uuid.uuid4())

    # Return preview (first 10 rows as records)
    preview = raw_df.head(10).fillna("").to_dict(orient="records")

    return {
        "session_id": session_id,
        "filename":   file.filename,
        "rows":       len(raw_df),
        "columns":    list(raw_df.columns),
        "preview":    preview,
        # Store raw CSV content temporarily in a simple way
        # (For production, persist to object storage; here we re-parse on /analyze)
        "_csv_b64":   content.decode("utf-8", errors="replace"),
    }


@router.post("/analyze")
async def analyze(payload: dict, db: Session = Depends(get_db)):
    """
    Run the full AI pipeline on a previously uploaded CSV.

    Expects JSON body:
    {
        "session_id": "<uuid>",
        "_csv_b64": "<raw csv text>",
        "contamination": 0.05   // optional, 0.01–0.20
    }
    """
    session_id = payload.get("session_id")
    csv_text   = payload.get("_csv_b64", "")
    contamination = float(payload.get("contamination", 0.05))

    if not session_id or not csv_text:
        raise HTTPException(status_code=400, detail="session_id and CSV data are required.")

    if not (0.01 <= contamination <= 0.20):
        raise HTTPException(
            status_code=400,
            detail="contamination must be between 0.01 and 0.20.",
        )

    # ── Parse ─────────────────────────────────────────────────────────────────
    try:
        raw_df = pd.read_csv(io.StringIO(csv_text))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"CSV parse error: {exc}")

    # ── Preprocess ────────────────────────────────────────────────────────────
    try:
        clean_df, preprocess_report = preprocess(raw_df)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # ── Delete any previous records for this session (idempotent re-run) ──────
    db.query(AirQualityRecord).filter(AirQualityRecord.session_id == session_id).delete()
    db.query(PollutionEvent).filter(PollutionEvent.session_id == session_id).delete()

    # ── Anomaly detection ─────────────────────────────────────────────────────
    try:
        result_df, model_info = detect_anomalies(clean_df, contamination=contamination)
    except Exception as exc:
        logger.exception("Anomaly detection failed")
        raise HTTPException(status_code=500, detail=f"ML error: {exc}")

    # ── Persist records ───────────────────────────────────────────────────────
    records_to_insert = []
    for _, row in result_df.iterrows():
        rec = AirQualityRecord(
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
        )
        records_to_insert.append(rec)

    db.bulk_save_objects(records_to_insert)
    db.flush()

    # ── Event detection ───────────────────────────────────────────────────────
    events_data = detect_events(result_df)

    event_objects = []
    for ev in events_data:
        explanation = generate_explanation(ev)
        pe = PollutionEvent(
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
            explanation      = explanation,
        )
        event_objects.append(pe)

    db.bulk_save_objects(event_objects)
    db.commit()

    return {
        "session_id":         session_id,
        "preprocessing":      preprocess_report,
        "model_info":         model_info,
        "events_detected":    len(events_data),
        "message":            (
            f"Analysis complete. {model_info['anomalies_detected']} anomalous records "
            f"grouped into {len(events_data)} pollution event(s)."
        ),
    }


def _safe(row, col: str):
    """Return float or None for a DataFrame row value."""
    val = row.get(col)
    if val is None:
        return None
    try:
        f = float(val)
        return None if np.isnan(f) else f
    except (TypeError, ValueError):
        return None
