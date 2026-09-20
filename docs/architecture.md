# AirGuard — System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                            │
│                                                                 │
│  ┌───────────┐  ┌───────────┐  ┌──────────┐  ┌─────────────┐  │
│  │ Dashboard │  │  Trends   │  │  Events  │  │  Upload UI  │  │
│  └─────┬─────┘  └─────┬─────┘  └────┬─────┘  └──────┬──────┘  │
│        └──────────────┴─────────────┴────────────────┘         │
│                              │                                  │
│              React + Vite (port 5173)                           │
│              Tailwind CSS · Recharts · React Router             │
└──────────────────────────┬──────────────────────────────────────┘
                           │  HTTP REST (Axios)
                           │  /api/* proxy → localhost:8000
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI BACKEND                            │
│                    (Uvicorn, port 8000)                         │
│                                                                 │
│  POST /api/upload      POST /api/analyze    GET /api/dashboard  │
│  GET  /api/events      GET  /api/events/{id}                    │
│  GET  /api/air-quality GET  /api/air-quality/trends             │
│  POST /api/chat        GET  /api/health                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  SERVICE LAYER                           │   │
│  │                                                          │   │
│  │  preprocessing.py          explanation.py               │   │
│  │  ├─ Column mapping          ├─ Rule-based AI text        │   │
│  │  ├─ Timestamp parsing       └─ Chatbot responses         │   │
│  │  ├─ Deduplication                                        │   │
│  │  ├─ Missing value fill                                   │   │
│  │  └─ Negative value guard                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   ML LAYER                               │   │
│  │                                                          │   │
│  │  anomaly_detector.py       event_detector.py             │   │
│  │  ├─ StandardScaler          ├─ Gap-based grouping         │   │
│  │  ├─ Isolation Forest        ├─ Duration calculation       │   │
│  │  ├─ Score normalisation     ├─ Peak pollutant stats       │   │
│  │  └─ is_anomaly flag         └─ Severity classification    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  DATABASE LAYER                          │   │
│  │                                                          │   │
│  │  SQLite (airguard.db) via SQLAlchemy ORM                 │   │
│  │                                                          │   │
│  │  air_quality_records          pollution_events           │   │
│  │  ├─ id, session_id            ├─ id, session_id          │   │
│  │  ├─ timestamp, location       ├─ start_time, end_time    │   │
│  │  ├─ pm25, pm10, no2, co       ├─ duration_minutes        │   │
│  │  ├─ so2, o3                   ├─ severity                │   │
│  │  ├─ temperature, humidity     ├─ max_pm25, max_pm10      │   │
│  │  ├─ wind_speed                ├─ anomaly_score           │   │
│  │  ├─ anomaly_score             ├─ anomaly_count           │   │
│  │  └─ is_anomaly                └─ explanation (text)      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User uploads CSV
      │
      ▼
POST /api/upload
  → validate file type and size
  → parse CSV with pandas
  → return session_id + preview
      │
      ▼
POST /api/analyze  (user clicks "Run AI Analysis")
  → preprocessing service
      ├─ map column synonyms
      ├─ parse timestamps
      ├─ remove duplicates
      ├─ fill missing values
      └─ reject invalid data
  → anomaly_detector
      ├─ select available features
      ├─ StandardScaler
      ├─ Isolation Forest (200 trees)
      ├─ predict (+1 / -1)
      └─ normalise scores → [0,1]
  → event_detector
      ├─ sort by timestamp
      ├─ group consecutive anomalies
      ├─ apply gap threshold (60 min)
      ├─ apply min_anomalies filter (2)
      └─ compute peak/avg statistics
  → explanation generator
      └─ build natural-language explanation paragraphs
  → SQLAlchemy bulk insert
      ├─ air_quality_records (one row per measurement)
      └─ pollution_events (one row per event)
  → return summary JSON
      │
      ▼
React dashboard fetches:
  GET /api/dashboard   → summary statistics
  GET /api/events      → events table
  GET /api/air-quality/trends?pollutant=pm25 → chart data
  GET /api/events/{id} → event detail + explanation
```

## Session Management

Each CSV upload creates a unique `session_id` (UUID v4).  
This ID is stored in the browser's `sessionStorage` and sent as a query
parameter with every subsequent GET request.  
This allows multiple independent analysis sessions without user accounts.

## Database Schema

### `air_quality_records`
```sql
id            INTEGER PRIMARY KEY
session_id    VARCHAR(64)   -- ties rows to an upload session
timestamp     DATETIME
location      VARCHAR(128)
pm25          FLOAT
pm10          FLOAT
no2           FLOAT
co            FLOAT
so2           FLOAT
o3            FLOAT
temperature   FLOAT
humidity      FLOAT
wind_speed    FLOAT
anomaly_score FLOAT         -- normalised [0,1]
is_anomaly    BOOLEAN
created_at    DATETIME
```

### `pollution_events`
```sql
id               INTEGER PRIMARY KEY
session_id       VARCHAR(64)
start_time       DATETIME
end_time         DATETIME
duration_minutes FLOAT
severity         VARCHAR(16)  -- NORMAL|MODERATE|HIGH|SEVERE
max_pm25         FLOAT
max_pm10         FLOAT
max_no2          FLOAT
max_co           FLOAT
avg_pm25         FLOAT
avg_pm10         FLOAT
anomaly_score    FLOAT        -- mean of event's anomaly scores
anomaly_count    INTEGER
explanation      TEXT
created_at       DATETIME
```

## Migrating to PostgreSQL

Change the single environment variable:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/airguard
```

Remove `connect_args={"check_same_thread": False}` from `connection.py`
and install `psycopg2-binary`. No other code changes are needed.

## Security Measures

| Concern              | Mitigation                                              |
|----------------------|---------------------------------------------------------|
| File type            | `.csv` extension check + pandas parse validation        |
| File size            | 10 MB limit enforced before reading content            |
| Input validation     | Pydantic schemas on all request/response models        |
| CORS                 | Explicit origin whitelist in `settings.CORS_ORIGINS`   |
| Secrets              | All keys in `.env`, never in code or frontend          |
| Code execution       | Uploaded files are never executed, only parsed          |
| Injection            | SQLAlchemy ORM parameterises all queries               |
