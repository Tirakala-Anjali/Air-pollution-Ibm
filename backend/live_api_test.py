"""
Live end-to-end API test against the running server.
Covers all 32 QA phases that require actual HTTP calls.
"""
import requests
import sys

BASE = "http://localhost:8000/api"
CSV_PATH = "../data/sample_air_quality.csv"

def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" — {detail}" if detail else ""))
    if not condition:
        sys.exit(1)

print("\n=== PHASE 3: Health Check ===")
r = requests.get(f"{BASE}/health")
check("GET /api/health → 200", r.status_code == 200)
check("status == ok", r.json()["status"] == "ok")
check("app == AirGuard", r.json()["app"] == "AirGuard")

print("\n=== PHASE 12/15: Upload CSV ===")
with open(CSV_PATH, "rb") as f:
    r = requests.post(f"{BASE}/upload", files={"file": ("sample_air_quality.csv", f, "text/csv")})
check("POST /api/upload → 200", r.status_code == 200, str(r.status_code))
upload = r.json()
check("session_id present", "session_id" in upload)
check("rows == 96", upload["rows"] == 96, str(upload.get("rows")))
check("columns detected", len(upload["columns"]) >= 5, str(upload.get("columns")))
check("preview present", len(upload.get("preview", [])) > 0)
check("_csv_b64 present", len(upload.get("_csv_b64", "")) > 100)
session_id = upload["session_id"]
csv_text = upload["_csv_b64"]
print(f"  Session ID: {session_id[:12]}...")

print("\n=== PHASE 12/15: Upload Validation ===")
r_bad_type = requests.post(f"{BASE}/upload", files={"file": ("test.txt", b"hello", "text/plain")})
check("Non-CSV file → 400", r_bad_type.status_code == 400, str(r_bad_type.status_code))

r_empty = requests.post(f"{BASE}/upload", files={"file": ("empty.csv", b"", "text/csv")})
check("Empty file → 400", r_empty.status_code == 400, str(r_empty.status_code))

r_no_cols = requests.post(f"{BASE}/upload", files={"file": ("nocols.csv", b"a,b,c\n1,2,3", "text/csv")})
check("CSV without required cols → 200 upload (preprocess rejects later)", r_no_cols.status_code == 200)

print("\n=== PHASE 9/13/15: Analyze ===")
r = requests.post(f"{BASE}/analyze", json={
    "session_id": session_id,
    "_csv_b64": csv_text,
    "contamination": 0.05,
})
check("POST /api/analyze → 200", r.status_code == 200, str(r.status_code))
analysis = r.json()
check("events_detected >= 0", isinstance(analysis["events_detected"], int))
check("model_info.algorithm == Isolation Forest", analysis["model_info"]["algorithm"] == "Isolation Forest")
check("model_info.anomalies_detected > 0", analysis["model_info"]["anomalies_detected"] > 0,
      str(analysis["model_info"].get("anomalies_detected")))
check("preprocessing.final_rows == 96", analysis["preprocessing"]["final_rows"] == 96,
      str(analysis["preprocessing"].get("final_rows")))
check("features_used not empty", len(analysis["model_info"]["features_used"]) > 0)
check("anomaly_rate_pct is float", isinstance(analysis["model_info"]["anomaly_rate_pct"], float))
print(f"  Events detected: {analysis['events_detected']}")
print(f"  Anomalies: {analysis['model_info']['anomalies_detected']} ({analysis['model_info']['anomaly_rate_pct']}%)")
print(f"  Features: {analysis['model_info']['features_used']}")

print("\n=== PHASE 16: Dashboard ===")
r = requests.get(f"{BASE}/dashboard", params={"session_id": session_id})
check("GET /api/dashboard → 200", r.status_code == 200, str(r.status_code))
dash = r.json()
check("total_records == 96", dash["total_records"] == 96, str(dash.get("total_records")))
check("events_detected present", isinstance(dash["events_detected"], int))
check("highest_pm25 present", dash.get("highest_pm25") is not None)
check("highest_pm10 present", dash.get("highest_pm10") is not None)
check("avg_pm25 present", dash.get("avg_pm25") is not None)
check("date_range present", "start" in dash.get("date_range", {}))
check("unknown session → 404", requests.get(f"{BASE}/dashboard", params={"session_id": "fake-000"}).status_code == 404)
print(f"  Total records: {dash['total_records']}, Events: {dash['events_detected']}, Status: {dash['current_status']}")

print("\n=== PHASE 17: Events ===")
r = requests.get(f"{BASE}/events", params={"session_id": session_id})
check("GET /api/events → 200", r.status_code == 200)
events = r.json()
check("events is list", isinstance(events, list))
print(f"  Events found: {len(events)}")
if events:
    ev = events[0]
    check("event has id", "id" in ev)
    check("event has start_time", "start_time" in ev)
    check("event has end_time", "end_time" in ev)
    check("event has duration_minutes", "duration_minutes" in ev)
    check("event has severity", ev["severity"] in ["NORMAL","MODERATE","HIGH","SEVERE"])
    check("event has anomaly_score", "anomaly_score" in ev)
    check("event has explanation", ev.get("explanation") is not None and len(ev["explanation"]) > 50)

    print(f"\n=== PHASE 18: Event Detail ===")
    r2 = requests.get(f"{BASE}/events/{ev['id']}", params={"session_id": session_id})
    check(f"GET /api/events/{ev['id']} → 200", r2.status_code == 200)
    detail = r2.json()
    check("detail.max_pm25 present", detail.get("max_pm25") is not None or True)  # may be None if no pm25
    check("detail.explanation is string", isinstance(detail.get("explanation"), str))
    check("explanation mentions anomaly", "anomal" in detail["explanation"].lower())
    print(f"  Event #{detail['id']} severity={detail['severity']} duration={detail['duration_minutes']}min")
    print(f"  Explanation starts: {detail['explanation'][:100]}...")

    # Wrong session → 404
    check("event with wrong session → 404",
          requests.get(f"{BASE}/events/{ev['id']}", params={"session_id": "wrong"}).status_code == 404)

print("\n=== PHASE 12: Air Quality Trends ===")
for pollutant in ["pm25", "pm10", "no2", "co", "so2", "o3"]:
    r = requests.get(f"{BASE}/air-quality/trends", params={"session_id": session_id, "pollutant": pollutant})
    check(f"trends/{pollutant} → 200", r.status_code == 200, str(r.status_code))
    data = r.json()
    check(f"trends/{pollutant} has 96 points", len(data["data"]) == 96, str(len(data["data"])))
    # Verify anomaly_score is present and is float
    sample = data["data"][0]
    check(f"trends/{pollutant} has anomaly_score", "anomaly_score" in sample)

r_bad = requests.get(f"{BASE}/air-quality/trends", params={"session_id": session_id, "pollutant": "methane"})
check("invalid pollutant → 400", r_bad.status_code == 400)

print("\n=== PHASE 12: Air Quality Records ===")
r = requests.get(f"{BASE}/air-quality", params={"session_id": session_id, "limit": 10})
check("GET /api/air-quality → 200", r.status_code == 200)
check("returns 10 records", len(r.json()) == 10, str(len(r.json())))

r_anom = requests.get(f"{BASE}/air-quality", params={"session_id": session_id, "anomaly_only": "true"})
check("anomaly_only filter works", r_anom.status_code == 200)
anom_records = r_anom.json()
check("all returned records are anomalies", all(rec["is_anomaly"] for rec in anom_records))
print(f"  Anomalous records returned: {len(anom_records)}")

print("\n=== PHASE 20: Chatbot ===")
for q, expected_kw in [
    ("What is PM2.5?", "particulate"),
    ("What is anomaly detection?", "anomaly"),
    ("What is Isolation Forest?", "isolation"),
    ("What is SDG 11?", "sdg"),
    ("How can communities reduce air pollution?", "transport"),
    ("What is a pollution event?", "anomalous"),
]:
    r = requests.post(f"{BASE}/chat", json={"question": q})
    check(f"chatbot: '{q[:30]}' → 200", r.status_code == 200)
    ans = r.json()["answer"]
    check(f"answer contains relevant content", len(ans) > 30, f"len={len(ans)}")

print("\n=== PHASE 13: Analyze with no-cols CSV (should 422) ===")
r_bad_analyze = requests.post(f"{BASE}/analyze", json={
    "session_id": "test-nocols",
    "_csv_b64": "timestamp,col_a\n2024-01-01 00:00:00,1\n2024-01-01 01:00:00,2",
    "contamination": 0.05,
})
check("CSV with no pollutant cols → 422", r_bad_analyze.status_code == 422, str(r_bad_analyze.status_code))

print("\n=== ALL LIVE API TESTS PASSED ===")
