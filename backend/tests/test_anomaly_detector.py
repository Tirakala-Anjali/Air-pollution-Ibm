"""Tests for the Isolation Forest anomaly detection pipeline."""

import pytest
import pandas as pd
import numpy as np
from app.ml.anomaly_detector import detect_anomalies


def make_clean_df(n=50, spike_at=None):
    """Return a preprocessed-style DataFrame with optional spike."""
    ts = pd.date_range("2024-01-01", periods=n, freq="h")
    pm25 = [25.0 + np.random.normal(0, 2) for _ in range(n)]
    pm10 = [45.0 + np.random.normal(0, 3) for _ in range(n)]

    if spike_at is not None:
        for idx in spike_at:
            pm25[idx] = 180.0  # severe spike
            pm10[idx] = 280.0

    return pd.DataFrame({"timestamp": ts, "pm25": pm25, "pm10": pm10})


class TestAnomalyDetector:

    def test_output_columns(self):
        df = make_clean_df()
        result, info = detect_anomalies(df)
        assert "anomaly_score" in result.columns
        assert "is_anomaly" in result.columns

    def test_row_count_preserved(self):
        df = make_clean_df(40)
        result, _ = detect_anomalies(df)
        assert len(result) == 40

    def test_score_range(self):
        df = make_clean_df(60)
        result, _ = detect_anomalies(df)
        assert result["anomaly_score"].between(0.0, 1.0).all()

    def test_spike_detected(self):
        """A very large spike should almost always be flagged."""
        np.random.seed(42)
        df = make_clean_df(80, spike_at=[40, 41, 42])
        result, info = detect_anomalies(df, contamination=0.05)
        assert info["anomalies_detected"] > 0

    def test_model_info_keys(self):
        df = make_clean_df(30)
        _, info = detect_anomalies(df)
        for key in ["algorithm", "n_estimators", "contamination",
                    "features_used", "total_records", "anomalies_detected"]:
            assert key in info

    def test_contamination_respected(self):
        np.random.seed(0)
        df = make_clean_df(100)
        _, info_5  = detect_anomalies(df, contamination=0.05)
        _, info_15 = detect_anomalies(df, contamination=0.15)
        # Higher contamination → more anomalies flagged
        assert info_15["anomalies_detected"] >= info_5["anomalies_detected"]

    def test_no_features_raises(self):
        df = pd.DataFrame({"timestamp": pd.date_range("2024-01-01", periods=10, freq="h"),
                           "location": ["A"] * 10})
        with pytest.raises(ValueError):
            detect_anomalies(df)
