"""
Integration tests for the FastAPI REST endpoints.
Uses TestClient (synchronous) — no external server needed.
"""

import io
import pytest
import pandas as pd
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import create_tables

# Ensure DB tables exist before tests run
create_tables()

client = TestClient(app)


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_csv_bytes(rows=30, add_spike=True):
    """Generate a minimal valid CSV for upload tests."""
    import numpy as np
    np.random.seed(1)
    ts = pd.date_range("2024-01-01", periods=rows, freq="h")
    pm25 = [25.0 + np.random.normal(0, 2) for _ in range(rows)]
    pm10 = [45.0 + np.random.normal(0, 3) for _ in range(rows)]
    if add_spike:
        pm25[15] = 180.0
        pm25[16] = 175.0
        pm25[17] = 190.0
        pm10[15] = 280.0
        pm10[16] = 275.0
        pm10[17] = 290.0
    df = pd.DataFrame({"timestamp": ts.astype(str), "pm25": pm25, "pm10": pm10})
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    return buf.getvalue()


# ── Health ─────────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_ok(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "app" in data


# ── Upload ─────────────────────────────────────────────────────────────────────

class TestUpload:
    def test_valid_upload(self):
        csv_bytes = make_csv_bytes()
        r = client.post("/api/upload", files={"file": ("test.csv", io.BytesIO(csv_bytes), "text/csv")})
        assert r.status_code == 200
        data = r.json()
        assert "session_id" in data
        assert data["rows"] == 30
        assert "_csv_b64" in data

    def test_non_csv_rejected(self):
        r = client.post("/api/upload", files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")})
        assert r.status_code == 400

    def test_empty_file_rejected(self):
        r = client.post("/api/upload", files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")})
        assert r.status_code == 400

    def test_invalid_csv_rejected(self):
        r = client.post("/api/upload", files={"file": ("bad.csv", io.BytesIO(b"\x00\x01\x02"), "text/csv")})
        # Should return 400 or 422
        assert r.status_code in (400, 422)


# ── Full pipeline integration ──────────────────────────────────────────────────

class TestFullPipeline:
    """Upload → Analyze → Dashboard → Events"""

    def setup_method(self):
        # Upload and analyze once; store session_id for all methods in this class
        csv_bytes = make_csv_bytes(rows=50, add_spike=True)
        r = client.post("/api/upload", files={"file": ("data.csv", io.BytesIO(csv_bytes), "text/csv")})
        assert r.status_code == 200
        upload = r.json()
        self.session_id = upload["session_id"]
        self.csv_b64    = upload["_csv_b64"]

    def test_analyze(self):
        r = client.post("/api/analyze", json={
            "session_id": self.session_id,
            "_csv_b64":   self.csv_b64,
            "contamination": 0.08,
        })
        assert r.status_code == 200
        data = r.json()
        assert "events_detected" in data
        assert data["model_info"]["algorithm"] == "Isolation Forest"

    def test_dashboard_after_analyze(self):
        # Run analysis first
        client.post("/api/analyze", json={
            "session_id": self.session_id,
            "_csv_b64":   self.csv_b64,
        })
        r = client.get("/api/dashboard", params={"session_id": self.session_id})
        assert r.status_code == 200
        data = r.json()
        assert data["total_records"] == 50
        assert "events_detected" in data

    def test_events_list(self):
        client.post("/api/analyze", json={
            "session_id": self.session_id,
            "_csv_b64":   self.csv_b64,
        })
        r = client.get("/api/events", params={"session_id": self.session_id})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_trends(self):
        client.post("/api/analyze", json={
            "session_id": self.session_id,
            "_csv_b64":   self.csv_b64,
        })
        r = client.get("/api/air-quality/trends",
                       params={"session_id": self.session_id, "pollutant": "pm25"})
        assert r.status_code == 200
        data = r.json()
        assert data["pollutant"] == "pm25"
        assert len(data["data"]) == 50

    def test_invalid_pollutant(self):
        r = client.get("/api/air-quality/trends",
                       params={"session_id": self.session_id, "pollutant": "unknown_gas"})
        assert r.status_code == 400


# ── Chatbot ────────────────────────────────────────────────────────────────────

class TestChatbot:
    def test_chat_pm25(self):
        r = client.post("/api/chat", json={"question": "What is PM2.5?"})
        assert r.status_code == 200
        assert "answer" in r.json()
        assert len(r.json()["answer"]) > 10

    def test_chat_default(self):
        r = client.post("/api/chat", json={"question": "What is the meaning of life?"})
        assert r.status_code == 200
        assert "answer" in r.json()


# ── Dashboard 404 for unknown session ─────────────────────────────────────────

class TestErrors:
    def test_dashboard_unknown_session(self):
        r = client.get("/api/dashboard", params={"session_id": "non-existent-session-xyz"})
        assert r.status_code == 404

    def test_event_not_found(self):
        r = client.get("/api/events/99999", params={"session_id": "non-existent-session"})
        assert r.status_code == 404
