-- Table: locations
-- Stores unique pickup and dropoff coordinates
CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    UNIQUE(latitude, longitude)
);

-- Table: trips
-- Stores valid cleaned trip records
CREATE TABLE IF NOT EXISTS trips (
    trip_id TEXT PRIMARY KEY,                  -- matches 'id' from dataset
    vendor_id INTEGER,
    pickup_datetime TEXT NOT NULL,
    dropoff_datetime TEXT NOT NULL,
    pickup_location_id INTEGER NOT NULL,
    dropoff_location_id INTEGER NOT NULL,
    passenger_count INTEGER,
    store_and_fwd_flag TEXT CHECK(store_and_fwd_flag IN ('Y','N')),
    trip_duration_s REAL,
    trip_distance_km REAL,                     -- derived field
    trip_speed_kmph REAL,                      -- derived field
    FOREIGN KEY (pickup_location_id) REFERENCES locations(location_id),
    FOREIGN KEY (dropoff_location_id) REFERENCES locations(location_id)
);

-- Table: excluded_trips
-- Logs invalid or excluded trip records
CREATE TABLE IF NOT EXISTS excluded_trips (
    excluded_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id TEXT,
    vendor_id INTEGER,
    pickup_datetime TEXT,
    dropoff_datetime TEXT,
    pickup_latitude REAL,
    pickup_longitude REAL,
    dropoff_latitude REAL,
    dropoff_longitude REAL,
    passenger_count INTEGER,
    store_and_fwd_flag TEXT,
    trip_duration_s REAL,
    reason TEXT
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_trips_pickup_datetime 
    ON trips (pickup_datetime);

CREATE INDEX IF NOT EXISTS idx_trips_dropoff_datetime 
    ON trips (dropoff_datetime);

CREATE INDEX IF NOT EXISTS idx_trips_pickup_location 
    ON trips (pickup_location_id);

CREATE INDEX IF NOT EXISTS idx_trips_dropoff_location 
    ON trips (dropoff_location_id);
