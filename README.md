# AirGuard — AI-Based Air Pollution Event Detection and Early Warning System

> A full-stack AI sustainability project built for the **1M1B AI for Sustainability Virtual Internship**
> in collaboration with **IBM SkillsBuild** and **AICTE**.

---

## Project Overview

AirGuard analyses time-series air-quality sensor data using an unsupervised **Isolation Forest** anomaly detection model to:

1. Identify unusual pollution patterns in uploaded CSV data
2. Group consecutive anomalous records into discrete **pollution events**
3. Classify each event by **severity** (NORMAL / MODERATE / HIGH / SEVERE)
4. Generate **human-readable AI explanations** for each event
5. Present everything through an **interactive web dashboard**

The system supports SDG 11 (Sustainable Cities), SDG 3 (Good Health), and SDG 13 (Climate Action).

---

## Features

- **CSV Upload** — drag-and-drop CSV upload with data preview
- **AI Analysis** — one-click Isolation Forest anomaly detection
- **Pollution Events** — smart grouping of consecutive anomalies
- **Severity Classification** — transparent, WHO-informed thresholds
- **Interactive Charts** — PM2.5, PM10, NO₂, CO, SO₂, O₃ time-series with anomaly highlights
- **AI Explanations** — plain-language event summaries
- **AI Chatbot** — rule-based sustainability Q&A assistant
- **Awareness Pages** — educational content on air pollution and SDGs
- **Responsible AI** — full transparency about limitations and caveats

---

## Technology Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Frontend   | React 19, Vite 8, Tailwind CSS 4, Recharts 3, Axios, React Router |
| Backend    | Python 3.11, FastAPI, Uvicorn, Pydantic v2      |
| ML         | scikit-learn (Isolation Forest), Pandas, NumPy  |
| Database   | SQLite via SQLAlchemy ORM (PostgreSQL-ready)     |

---

## Architecture

```
React Frontend (Vite, port 5173)
        │
        │  REST API (Axios, /api proxy)
        ▼
FastAPI Backend (Uvicorn, port 8000)
        │
   ┌────┼──────────────┐
   │    │              │
   ▼    ▼              ▼
ML    Database      AI Explanation
(Isolation (SQLite /   (rule-based
 Forest)   SQLAlchemy)  engine)
   │
   ▼
Preprocessing → Anomaly Detection → Event Grouping → Severity
```

---

## Project Structure

```
airguard/
├── frontend/               # React + Vite application
│   ├── src/
│   │   ├── components/     # Sidebar, StatCard, SeverityBadge, etc.
│   │   ├── pages/          # Dashboard, Trends, Events, Upload, Chatbot, etc.
│   │   ├── services/       # api.js (all Axios calls)
│   │   ├── hooks/          # useSession.js
│   │   ├── utils/          # severity helpers
│   │   ├── App.jsx         # Router + Layout
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── main.py         # FastAPI app, CORS, routes
│   │   ├── api/            # upload.py, dashboard.py, events.py, air_quality.py, chatbot.py
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # preprocessing.py, explanation.py
│   │   ├── ml/             # anomaly_detector.py, event_detector.py
│   │   ├── database/       # connection.py (session, Base, create_tables)
│   │   └── utils/          # config.py (pydantic-settings)
│   ├── tests/              # 41 pytest tests
│   ├── requirements.txt
│   └── .env.example
│
├── data/
│   └── sample_air_quality.csv   # Synthetic demo dataset
│
├── docs/
│   ├── project_report.md
│   ├── architecture.md
│   └── presentation.md
│
└── README.md
```

---

## Installation & Setup

### Prerequisites

- Python 3.10+ (project uses 3.11)
- Node.js 18+ and npm
- Git

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd airguard
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at **http://localhost:8000**
Interactive API docs: **http://localhost:8000/docs**

### 3. Frontend Setup

Open a **new terminal window**:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at **http://localhost:5173**

---

## Running the Application

1. Start the **backend** (`uvicorn app.main:app --reload`)
2. Start the **frontend** (`npm run dev`)
3. Open **http://localhost:5173** in your browser
4. Go to **Upload Data** and upload `data/sample_air_quality.csv`
5. Click **Run AI Analysis**
6. Explore the **Dashboard**, **Trends**, and **Events** pages

---

## Dataset Format

### Required Columns

| Column      | Description                         | Example              |
|-------------|-------------------------------------|----------------------|
| `timestamp` | Date and time of measurement        | `2024-01-15 09:00:00`|
| At least one of: `pm25`, `pm10`, `no2`, `co`, `so2`, `o3` | Pollutant concentration | `35.2` |

### Optional Columns

| Column        | Description             | Unit   |
|---------------|-------------------------|--------|
| `pm25`        | Fine particulate matter | µg/m³  |
| `pm10`        | Coarse particulate matter | µg/m³ |
| `no2`         | Nitrogen dioxide        | µg/m³  |
| `co`          | Carbon monoxide         | mg/m³  |
| `so2`         | Sulphur dioxide         | µg/m³  |
| `o3`          | Ozone                   | µg/m³  |
| `temperature` | Air temperature         | °C     |
| `humidity`    | Relative humidity       | %      |
| `wind_speed`  | Wind speed              | m/s    |
| `location`    | Station name            | string |

Column names are case-insensitive and common synonyms are automatically detected (e.g., `PM2.5`, `pm_2_5`, `DateTime`).

### Real Datasets

You can use publicly available datasets such as:
- [OpenAQ](https://openaq.org/) — global open air quality data
- [CPCB India](https://app.cpcbccr.com/AQI_India/) — India AQI data
- [US EPA AirNow](https://www.airnow.gov/) — US air quality data
- [UCI Air Quality Dataset](https://archive.ics.uci.edu/dataset/360/air+quality)

---

## ML Methodology

### Algorithm: Isolation Forest

**Why Isolation Forest?**
- Air-quality datasets typically have no labelled anomalies → supervised models are not applicable
- Isolation Forest is unsupervised and efficient
- It produces a continuous anomaly score (not just binary), enabling severity gradations
- It handles multi-dimensional feature spaces (multiple pollutants simultaneously)
- No distributional assumptions — air-quality data is not Gaussian
- The contamination parameter is transparent and adjustable by the user

**Pipeline:**
1. Column mapping and validation
2. Timestamp parsing and sorting
3. Duplicate removal and missing value imputation
4. Standard scaling (zero mean, unit variance)
5. Isolation Forest training (200 estimators, configurable contamination)
6. Score normalisation to [0, 1] (1 = most anomalous)
7. Consecutive anomaly grouping into events
8. Severity classification (score + PM2.5 thresholds)

---

## API Endpoints

| Method | Endpoint                        | Description                       |
|--------|---------------------------------|-----------------------------------|
| GET    | `/api/health`                   | Health check                      |
| POST   | `/api/upload`                   | Upload and preview CSV            |
| POST   | `/api/analyze`                  | Run AI analysis on uploaded data  |
| GET    | `/api/dashboard?session_id=`    | Dashboard statistics              |
| GET    | `/api/events?session_id=`       | List all pollution events         |
| GET    | `/api/events/{id}?session_id=`  | Single event with AI explanation  |
| GET    | `/api/air-quality?session_id=`  | Paginated air quality records     |
| GET    | `/api/air-quality/trends?session_id=&pollutant=pm25` | Time-series trend data |
| POST   | `/api/chat`                     | Rule-based chatbot                |

Full interactive docs: **http://localhost:8000/docs**

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

Expected output: **41 passed**

---

## Responsible AI

- **Transparency** — anomaly scores and decision thresholds are documented
- **No false causation** — AI explanations never claim a definitive pollution source
- **Custom severity** — labels are NOT official AQI classifications
- **Human oversight** — results should be verified by domain experts
- **Data quality** — results depend on the quality of the uploaded sensor data
- **No PII** — only environmental sensor data is processed

---

## Limitations

- No real-time data feed — manual CSV upload only
- Cannot identify the exact source of a pollution event
- Single-location analysis (multi-location is a future enhancement)
- Severity labels are custom, not equivalent to official government AQI
- Not validated against real-world monitoring stations in this implementation

---

## Future Enhancements

1. Real-time IoT sensor integration
2. Live air-quality API feeds (OpenAQ, CPCB)
3. Geographic pollution maps (Leaflet.js)
4. Weather data integration for context
5. SMS/email alert system
6. Mobile application (React Native)
7. Multi-location comparison dashboard
8. LSTM/deep learning anomaly detection
9. Export reports as PDF
10. Community pollution report submissions

---

## Project Context

| | |
|---|---|
| **Programme** | 1M1B AI for Sustainability Virtual Internship |
| **Partner** | IBM SkillsBuild × AICTE |
| **Primary SDG** | SDG 11 – Sustainable Cities and Communities |
| **Secondary SDGs** | SDG 3 – Good Health · SDG 13 – Climate Action |
| **Project type** | Student educational project |

> **Disclaimer:** AirGuard is a student educational project. Results are AI-generated statistical patterns and do not replace official government air-quality advisories, professional environmental assessments, or medical advice.
