"""
Pollution event detection and severity classification.

Algorithm
─────────
1. Walk through the anomaly-labelled time series chronologically.
2. Consecutive anomalous rows are merged into a single event.
3. A gap of more than `gap_minutes` between anomalous rows breaks
   the streak and starts a new event.
4. Events that contain fewer than `min_anomalies` records are discarded
   (single-record spikes that are likely sensor noise).
5. Each event is then scored for severity using the peak PM2.5 and
   peak anomaly score.

Severity categories (custom, NOT official government AQI)
──────────────────────────────────────────────────────────
These thresholds are defined specifically for this system.
They are based on the WHO 24-hour mean PM2.5 guideline (15 µg/m³, 2021)
and are provided for educational/awareness purposes only.
They should NOT be used in place of official government air-quality advisories.

  NORMAL   – anomaly score < 0.40 AND max PM2.5 ≤ 25
  MODERATE – anomaly score 0.40–0.59 OR max PM2.5 26–55
  HIGH     – anomaly score 0.60–0.79 OR max PM2.5 56–150
  SEVERE   – anomaly score ≥ 0.80    OR max PM2.5 > 150

Reference: WHO Global Air Quality Guidelines (2021).
https://www.who.int/publications/i/item/9789240034228
"""

import logging
from typing import List
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# ── Tuneable parameters ───────────────────────────────────────────────────────
DEFAULT_GAP_MINUTES  = 60   # max gap between anomalous rows to stay in same event
DEFAULT_MIN_ANOMALIES = 2   # minimum anomalous records to constitute a real event


def _classify_severity(max_pm25: float | None, avg_anomaly_score: float) -> str:
    """
    Assign a human-readable severity label.

    Severity is determined by BOTH peak PM2.5 (when available) and the
    average normalised anomaly score.  The higher of the two classifications
    is returned.
    """
    # PM2.5-based severity (WHO-informed thresholds, not official AQI)
    pm_severity = "NORMAL"
    if max_pm25 is not None and not np.isnan(max_pm25):
        if max_pm25 > 150:
            pm_severity = "SEVERE"
        elif max_pm25 > 55:
            pm_severity = "HIGH"
        elif max_pm25 > 25:
            pm_severity = "MODERATE"

    # Score-based severity
    score_severity = "NORMAL"
    if avg_anomaly_score >= 0.80:
        score_severity = "SEVERE"
    elif avg_anomaly_score >= 0.60:
        score_severity = "HIGH"
    elif avg_anomaly_score >= 0.40:
        score_severity = "MODERATE"

    # Return the more serious of the two
    ranking = {"NORMAL": 0, "MODERATE": 1, "HIGH": 2, "SEVERE": 3}
    if ranking[score_severity] >= ranking[pm_severity]:
        return score_severity
    return pm_severity


def detect_events(
    df: pd.DataFrame,
    gap_minutes: int = DEFAULT_GAP_MINUTES,
    min_anomalies: int = DEFAULT_MIN_ANOMALIES,
) -> List[dict]:
    """
    Group consecutive anomalous records into pollution events.

    Parameters
    ----------
    df : pd.DataFrame
        Output of ``detect_anomalies`` – must have ``timestamp``,
        ``is_anomaly``, and ``anomaly_score`` columns.
    gap_minutes : int
        If the time gap between two anomalous rows exceeds this value,
        they belong to separate events.
    min_anomalies : int
        Minimum number of anomalous records for an event to be reported.

    Returns
    -------
    events : list[dict]
        Each dict represents one pollution event with all statistics.
    """
    if df.empty or "is_anomaly" not in df.columns:
        return []

    df = df.sort_values("timestamp").reset_index(drop=True)
    anomaly_df = df[df["is_anomaly"]].copy()

    if anomaly_df.empty:
        logger.info("No anomalies detected; no events to report.")
        return []

    events: List[dict] = []
    event_rows: List[pd.Series] = []

    for _, row in anomaly_df.iterrows():
        if not event_rows:
            event_rows.append(row)
            continue

        prev_ts = event_rows[-1]["timestamp"]
        curr_ts = row["timestamp"]
        gap = (curr_ts - prev_ts).total_seconds() / 60.0

        if gap <= gap_minutes:
            event_rows.append(row)
        else:
            # Finalise the current event
            if len(event_rows) >= min_anomalies:
                events.append(_build_event(event_rows, len(events) + 1))
            event_rows = [row]

    # Don't forget the last open event
    if len(event_rows) >= min_anomalies:
        events.append(_build_event(event_rows, len(events) + 1))

    logger.info("Detected %d pollution event(s).", len(events))
    return events


def _build_event(rows: list, event_id: int) -> dict:
    """Compute all statistics for one event from its constituent rows."""
    event_df = pd.DataFrame(rows)

    start_time = event_df["timestamp"].min()
    end_time   = event_df["timestamp"].max()
    duration   = (end_time - start_time).total_seconds() / 60.0  # minutes

    avg_score  = float(event_df["anomaly_score"].mean())
    max_score  = float(event_df["anomaly_score"].max())

    def _safe_max(col: str) -> float | None:
        if col in event_df.columns:
            vals = event_df[col].dropna()
            return float(vals.max()) if not vals.empty else None
        return None

    def _safe_avg(col: str) -> float | None:
        if col in event_df.columns:
            vals = event_df[col].dropna()
            return round(float(vals.mean()), 2) if not vals.empty else None
        return None

    max_pm25 = _safe_max("pm25")
    max_pm10 = _safe_max("pm10")
    max_no2  = _safe_max("no2")
    max_co   = _safe_max("co")

    severity = _classify_severity(max_pm25, avg_score)

    return {
        "id":               event_id,
        "start_time":       start_time,
        "end_time":         end_time,
        "duration_minutes": round(duration, 1),
        "severity":         severity,
        "max_pm25":         round(max_pm25, 2) if max_pm25 is not None else None,
        "max_pm10":         round(max_pm10, 2) if max_pm10 is not None else None,
        "max_no2":          round(max_no2,  2) if max_no2  is not None else None,
        "max_co":           round(max_co,   2) if max_co   is not None else None,
        "avg_pm25":         _safe_avg("pm25"),
        "avg_pm10":         _safe_avg("pm10"),
        "anomaly_score":    round(avg_score, 4),
        "max_anomaly_score":round(max_score, 4),
        "anomaly_count":    len(rows),
    }
