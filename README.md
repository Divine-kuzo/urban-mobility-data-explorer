### Urban Mobility Data Explorer (NYC Taxi)

Demo video – https://www.youtube.com/watch?v=EkILz0te4W4

## Overview
The Urban Mobility Data Explorer is a web app to visualize and analyze NYC taxi trips. It combines a static frontend (HTML/CSS/JS with Chart.js) and a Flask + SQLite backend API. Users can filter trips, view charts and insights, and browse a paginated table of trips.

---

## Features

### Frontend
- Interactive chart: Trips per hour (Chart.js)
- Live card with most recent trip details
- Filters: date and minimum distance
- Paginated trips table

Note: “Summary Visualizations” and “Key Insights” may take a few seconds to load when working with very large datasets, as the backend performs server-side aggregation/sampling.

### Backend
- Flask REST API backed by SQLite (`database/data.db`)
- Fast, paginated trips endpoint with optional filters
- Aggregated summaries and insights endpoints

---

## Project Structure
```
urban-mobility-data-explorer/
├── backend/
│  ├── app.py                 # Flask API server (entry point)
│  ├── data_processing.py     # Data utilities (optional)
│  └── requirements.txt       # Backend Python dependencies
├── database/
│  ├── data.db                # SQLite database (pre-populated)
│  └── schema.sql             # Schema (reference)
├── frontend/
│  ├── index.html             # UI
│  ├── scripts.js             # Frontend logic (calls the API)
│  └── styles.css             # Styling
├── cleaned_data.csv          # Output of cleaning (reference)
├── excluded_records.csv      # Rejected rows (reference)
├── train.csv                 # Raw sample data (reference)
├── SYSTEM ARCHITECTURE DIAGRAM.jpg
└── README.md
```

---

## Prerequisites
- Python 3.10+ on Windows (PowerShell)
- Recommended: use the provided virtual environment `venv\` or create your own

---

## Quick Start (Windows PowerShell)

### 1) Activate virtual environment and install deps
If you want to use the provided env:
```
./venv/Scripts/Activate.ps1
```
Otherwise, create a new one and install:
```
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r backend/requirements.txt
pip install flask
pip install flask
```
### 2)Since train.csv, cleaned_data.csv, and the database(data_db) were too large to be pushed on github, they were left in the codebase. 
```
Download train.csv from kaggle: https://www.kaggle.com/competitions/nyc-taxi-trip-duration/data?select=train.zip and place it in the root of the repo
run python data_processing.py to get cleaned_data.csv, excluded_data.csv and populate the cleaned data inn database(data_db)
```

### 3) Start the backend API (port 5000)
```
python backend/app.py
```
You should see the server running on `http://localhost:5000`.

Health checks:
- `GET http://localhost:5000/api/test` → simple OK
- `GET http://localhost:5000/` → API welcome message

### 4) Open the index.html file with live server in VScode
LOADING THE DATA MAY TAKE UP TO 5-10 MIMUTES, WAIT PATIENTLY.

## How It Works
1. The frontend calls the API endpoints to fetch trips, a trips-per-hour summary, and insights.
2. The backend executes optimized queries (with sampling where helpful) against `database/data.db`.
3. The UI renders a chart, insights, and a paginated table. Filters (date, min distance) are applied server-side.

---

## API Endpoints
- `GET /` → API welcome message
- `GET /api/test` → Health check
- `GET /api/trips?page=<n>&per_page=<k>&date=YYYY-MM-DD&min_distance=<m>` → Paginated trips
- `GET /api/summary` → Trips-per-hour summary (sampled)
- `GET /api/insights` → Top insights (busiest hours, slowest hours, longest trips)
- `GET /api/stats` → Aggregate stats (totals/averages)
- `GET /api/debug` → DB table counts and DB size

---

## Configuration
- API host/port: change in how you run Flask (default is `localhost:5000`).
- Frontend API target: update `API_BASE_URL` in `frontend/scripts.js` if the backend host/port changes.
- Database location: `database/data.db` (resolved relative to `backend/app.py`).

---

## Troubleshooting
- Backend fails with “Database file not found”: confirm `database/data.db` exists and that `backend/app.py` can resolve `../database/data.db` on your machine.
- Frontend shows CORS/network errors: ensure the backend is running on port 5000 and that you’re serving the frontend via `http://localhost:8000` (not `file://`).
- Empty tables/charts: verify the DB has data via `GET /api/debug` and `GET /api/stats`.

---

## Tech Stack
- Frontend: HTML, CSS, JavaScript, Chart.js
- Backend: Python, Flask, Flask-CORS, SQLite

---

## Demo Video
Demo video placeholder– https://www.youtube.com/watch?v=EkILz0te4W4
