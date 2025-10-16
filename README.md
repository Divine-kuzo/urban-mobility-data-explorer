### NYC Taxi Mobility Dashboard

## Overview
The **NYC Taxi Mobility Dashboard** is a web-based application designed to visualize and analyze New York City taxi trip data. The dashboard allows users to explore trip patterns, distances, and passenger counts, through interactive charts, insights, and tabular data.

The application integrates a **frontend** built with HTML, CSS, and JavaScript (Chart.js) and a **backend** powered by Flask and SQLite. The backend provides endpoints to fetch trip data, apply filters, and calculate aggregated statistics.

---

## Features

### Frontend
- Responsive layout with a sidebar for filters and a main content area for charts and tables.
- Interactive charts including:
  - Trips per hour (Bar chart)
- Dynamic insights including:
  - Total trips
  - Average distance and fare
  - Busiest hour
  - Longest and shortest trip
  - Average passengers
- Filter options for:
  - Date range
  - Distance range
  - Passenger count
- Trip data table with sortable columns.

### Backend
- Flask-based REST API serving trip data from SQLite database.
- Endpoints include:
  - `/` – Home route with available routes listed.
  - `/top_dropoffs` – Returns top 10 dropoff locations with average fare and distance.
  - Additional endpoints for highest passengers, shortest trip durations, and vendor information.
- SQLite database schema:
  - **locations**: `location_id`, `latitude`, `longitude`
  - **trips**: `trip_id`, `pickup_datetime`, `dropoff_datetime`, `trip_duration_s`, `trip_distance_km`, `trip_speed_kmph`, `pickup_location_id`, `dropoff_location_id`, `passenger_id`, `payment_id`, `fare_amount`
- Indexes for optimized queries:
  - `idx_trips_pickup_datetime`
  - `idx_trips_dropoff_datetime`
  - `idx_trips_distance`
    
### Data Management
- Data cleaning and preprocessing with Python and Pandas:
  - Timestamp validation
  - Coordinate validation within NYC bounding box
  - Haversine distance calculation
  - Trip duration and speed computation
  - Duplicate detection
  - Exclusion of invalid records
- Sample data insertion script provided to populate the database with demo trips.

---

## Technologies
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Backend**: Python, Flask, SQLite
- **Data Processing**: Python, Pandas, Haversine formula
- **Database**: SQLite with relational schema and indexing

---

## File Structure
```
.
├── app.js # Frontend JavaScript for charts, table, and filters
├── index.html # Frontend HTML layout
├── style.css # Frontend CSS styling
├── backend/
│ ├── app.py # Flask backend application
│ ├── main.py # Additional Flask routes
│ ├── database/
│ │ ├── dump.db # SQLite database file
│ │ └── schema.sql # Database schema definitions
│ └── data-insertion.py # Script to insert demo data
├── data/
│ ├── train.csv # Raw NYC taxi trip dataset
│ ├── cleaned-trips.csv # Cleaned trip dataset
│ └── excluded-trips.csv # Excluded/invalid records
└── README.md 
```
---

## How It Works
1. **Frontend** fetches trip data from backend endpoints.
2. **Filters** can be applied to refine trips by date, distance, and passenger count.
3. **Charts** are dynamically generated using Chart.js based on filtered data.
4. **Insights** are calculated and displayed in real-time.
5. **Database** stores cleaned and structured trip data with proper relationships between trips and locations

---

## Database Schema

### locations
- `location_id` (INTEGER, PRIMARY KEY)
- `latitude` (REAL, NOT NULL)
- `longitude` (REAL, NOT NULL)

### trips
- `trip_id` (INTEGER, PRIMARY KEY)
- `pickup_datetime` (TEXT, NOT NULL)
- `dropoff_datetime` (TEXT, NOT NULL)
- `trip_duration_s` (REAL)
- `trip_distance_km` (REAL)
- `trip_speed_kmph` (REAL)
- `pickup_location_id` (INTEGER, FOREIGN KEY → locations.location_id)
- `dropoff_location_id` (INTEGER, FOREIGN KEY → locations.location_id)

---

## Endpoints

- **Home**: `/` – Returns available routes.
- **Top dropoff locations**: `/top_dropoffs` – Top 10 dropoff locations.
- **Highest passengers**: `/highest_passengers` – Returns rides with highest passenger counts.
- **Shortest trip durations**: `/shortest_trip_duration` – Returns shortest trips.
- **Vendor info**: `/vendor` – Returns vendor information.

---

## Data Cleaning
- Excludes trips with:
  - Invalid timestamps or negative durations
  - Missing or invalid coordinates
  - Duplicate entries
  - Unrealistic speeds (>200 km/h)
- Computes trip distance using Haversine formula.
- Produces separate files for cleaned trips and excluded trips.

---

## Demo Data Insertion
- `data_insertion.py` inserts sample trips into the database for testing.
- Example inserted fields:
  - Passenger count
  - Pickup and dropoff locations
  - Trip datetime, distance, duration, and speed

---
## Installation steps
- Clone the repository:
  - git clone https://github.com/Divine-kuzo/urban-mobility-data-explorer
  - cd urban-mobility-data-explorer

- Install Python (3.10 or higher) from python.org
- Install required Python packages:
  - pip install -r requirements.txt
- Ensure database file is in place (database/dump.db) or run the data insertion script to populate it.
- Make sure Chart.js is available via CDN in the frontend HTML.

---
## Environment setup
- set Up Python Environment
  - Create a virtual environment (recommended):
     python -m venv venv
- Activate the virtual environment:
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
  - Install Python dependencies:
     pip install -r requirements.txt
- Prepare the Database
  - Ensure SQLite database file exists at database/dump.db.
  - Populate demo data (optional but recommended):
     python database/insert_data.py
- Set Up Frontend
  - Frontend files are in the project root (index.html, style.css, app.js).
  - To serve the frontend locally, run:
     python -m http.server 8000
  - Open your browser at http://localhost:8000.
- No Additional Environment Variables Required
All configurations and paths are already set relative to the project structure.

---
### Launching the Application
## 1. Launch Backend (Flask API)
- Ensure your virtual environment is activated.
- Navigate to the backend folder (if applicable).
- Run the Flask app:
# For main backend app
  python app.py
- By default, the backend runs on:
  http://127.0.0.1:5000 (or the port specified in the code).
- API Endpoints available:
  / → Home route, basic status check
  /top_dropoffs → Top dropoff locations
  Additional endpoints from main.py as defined
## 2. Launch Frontend
- Ensure the backend is running.
- Serve the frontend using a local server:
  python -m http.server 8000
- Open your browser at:
  http://localhost:8000
- The frontend connects to the backend to fetch trip data and display charts, tables, and insights.
## 3. Verify Application
- Open the frontend URL in a browser.
- Apply filters using the sidebar to see live updates of charts, tables, and analytics.
- Confirm backend API returns JSON data without errors.

---

## Notes
- Frontend uses Chart.js for dynamic charting.
- SQLite database ensures data integrity through relational constraints and indexes.

---
### Documentation / Report
---
### Video Demonstration
This video demonstrates our NYC Taxi Mobility Dashboard, where we walk through the functionality of the application, including how to filter trips, interpret the interactive charts, and explore key insights derived from the taxi trip data. It provides an overview of how the frontend, backend, and database work together to deliver data analysis experience.
