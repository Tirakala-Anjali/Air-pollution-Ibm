"""
Tests for the POST /api/demo endpoint.
Verifies that the demo route runs the full pipeline without duplicating logic.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import create_tables

create_tables()
client = TestClient(app)


class TestDemoEndpoint:

    def test_demo_returns_200(self):
        r = client.post("/api/demo")
        assert r.status_code == 200, r.text

    def test_demo_response_shape(self):
        r = client.post("/api/demo")
        d = r.json()
        for key in ["session_id", "is_demo", "demo_label", "preprocessing",
                    "model_info", "events_detected", "message"]:
            assert key in d, f"Missing key: {key}"

    def test_demo_is_demo_flag(self):
        r = client.post("/api/demo")
        assert r.json()["is_demo"] is True

    def test_demo_label_mentions_synthetic(self):
        r = client.post("/api/demo")
        assert "synthetic" in r.json()["demo_label"].lower()

    def test_demo_uses_isolation_forest(self):
        r = client.post("/api/demo")
        assert r.json()["model_info"]["algorithm"] == "Isolation Forest"

    def test_demo_processes_96_rows(self):
        r = client.post("/api/demo")
        assert r.json()["preprocessing"]["final_rows"] == 96

    def test_demo_detects_anomalies(self):
        r = client.post("/api/demo")
        assert r.json()["model_info"]["anomalies_detected"] > 0

    def test_demo_detects_events(self):
        r = client.post("/api/demo")
        assert r.json()["events_detected"] >= 1

    def test_demo_session_queryable(self):
        """After /demo, the session_id must work with /dashboard and /events."""
        r = client.post("/api/demo")
        sid = r.json()["session_id"]

        dash = client.get("/api/dashboard", params={"session_id": sid})
        assert dash.status_code == 200
        assert dash.json()["total_records"] == 96

        evts = client.get("/api/events", params={"session_id": sid})
        assert evts.status_code == 200
        assert len(evts.json()) >= 1

    def test_demo_idempotent(self):
        """Calling /demo twice should not duplicate records in the DB."""
        r1 = client.post("/api/demo")
        sid1 = r1.json()["session_id"]

        r2 = client.post("/api/demo")
        sid2 = r2.json()["session_id"]

        # Each call creates a fresh session; records for each are 96
        for sid in [sid1, sid2]:
            dash = client.get("/api/dashboard", params={"session_id": sid})
            assert dash.json()["total_records"] == 96

    def test_demo_trends_available(self):
        r = client.post("/api/demo")
        sid = r.json()["session_id"]
        t = client.get("/api/air-quality/trends",
                       params={"session_id": sid, "pollutant": "pm25"})
        assert t.status_code == 200
        assert len(t.json()["data"]) == 96

    def test_demo_anomaly_scores_are_varied(self):
        """Scores must not all be identical — proves real ML ran."""
        r = client.post("/api/demo")
        sid = r.json()["session_id"]
        recs = client.get("/api/air-quality",
                          params={"session_id": sid, "limit": 96}).json()
        scores = [rec["anomaly_score"] for rec in recs if rec["anomaly_score"] is not None]
        unique = len(set(round(s, 4) for s in scores))
        assert unique > 10, f"Only {unique} unique scores — ML may not have run"
