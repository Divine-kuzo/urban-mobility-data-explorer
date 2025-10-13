CREATE TABLE passengers (
    passenger_id INTEGER PRIMARY KEY,
    passenger_count INTEGER NOT NULL CHECK (passenger_count > 0)
);
CREATE TABLE locations (
    location_id INTEGER PRIMARY KEY,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL
);
CREATE TABLE trips (
    trip_id INTEGER PRIMARY KEY,
    pickup_datetime TEXT NOT NULL,   -- ISO-8601 string (YYYY-MM-DD HH:MM:SS)
    dropoff_datetime TEXT NOT NULL,  -- ISO-8601 string
    trip_duration_s REAL,
    trip_distance_km REAL,
    trip_speed_kmph REAL,
    pickup_location_id INTEGER NOT NULL,
    dropoff_location_id INTEGER NOT NULL,
    passenger_id INTEGER NOT NULL,
    payment_id INTEGER NOT NULL, fare_amount REAL,

    FOREIGN KEY (pickup_location_id) REFERENCES locations(location_id),
    FOREIGN KEY (dropoff_location_id) REFERENCES locations(location_id),
    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id),
    FOREIGN KEY (payment_id) REFERENCES "payments"(payment_id)
);
CREATE INDEX idx_trips_pickup_datetime ON trips(pickup_datetime);
CREATE INDEX idx_trips_dropoff_datetime ON trips(dropoff_datetime);
CREATE INDEX idx_trips_distance ON trips(trip_distance_km);
CREATE TABLE IF NOT EXISTS "payments" (
    payment_id INTEGER PRIMARY KEY,
    payment_type TEXT,
    fare_amount REAL,
    trip_id INTEGER,
    FOREIGN KEY(trip_id) REFERENCES trips(trip_id)
);
CREATE INDEX idx_trips_pickup ON trips(pickup_datetime);
CREATE INDEX idx_payments_trip ON payments(trip_id);
