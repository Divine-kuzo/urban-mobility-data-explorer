### NYC Taxi Mobility Dashboard

## Overview
The **NYC Taxi Mobility Dashboard** is a web-based application designed to visualize and analyze New York City taxi trip data. The dashboard allows users to explore trip patterns, fares, distances, passenger counts, and payment types through interactive charts, insights, and tabular data.

The application integrates a **frontend** built with HTML, CSS, and JavaScript (Chart.js) and a **backend** powered by Flask and SQLite. The backend provides endpoints to fetch trip data, apply filters, and calculate aggregated statistics.

---

## Features

### Frontend
- Responsive layout with a sidebar for filters and a main content area for charts and tables.
- Interactive charts including:
  - Trips per hour (Bar chart)
  - Fare vs Distance (Scatter chart)
  - Payment Type Distribution (Pie chart)
- Dynamic insights including:
  - Total trips
  - Average distance and fare
  - Busiest hour
  - Longest and shortest trip
  - Highest fare
  - Average passengers
  - Payment distribution percentages
- Filter options for:
  - Date range
  - Distance range
  - Fare range
  - Passenger count
  - Payment type
- Trip data table with sortable columns.

### Backend
- Flask-based REST API serving trip data from SQLite database.
- Endpoints include:
  - `/` – Home route with available routes listed.
  - `/avg_fare_by_hour` – Returns average fare per hour with trip counts.
  - `/top_dropoffs` – Returns top 10 dropoff locations with average fare and distance.
  - Additional endpoints for highest passengers, shortest trip durations, and vendor information.
- SQLite database schema:
  - **locations**: `location_id`, `latitude`, `longitude`
  - **trips**: `trip_id`, `pickup_datetime`, `dropoff_datetime`, `trip_duration_s`, `trip_distance_km`, `trip_speed_kmph`, `pickup_location_id`, `dropoff_location_id`, `passenger_id`, `payment_id`, `fare_amount`
- Indexes for optimized queries:
  - `idx_trips_pickup_datetime`
  - `idx_trips_dropoff_datetime`
  - `idx_trips_distance`
  - `idx_payments_trip`

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
2. **Filters** can be applied to refine trips by date, distance, fare, passenger count, and payment type.
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
- `payment_count` (INTEGER)

---

## Endpoints

- **Home**: `/` – Returns available routes.
- **Average fare by hour**: `/avg_fare_by_hour` – Aggregated trip count and average fare per hour.
- **Top dropoff locations**: `/top_dropoffs` – Top 10 dropoff locations sorted by average fare.
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
  - Payment type and fare
  - Trip datetime, distance, duration, and speed

---

## Notes
- Backend is implemented in Flask, running on `127.0.0.1` ports 5000.
- Frontend uses Chart.js for dynamic charting.
- SQLite database ensures data integrity through relational constraints and indexes.

