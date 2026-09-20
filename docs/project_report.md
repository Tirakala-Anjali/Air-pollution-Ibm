# AirGuard — Project Report
## 1M1B AI for Sustainability Virtual Internship

---

## 1. Title
**AirGuard: AI-Based Air Pollution Event Detection and Early Warning System**

---

## 2. Student Information
- **Programme:** 1M1B AI for Sustainability Virtual Internship
- **Collaboration:** IBM SkillsBuild × AICTE
- **Domain:** AI/ML · Environmental Sustainability · Full-Stack Web Development

---

## 3. Problem Statement

Air pollution levels can change rapidly due to traffic, industrial activity, construction,
weather conditions, waste burning, and other localised sources. Traditional monitoring
systems provide raw measurements but offer limited automated intelligence for identifying
when and how significant pollution events occur.

Continuously detecting unusual pollution patterns from large sensor datasets manually is
impractical. Communities, schools, and individuals lack accessible tools to understand
pollution anomalies in their local environment.

**AirGuard addresses this gap** by applying AI-based anomaly detection to air-quality
time-series data, grouping anomalous readings into human-understandable pollution events,
and presenting actionable information through an accessible web dashboard.

---

## 4. Target Users

| User Group | How AirGuard Helps |
|---|---|
| Students | Understand AI application in environmental science |
| Citizens | Awareness of local air quality changes |
| Educational institutions | Teaching tool for sustainability and AI |
| Environmental awareness groups | Data analysis without programming knowledge |
| Researchers | Rapid prototyping of pollution event detection |
| Local communities | Community-level environmental monitoring awareness |

AirGuard is a **monitoring and decision-support tool**, not a replacement for official environmental monitoring authorities.

---

## 5. Empathy (Who is Affected?)

Urban and peri-urban populations who:
- Live near industrial zones, highways, or construction sites
- Have limited access to real-time air-quality information
- Cannot interpret raw sensor numbers without context
- Belong to vulnerable groups (children, elderly, respiratory patients)

Pain points:
- Raw AQI numbers without explanation
- No automated detection of when pollution is unusually elevated
- No context about duration, severity, or possible causes

---

## 6. Define

**Core user need:** An accessible way to understand when air quality is significantly worse than normal, how long it lasts, and what pollutants are involved.

**Problem statement (refined):** How might we help communities identify unusual pollution patterns in time-series sensor data without requiring data science expertise?

---

## 7. Ideate

Approaches considered:

| Approach | Pros | Cons |
|---|---|---|
| Threshold alerts (PM2.5 > X) | Simple | No baseline adaptation; too many false alerts |
| Statistical z-score | Simple | Assumes Gaussian distribution; not robust |
| **Isolation Forest (chosen)** | Unsupervised, multi-dimensional, produces continuous score | Requires parameter tuning |
| LSTM deep learning | Can capture temporal patterns | Requires large labelled dataset |
| Autoencoder | Good for time-series anomalies | More complex, harder to explain |

**Isolation Forest was selected** as the best balance of simplicity, effectiveness, and explainability for a student project operating on unlabelled data.

---

## 8. Prototype

**Phase 1:** Folder structure and technology scaffold
**Phase 2:** FastAPI backend with SQLAlchemy and SQLite
**Phase 3:** CSV preprocessing pipeline (column mapping, deduplication, imputation)
**Phase 4:** Isolation Forest anomaly detection with score normalisation
**Phase 5:** Event grouping algorithm with gap-based merging
**Phase 6:** REST API with Pydantic schemas and full error handling
**Phase 7:** React + Vite frontend with Tailwind CSS
**Phase 8:** Axios-based frontend-backend integration
**Phase 9:** Dashboard, trends charts, events table, event detail
**Phase 10:** Rule-based AI explanation engine and chatbot
**Phase 11:** Responsible AI page with transparent limitations

---

## 9. Test & Refine

- **41 automated backend tests** (pytest) covering preprocessing, anomaly detection, event grouping, severity classification, and all API endpoints — all passing
- **Frontend production build** — zero errors
- **End-to-end pipeline verified** with synthetic sample dataset (96 records, 3 severity events detected including 1 SEVERE event with PM2.5 peak = 162.5 µg/m³)

---

## 10. SDG Alignment

### Primary: SDG 11 — Sustainable Cities and Communities
Target 11.6: Reduce the adverse per capita environmental impact of cities, with special attention to air quality.

AirGuard provides a community-accessible tool for understanding pollution patterns in urban environments, supporting evidence-based awareness and advocacy.

### Secondary: SDG 3 — Good Health and Well-being
Target 3.9: Substantially reduce deaths and illnesses from hazardous chemicals and air pollution.

By making pollution event information accessible and understandable, AirGuard supports public health literacy around air pollution.

### Secondary: SDG 13 — Climate Action
Many air pollutants (black carbon, methane, tropospheric ozone) are short-lived climate forcers. Monitoring and reducing them supports both air quality and climate objectives.

---

## 11. AI Solution

### Algorithm
Isolation Forest (scikit-learn) — unsupervised anomaly detection.

### Why Isolation Forest?
1. No labelled anomaly data required (unsupervised)
2. Handles multiple pollutant features simultaneously
3. Produces continuous anomaly score for severity gradation
4. No Gaussian distribution assumption required
5. Computationally efficient on standard hardware

### Pipeline
```
CSV upload → Column mapping → Timestamp parsing → Deduplication →
Missing value imputation → StandardScaler → Isolation Forest (200 trees) →
Score normalisation [0,1] → Consecutive anomaly grouping →
Severity classification → Natural language explanation
```

### Features Used
PM2.5, PM10, NO₂, CO, SO₂, O₃ (whichever are present in uploaded data)

---

## 12. System Architecture

See `architecture.md` for full system architecture diagram.

**Stack summary:**
- Frontend: React 19, Vite 8, Tailwind CSS 4, Recharts 3
- Backend: Python 3.11, FastAPI, SQLAlchemy
- Database: SQLite (PostgreSQL-ready)
- ML: scikit-learn Isolation Forest

---

## 13. Dataset

The project includes a synthetic demonstration dataset (`data/sample_air_quality.csv`) containing:
- 96 hourly measurements across 4 days
- Normal baseline PM2.5: 15–40 µg/m³
- Three pollution spike periods with PM2.5 peaks of 95–162 µg/m³
- All major pollutants: PM2.5, PM10, NO₂, CO, SO₂, O₃
- Meteorological variables: temperature, humidity

**This is explicitly synthetic demo data and does not represent real measurements from any location.**

The system also supports real publicly available datasets (OpenAQ, CPCB, US EPA AirNow, UCI Air Quality Dataset).

---

## 14. Results

With the sample dataset:
- 96 records processed
- 5 anomalous records detected (5.2% anomaly rate)
- 1 SEVERE pollution event detected
  - Duration: ~4 hours
  - Max PM2.5: 162.5 µg/m³
  - Max PM10: 258.8 µg/m³
  - AI explanation generated automatically

Note: These are results from synthetic demo data. Actual results will vary by dataset.

---

## 15. Responsible AI

| Principle | Implementation |
|---|---|
| Transparency | Anomaly scores displayed; algorithm documented |
| Fairness | No demographic data used; location-agnostic |
| Privacy | No PII collected; session data in browser only |
| False positives | Documented; contamination rate adjustable |
| False negatives | Documented as a known limitation |
| Human oversight | Explicit disclaimers on all result pages |
| Source attribution | AI never claims definitive pollution source |
| Health information | General awareness only, not medical advice |

---

## 16. Expected Impact

- Increases public awareness of air pollution events in urban communities
- Makes AI-driven environmental analysis accessible to non-technical users
- Demonstrates practical application of AI for the UN Sustainable Development Goals
- Provides a reusable educational template for AI sustainability projects

---

## 17. Limitations

1. Cannot identify the exact source of a pollution event from sensor data alone
2. Results depend on data quality — faulty sensors produce incorrect detections
3. Anomaly scores are relative to the uploaded dataset, not a universal baseline
4. No real-time data integration (manual CSV upload only)
5. Single-location analysis only
6. Custom severity labels are not official AQI classifications
7. Not validated against official monitoring stations in this implementation

---

## 18. Future Scope

1. Real-time IoT sensor data integration
2. Live air-quality API feeds (OpenAQ, CPCB, EPA)
3. Geographic pollution maps with Leaflet.js
4. Weather data integration for contextual analysis
5. SMS/email alert system for detected events
6. Mobile application (React Native or PWA)
7. Multi-location comparative dashboard
8. Advanced ML: LSTM time-series anomaly detection
9. Export event reports as PDF
10. Community pollution source reporting

---

## 19. Conclusion

AirGuard demonstrates how modern AI and web development techniques can be combined to
address real-world sustainability challenges. The system applies unsupervised machine
learning to detect pollution anomalies, groups them into interpretable events, and
presents results through a professional web interface — making environmental AI
accessible to students, communities, and researchers.

The project supports SDG 11, SDG 3, and SDG 13, and is built with responsible AI
principles including transparency, honesty about limitations, and explicit disclaimers
against misuse.

---

*This report was prepared as part of the 1M1B AI for Sustainability Virtual Internship,
in collaboration with IBM SkillsBuild and AICTE.*
