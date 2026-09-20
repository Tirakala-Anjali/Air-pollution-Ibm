# AirGuard — Viva Preparation
## 1M1B AI for Sustainability Virtual Internship

---

## PART A — Project-Level Questions

---

**Q1. Why did you select air pollution as your problem area?**

Air pollution is one of the most urgent environmental health challenges globally. The WHO estimates that 99% of the world's population breathes air that exceeds WHO guideline limits. It directly affects human health (respiratory disease, cardiovascular problems), quality of life in cities, and is linked to climate change through short-lived climate pollutants like black carbon. It is also a measurable, data-driven problem — making it ideal for an AI solution.

---

**Q2. What is the problem your project solves?**

Air-quality monitoring systems produce continuous sensor data, but manually identifying when pollution is unusually elevated, how long it lasts, and how serious it is, is difficult without automation. AirGuard uses AI anomaly detection to automatically identify unusual pollution patterns, groups them into events, classifies their severity, and presents results in an easy-to-understand web dashboard — making pollution intelligence accessible to non-technical users.

---

**Q3. Why SDG 11?**

SDG 11 — Sustainable Cities and Communities — includes Target 11.6, which specifically aims to reduce the adverse environmental impact of cities with attention to air quality. Urban air pollution is a direct challenge for sustainable city living. AirGuard helps communities monitor and understand local pollution patterns, which supports evidence-based advocacy for cleaner urban environments.

---

**Q4. What are the secondary SDGs and why are they relevant?**

- **SDG 3 (Good Health):** Target 3.9 aims to reduce deaths and illnesses from air pollution. AirGuard raises pollution awareness, which can prompt protective health actions.
- **SDG 13 (Climate Action):** Air pollutants like black carbon and methane are also short-lived climate forcers. Monitoring and reducing them supports both air quality and climate objectives simultaneously.

---

**Q5. Who are the target users of AirGuard?**

Students, citizens, educational institutions, environmental awareness groups, researchers, and local communities. AirGuard is designed as a monitoring and decision-support tool — it is not a replacement for official government air-quality monitoring systems or professional environmental assessments.

---

## PART B — AI / ML Questions

---

**Q6. Why did you use AI instead of simple threshold alerts?**

Simple threshold alerts (e.g., "flag if PM2.5 > 50") have major limitations:
1. They use fixed global thresholds, not the local baseline of the specific location being monitored.
2. They produce many false alerts during normal morning/evening traffic variations.
3. They cannot consider multiple pollutants simultaneously.

AI anomaly detection learns the normal pattern from the actual dataset and flags deviations from *that* specific baseline — making it adaptive and location-aware.

---

**Q7. What is anomaly detection?**

Anomaly detection is a machine learning technique that learns the "normal" pattern in data and identifies observations that significantly deviate from it. Unlike supervised classification (which requires labelled examples of "normal" and "anomalous"), anomaly detection is unsupervised — it learns patterns without any labels. In AirGuard, it identifies air-quality readings that are statistically unusual compared to the rest of the dataset.

---

**Q8. What is Isolation Forest?**

Isolation Forest is an unsupervised anomaly detection algorithm introduced by Liu et al. (2008). It works by:
1. Randomly selecting a feature and a split value
2. Recursively splitting the data until each point is isolated
3. Anomalies, being rare and different, require **fewer splits** to isolate → shorter path length → lower score
4. Normal points are surrounded by similar neighbours → require **more splits** → higher score

The algorithm gives each point an "anomaly score" based on its average path length across many random trees.

---

**Q9. Why Isolation Forest specifically and not another algorithm?**

| Requirement | Why Isolation Forest fits |
|---|---|
| No labelled anomalies | Fully unsupervised |
| Multiple pollutants | Handles high-dimensional data efficiently |
| Continuous severity | Produces a score, not just binary output |
| No distribution assumption | Air quality is not Gaussian |
| Speed | Fast even on thousands of records |
| Interpretability | Contamination parameter is transparent |

Alternative algorithms like Gaussian Mixture Models assume Gaussian distributions, DBSCAN is sensitive to density parameters, and LSTM requires large labelled temporal datasets — all less suitable for this student project context.

---

**Q10. What is an anomaly score in your system?**

In AirGuard, the anomaly score is normalised to a range of **0 to 1**, where:
- **0** = most normal (similar to the majority of observations)
- **1** = most anomalous (very different from the baseline)

The raw Isolation Forest `decision_function` output is linear-scaled to this range for interpretability. It is a *relative* score — it compares observations within the uploaded dataset, not against any external standard.

---

**Q11. What are the features your ML model uses?**

The model uses whichever of these pollutant columns are present in the uploaded CSV:
- PM2.5, PM10, NO₂, CO, SO₂, O₃
- Optionally: temperature, humidity, wind_speed

The system automatically detects available columns and uses only those, so it works even if the dataset has only PM2.5 and PM10.

---

**Q12. What is StandardScaler and why do you use it?**

StandardScaler transforms each feature to have zero mean and unit variance (z-score normalisation). It is used before Isolation Forest because:
1. The features have very different scales (PM2.5 in µg/m³ vs. CO in mg/m³)
2. Without scaling, features with larger values would dominate the random splits
3. After scaling, all features contribute equally to anomaly detection

---

**Q13. What is the contamination parameter?**

Contamination is the expected fraction of anomalies in the dataset (e.g., 0.05 = 5%). The Isolation Forest uses this to set the decision threshold between normal and anomalous. In AirGuard:
- Default: 5% (suitable for most air-quality datasets)
- Range: 1% to 20%
- Higher contamination → more records flagged as anomalies
- The user can adjust this through the upload interface

---

## PART C — Pollution Events

---

**Q14. What is a pollution event in your system?**

A pollution event is a continuous period during which the AI model detects an unusual elevation in one or more pollutants. Instead of treating each anomalous data point separately, AirGuard groups **consecutive anomalous records** (within a configurable time gap) into a single event. Each event has a start time, end time, duration, severity label, peak pollutant values, and an AI-generated explanation.

---

**Q15. How are anomalies grouped into events?**

The event detection algorithm:
1. Sorts all records chronologically
2. Walks through anomalous records in order
3. If the time gap between two consecutive anomalous records is less than `gap_minutes` (default: 60 min), they belong to the same event
4. If the gap exceeds `gap_minutes`, a new event starts
5. Events with fewer than `min_anomalies` records (default: 2) are discarded as noise

This prevents treating single-record sensor glitches as pollution events.

---

**Q16. How is severity calculated?**

Severity is determined by the **higher** of two independent assessments:

**By anomaly score (average for the event):**
- < 0.40 → NORMAL
- 0.40–0.59 → MODERATE
- 0.60–0.79 → HIGH
- ≥ 0.80 → SEVERE

**By peak PM2.5 (WHO-informed, custom thresholds):**
- ≤ 25 µg/m³ → NORMAL
- 26–55 µg/m³ → MODERATE
- 56–150 µg/m³ → HIGH
- > 150 µg/m³ → SEVERE

These are **custom categories** for this system, not official government AQI classifications.

---

## PART D — Data & Technical Questions

---

**Q17. What is PM2.5?**

PM2.5 refers to fine particulate matter with an aerodynamic diameter of 2.5 micrometres or less (about 30 times smaller than a human hair). These particles can penetrate deep into the lungs and enter the bloodstream. Long-term exposure is associated with respiratory disease, cardiovascular problems, and premature mortality. The WHO 24-hour mean guideline for PM2.5 is 15 µg/m³ (2021 guidelines).

---

**Q18. What is PM10?**

PM10 refers to coarse particles with diameters up to 10 micrometres. Sources include road dust, construction, pollen, and mould. PM10 is filtered more effectively than PM2.5 by the upper respiratory tract, but elevated levels can still cause respiratory irritation. The WHO 24-hour mean guideline for PM10 is 45 µg/m³ (2021 guidelines).

---

**Q19. What dataset did you use?**

The project includes a **synthetic demonstration dataset** (`sample_air_quality.csv`) with 96 hourly measurements over 4 days, including normal baseline periods and three artificial pollution spikes. It is explicitly labelled as synthetic data and does not represent real measurements from any location. The system also supports real publicly available datasets such as OpenAQ, CPCB India, US EPA AirNow, and the UCI Air Quality Dataset.

---

**Q20. How do you handle missing data?**

The preprocessing pipeline:
1. Converts invalid non-numeric values to NaN
2. Replaces negative values (impossible for pollutants) with NaN
3. Applies **forward-fill then backward-fill** for up to 3 consecutive missing values
4. Drops rows where **all** pollutant columns are still NaN after filling
5. Reports all steps taken to the user in the analysis result

---

## PART E — Technology Questions

---

**Q21. Why React for the frontend?**

React is the most widely used frontend JavaScript framework, making the project a useful learning exercise. It enables component-based UI design (reusable dashboard cards, charts, tables), declarative state management, and integrates well with Vite for fast development. The component architecture makes the AirGuard UI modular and maintainable.

---

**Q22. Why FastAPI for the backend?**

FastAPI is:
1. **Fast** — one of the fastest Python web frameworks
2. **Modern** — uses Python type hints natively for automatic validation
3. **Auto-documented** — generates interactive API docs (Swagger UI) automatically
4. **Pydantic integration** — request/response validation is built-in
5. **Async-ready** — supports async endpoints for future real-time features
6. Simple and student-friendly compared to Django

---

**Q23. Why SQLite?**

SQLite is:
- Zero-configuration — no separate database server to set up
- Suitable for single-user student projects
- File-based — easy to inspect and reset during development
- The system is designed to switch to PostgreSQL by changing a single environment variable (`DATABASE_URL`)

---

**Q24. How does the frontend communicate with the backend?**

Using the **Axios** HTTP client library in the React frontend. All API calls go through a centralised `api.js` service module. During development, Vite's proxy configuration forwards all `/api/*` requests from `localhost:5173` to the FastAPI backend at `localhost:8000`. In production, a reverse proxy (Nginx) would handle this routing.

---

**Q25. What is CORS and how do you handle it?**

CORS (Cross-Origin Resource Sharing) is a browser security mechanism that blocks frontend JavaScript from making API calls to a different domain unless the server explicitly allows it. In AirGuard:
- FastAPI's `CORSMiddleware` is configured to allow requests from `localhost:5173` (the Vite dev server)
- Allowed origins are stored in the `.env` file, not hard-coded
- In production, the list would be updated to the actual deployed domain

---

## PART F — Responsible AI & Limitations

---

**Q26. What are the limitations of your system?**

1. Cannot identify the exact pollution source from sensor data alone
2. Results are relative to the uploaded dataset, not a universal standard
3. False positives — legitimate readings may be flagged (e.g., weather changes)
4. False negatives — gradual pollution increases may be missed
5. Data quality dependency — faulty sensors → incorrect detections
6. No real-time data feed (manual CSV upload only)
7. Single-location analysis
8. Custom severity labels ≠ official AQI classifications

---

**Q27. Can your system identify the exact source of pollution?**

**No.** AirGuard detects statistical anomalies in concentration data but cannot determine what caused them. The AI explanation explicitly lists possible contributing factors (traffic, industrial activity, construction, weather, etc.) as examples only, with the statement: *"the available sensor data is insufficient to determine the exact pollution source."* Source attribution requires ground-truth investigation (e.g., emissions inventories, meteorological backtrajectory analysis) that goes beyond what this system provides.

---

**Q28. What is Responsible AI and how is it implemented in your project?**

Responsible AI refers to developing and deploying AI systems in ways that are transparent, fair, safe, and beneficial. In AirGuard:
- **Transparency:** Anomaly scores, algorithm, and thresholds are all documented and visible
- **Honesty:** AI never overstates what it knows — "possible factors" not "confirmed causes"
- **Fairness:** No demographic bias — only environmental sensor data is used
- **Privacy:** No personal data collected; session data stays in the browser
- **Human oversight:** Disclaimer on every result page emphasises that results need expert review
- **Limitation acknowledgement:** A dedicated Responsible AI page lists all known limitations

---

**Q29. How can the system be improved in the future?**

1. Real-time IoT integration — automatic data feed instead of CSV upload
2. Live API connections — OpenAQ, CPCB, EPA for current data
3. Geographic maps — visualise pollution spread across multiple locations
4. Advanced ML — LSTM or transformer models for temporal pattern detection
5. Alert system — SMS/email notifications when events are detected
6. Weather integration — temperature, wind speed context for better explanations
7. Validation — compare against official monitoring station data
8. Multi-language support for broader community access

---

**Q30. What did you learn from this project?**

*(Personalise this answer for your viva)*

This project taught me how to:
- Design and build a complete full-stack AI application from scratch
- Apply unsupervised machine learning (Isolation Forest) to a real-world environmental problem
- Connect a React frontend to a FastAPI backend through REST APIs
- Think about Responsible AI — not just model accuracy but transparency and limitations
- Align technology work with the UN Sustainable Development Goals
- Write automated tests for both ML pipelines and API endpoints

Most importantly, I learned that building AI for sustainability means being honest about what the system can and cannot do, and ensuring that it helps rather than misleads the communities it serves.

---

*Prepared for the 1M1B AI for Sustainability Virtual Internship — IBM SkillsBuild × AICTE*
