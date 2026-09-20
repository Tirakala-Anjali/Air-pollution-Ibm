# AirGuard — Presentation Slides
## 1M1B AI for Sustainability Virtual Internship

---

## SLIDE 1 — Project Title

**Title:** AirGuard
**Subtitle:** AI-Based Air Pollution Event Detection and Early Warning System

**Visual:** Air quality sensor graphic / city skyline with pollution haze

**Footer:**
- 1M1B AI for Sustainability Virtual Internship
- IBM SkillsBuild × AICTE
- SDG 11 · SDG 3 · SDG 13

---

## SLIDE 2 — Problem Statement

**Title:** The Problem

**Key Points:**
- Air pollution levels change rapidly due to traffic, industry, construction, and weather
- Raw sensor data is difficult to interpret without expertise
- Unusual pollution events are often missed or identified too late
- Communities lack accessible tools to understand local pollution patterns

**Quote / Statistic:**
> 99% of the world's population breathes air that exceeds WHO guideline limits.
> — World Health Organization, 2022

**Visual:** Graph of pollution spikes with no annotations vs. clearly marked events

---

## SLIDE 3 — Who Is Affected?

**Title:** Who Needs This?

| Group | Need |
|---|---|
| 👨‍🎓 Students | Learning about AI and environmental science |
| 🏙️ Urban Citizens | Understanding local air quality |
| 🏫 Schools & Colleges | Environmental awareness education |
| 🌱 Eco Groups | Community-level monitoring |
| 🔬 Researchers | Rapid pollution event analysis |
| 🏡 Local Communities | Early warning for pollution spikes |

**Key Message:** AirGuard is a monitoring and awareness tool — not a replacement for official environmental monitoring.

---

## SLIDE 4 — SDG Alignment

**Title:** Aligning with the UN Sustainable Development Goals

**Primary SDG:**
🏙️ **SDG 11 — Sustainable Cities and Communities**
Target 11.6: Reduce the environmental impact of cities, including air quality

**Secondary SDGs:**
💚 **SDG 3 — Good Health and Well-being**
Target 3.9: Reduce deaths from air pollution

🌍 **SDG 13 — Climate Action**
Air pollutants like black carbon are also short-lived climate forcers

**Visual:** SDG 11, 3, 13 icons with connecting arrows to the AirGuard application

---

## SLIDE 5 — Proposed Solution

**Title:** AirGuard — The Solution

**Three-layer value proposition:**

1. **Detect** — AI identifies unusual pollution patterns automatically
2. **Understand** — Groups anomalies into human-readable pollution events
3. **Act** — Provides severity, duration, and awareness recommendations

**Flow Diagram:**
```
CSV Data → AI Analysis → Pollution Events → Dashboard → Awareness
```

**Key features:**
- No expertise required — just upload a CSV
- Works with any standard air-quality sensor dataset
- Free, open-source, runs on a laptop

---

## SLIDE 6 — AI/ML Methodology

**Title:** The AI Engine — Isolation Forest

**Why Isolation Forest?**
- Unsupervised — no labelled data needed ✓
- Handles multiple pollutants simultaneously ✓
- Produces continuous anomaly score ✓
- No Gaussian distribution assumption ✓
- Efficient on standard hardware ✓

**How it works:**
1. Randomly partition the feature space
2. Anomalies are isolated in fewer steps → lower score
3. Normal points require many steps → higher score
4. Scores normalised to [0, 1] for interpretability

**Event Detection:**
Consecutive anomalous records → grouped into events → severity classified

---

## SLIDE 7 — Full-Stack Architecture

**Title:** Technical Architecture

```
React Frontend (Vite + Tailwind)
           │
    REST API (Axios)
           │
    FastAPI Backend
    ┌──────┼───────┐
    │      │       │
   ML   Database  Explanation
(Isolation (SQLite)  (Rule-based)
  Forest)
```

**Tech Stack:**
- **Frontend:** React 19 · Vite · Tailwind CSS · Recharts
- **Backend:** Python · FastAPI · Pydantic · SQLAlchemy
- **ML:** scikit-learn · Pandas · NumPy
- **DB:** SQLite (PostgreSQL-ready)

---

## SLIDE 8 — Frontend / Dashboard

**Title:** The Dashboard — Making Data Understandable

**Dashboard cards:**
- Total Records | Events Detected | Anomaly Rate | Current Status
- Highest PM2.5 | Highest PM10 | Average PM2.5 | High Severity Events

**Key UI features:**
- Interactive PM2.5/PM10/NO₂ time-series charts
- Anomaly points highlighted in red on charts
- Sortable and filterable events table
- Event detail page with AI explanation
- AI chatbot for sustainability Q&A
- Environmental Awareness educational page

**Visual:** Screenshot of dashboard / mockup

---

## SLIDE 9 — Results and Detected Events

**Title:** Results — Sample Dataset Analysis

**Input:** 96 hourly measurements (synthetic demo data, 4 days)

**AI Output:**
| Metric | Value |
|---|---|
| Records processed | 96 |
| Anomalies detected | 5 (5.2%) |
| Pollution events | 1 SEVERE event |
| Event duration | ~4 hours |
| Peak PM2.5 | 162.5 µg/m³ |
| Peak PM10 | 258.8 µg/m³ |

**Sample AI Explanation (excerpt):**
> "The AI anomaly detection system identified an unusual pattern spanning approximately 4 hours (5 anomalous observations). PM2.5 peaked at 162.5 µg/m³, PM10 peaked at 258.8 µg/m³..."

**Note:** Results are from synthetic demo data. Real results depend on the uploaded dataset.

---

## SLIDE 10 — Responsible AI

**Title:** Responsible AI — Transparency First

**Commitments:**

| Principle | What We Do |
|---|---|
| Transparency | Anomaly scores visible; algorithm explained |
| No false causation | Never claims a definitive pollution source |
| Custom severity | Not official AQI — clearly labelled |
| Human oversight | Explicit disclaimers on every result page |
| Privacy | No personal data; session-only storage |
| Data quality | Preprocessing steps reported to user |
| Limitations | Fully documented — false positives acknowledged |

**Disclaimer shown in the app:**
> "AirGuard results are AI-generated statistical patterns and do not replace official government air-quality advisories."

---

## SLIDE 11 — Expected Impact

**Title:** Expected Impact

**Direct impact:**
- Makes AI-driven pollution analysis accessible to non-technical users
- Raises community awareness of air pollution events
- Supports environmental education in schools and colleges

**Indirect impact:**
- Encourages data-driven environmental advocacy
- Demonstrates practical AI application for the SDGs
- Template for future real-time community monitoring tools

**Scale potential:**
- Deployable in any city with basic sensor data
- Open-source and extensible
- Designed to work on a standard laptop or low-cost server

---

## SLIDE 12 — Future Scope & Conclusion

**Title:** What's Next + Key Takeaways

**Future Enhancements:**
1. Real-time IoT sensor integration
2. Live API feeds (OpenAQ, CPCB, EPA)
3. Geographic pollution maps
4. SMS/email alerts for detected events
5. Mobile application
6. LSTM deep learning model
7. Multi-location comparison

**Key Takeaways:**
✅ Full-stack AI sustainability project — frontend + backend + ML
✅ 41 automated tests — all passing
✅ Responsible AI principles throughout
✅ Aligned with SDG 11, SDG 3, SDG 13
✅ Accessible to non-technical users
✅ Runs entirely on a laptop

**Closing:**
> "AirGuard shows that AI can make environmental data accessible, understandable, and actionable — putting sustainability intelligence in the hands of every community."

---

*Prepared for the 1M1B AI for Sustainability Virtual Internship — IBM SkillsBuild × AICTE*
