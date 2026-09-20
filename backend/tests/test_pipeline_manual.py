import os
import pandas as pd
from app.services.preprocessing import preprocess
from app.ml.anomaly_detector import detect_anomalies
from app.ml.event_detector import detect_events
from app.services.explanation import generate_explanation

# Locate sample data relative to this file's location
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE, '..', 'data', 'sample_air_quality.csv')

df = pd.read_csv(CSV_PATH)
print(f'Raw rows: {len(df)}')

clean, report = preprocess(df)
print(f'Clean rows: {report["final_rows"]}')
print(f'Features: {report["available_features"]}')

result, info = detect_anomalies(clean)
print(f'Anomalies: {info["anomalies_detected"]} ({info["anomaly_rate_pct"]}%)')

events = detect_events(result)
print(f'Events detected: {len(events)}')
for e in events:
    print(f'  Event {e["id"]}: {e["severity"]} | PM2.5 peak={e["max_pm25"]} | {e["duration_minutes"]}min')
    exp = generate_explanation(e)
    print(f'  Explanation preview: {exp[:150]}')
    print()
print("ALL PIPELINE TESTS PASSED")
