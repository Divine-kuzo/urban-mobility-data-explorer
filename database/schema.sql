-- SQLite schema for Urban Mobility Explorer

CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY,
    latitude REAL,
    longitude REAL
);

CREATE TABLE trips (
    trip_id TEXT PRIMARY KEY,
    vendor_id INTEGER,
    pickup_datetime TEXT,
    dropoff_datetime TEXT,
    passenger_count INTEGER,
    trip_distance REAL,
    pickup_location_id INTEGER,
    dropoff_location_id INTEGER,
    store_and_fwd_flag TEXT,
    FOREIGN KEY (pickup_location_id) REFERENCES locations(location_id),
    FOREIGN KEY (dropoff_location_id) REFERENCES locations(location_id)
);

CREATE TABLE derived_metrics (
    trip_id TEXT PRIMARY KEY,
    trip_duration_min REAL,
    speed_mph REAL,
    FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
);

CREATE INDEX idx_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX idx_trip_distance ON trips(trip_distance);