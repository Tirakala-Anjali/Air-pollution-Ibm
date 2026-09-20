"""Tests for pollution event grouping and severity classification."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.ml.event_detector import detect_events, _classify_severity


def make_result_df(anomaly_pattern, base_ts=None):
    """
    Build a synthetic result DataFrame.
    anomaly_pattern: list of True/False per row.
    """
    if base_ts is None:
        base_ts = datetime(2024, 1, 1, 0, 0, 0)
    rows = []
    for i, is_anom in enumerate(anomaly_pattern):
        rows.append({
            "timestamp":     base_ts + timedelta(hours=i),
            "pm25":          150.0 if is_anom else 25.0,
            "pm10":          250.0 if is_anom else 40.0,
            "is_anomaly":    is_anom,
            "anomaly_score": 0.85 if is_anom else 0.15,
        })
    return pd.DataFrame(rows)


class TestEventDetector:

    def test_no_anomalies_no_events(self):
        df = make_result_df([False] * 20)
        events = detect_events(df)
        assert events == []

    def test_single_run_one_event(self):
        pattern = [False]*5 + [True]*4 + [False]*5
        df = make_result_df(pattern)
        events = detect_events(df, min_anomalies=2)
        assert len(events) == 1

    def test_two_runs_two_events(self):
        # Two separate bursts with a large gap between them
        pattern = ([False]*3 + [True]*3 + [False]*10 +
                   [True]*3 + [False]*3)
        df = make_result_df(pattern)
        # gap_minutes=60 → 10h gap → two events
        events = detect_events(df, gap_minutes=60, min_anomalies=2)
        assert len(events) == 2

    def test_event_has_correct_fields(self):
        pattern = [False]*3 + [True]*4 + [False]*3
        df = make_result_df(pattern)
        events = detect_events(df, min_anomalies=2)
        assert len(events) == 1
        ev = events[0]
        for field in ["id", "start_time", "end_time", "duration_minutes",
                      "severity", "max_pm25", "max_pm10", "anomaly_score", "anomaly_count"]:
            assert field in ev

    def test_min_anomalies_filter(self):
        """A run of only 1 anomaly should be dropped."""
        pattern = [False]*5 + [True]*1 + [False]*5
        df = make_result_df(pattern)
        events = detect_events(df, min_anomalies=2)
        assert events == []

    def test_duration_calculated(self):
        pattern = [False]*2 + [True]*5 + [False]*2
        df = make_result_df(pattern)
        events = detect_events(df, min_anomalies=2)
        assert len(events) == 1
        # 5 rows × 1h spacing = 4h gap between first and last → 240 min
        assert events[0]["duration_minutes"] == 240.0


class TestSeverityClassification:

    def test_normal(self):
        assert _classify_severity(20.0, 0.2) == "NORMAL"

    def test_moderate_by_score(self):
        assert _classify_severity(10.0, 0.45) == "MODERATE"

    def test_high_by_pm25(self):
        assert _classify_severity(80.0, 0.3) == "HIGH"

    def test_severe_by_pm25(self):
        assert _classify_severity(200.0, 0.5) == "SEVERE"

    def test_severe_by_score(self):
        assert _classify_severity(10.0, 0.85) == "SEVERE"

    def test_higher_wins(self):
        # score says HIGH (0.65) but pm25 says SEVERE (>150) → SEVERE
        assert _classify_severity(160.0, 0.65) == "SEVERE"
