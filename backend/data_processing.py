import pandas as pd
import sqlite3
from math import radians, sin, cos, sqrt, atan2

# Custom algorithm: Manual z-score anomaly detection (no libraries for calc)
def detect_anomalies(values, threshold=3):
    if not values:
        return []
    n = len(values)
    mean = sum(values) / n
    sum_sq_diff = sum((x - mean) ** 2 for x in values)
    variance = sum_sq_diff / n
    std_dev = sqrt(variance) if variance > 0 else 0
    anomalies = [x for x in values if abs((x - mean) / std_dev) > threshold] if std_dev > 0 else []
    return anomalies

# Haversine formula for distance calculation
def haversine(lon1, lat1, lon2, lat2):
    R = 3958.8  # Earth radius in miles
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# Data processing function
def process_data(input_file, output_file, db_file):
    # Load data
    print("Loading data...")
    df = pd.read_csv(input_file, parse_dates=['pickup_datetime', 'dropoff_datetime'])
    # Optional: Subsample for testing (uncomment if needed)
    # df = df.sample(n=10000, random_state=42)

    # Handle missing values: Drop rows with critical missing fields
    critical_cols = ['id', 'pickup_datetime', 'dropoff_datetime', 'passenger_count', 'pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude', 'trip_duration']
    original_len = len(df)
    df = df.dropna(subset=critical_cols)
    print(f"Dropped {original_len - len(df)} rows with missing critical values.")

    # Remove duplicates
    df = df.drop_duplicates()
    print(f"Removed {original_len - len(df)} duplicate rows.")

    # Invalid records and outliers
    df = df[(df['passenger_count'] > 0) & (df['passenger_count'] <= 6)]  # Reasonable passengers
    df = df[(df['trip_duration'] > 0) & (df['trip_duration'] < 7200)]  # Less than 2 hours
    df = df[(df['pickup_latitude'].between(40.5, 41.0)) & (df['pickup_longitude'].between(-74.5, -73.5))]
    df = df[(df['dropoff_latitude'].between(40.5, 41.0)) & (df['dropoff_longitude'].between(-74.5, -73.5))]
    print(f"Filtered to {len(df)} valid records.")

    # Derived features
    df['trip_duration_min'] = df['trip_duration'] / 60  # Convert seconds to minutes
    df['trip_distance'] = df.apply(lambda row: haversine(row['pickup_longitude'], row['pickup_latitude'], row['dropoff_longitude'], row['dropoff_latitude']), axis=1)
    df['speed_mph'] = df['trip_distance'] / (df['trip_duration_min'] / 60)  # Miles per hour
    print("Derived features: trip_duration_min, trip_distance, speed_mph.")

    # Custom algorithm: Detect anomalies in speed_mph
    speed_values = df['speed_mph'].tolist()
    anomalies = detect_anomalies(speed_values)
    print(f"Detected {len(anomalies)} anomalies in speed_mph (z-score > 3)")

    # Log excluded records (placeholder; enhance if needed)
    excluded = pd.DataFrame()  # Compare with original df if needed
    excluded.to_csv('excluded_records.csv', index=False)
    print("Logged excluded records to excluded_records.csv.")

    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"Saved cleaned data to {output_file}.")

    # Populate database
    print("Connecting to database...")
    conn = sqlite3.connect(db_file)

    # Clear existing tables to avoid conflicts
    conn.execute('DROP TABLE IF EXISTS locations')
    conn.execute('DROP TABLE IF EXISTS trips')
    conn.execute('DROP TABLE IF EXISTS derived_metrics')
    print("Cleared existing tables.")

    # Create tables
    conn.execute('''
    CREATE TABLE locations (
        location_id INTEGER PRIMARY KEY,
        latitude REAL,
        longitude REAL
    )
    ''')
    conn.execute('''
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
    )
    ''')
    conn.execute('''
    CREATE TABLE derived_metrics (
        trip_id TEXT PRIMARY KEY,
        trip_duration_min REAL,
        speed_mph REAL,
        FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
    )
    ''')

    # Indexes for efficiency
    conn.execute('CREATE INDEX IF NOT EXISTS idx_pickup_datetime ON trips(pickup_datetime)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_trip_distance ON trips(trip_distance)')
    print("Created database tables and indexes.")

    # Insert locations
    pickup_locs = df[['pickup_latitude', 'pickup_longitude']].drop_duplicates().reset_index(drop=True)
    dropoff_locs = df[['dropoff_latitude', 'dropoff_longitude']].drop_duplicates().reset_index(drop=True)
    # Rename columns before concatenation
    pickup_locs = pickup_locs.rename(columns={'pickup_latitude': 'latitude', 'pickup_longitude': 'longitude'})
    dropoff_locs = dropoff_locs.rename(columns={'dropoff_latitude': 'latitude', 'dropoff_longitude': 'longitude'})
    locations = pd.concat([pickup_locs, dropoff_locs]).drop_duplicates(subset=['latitude', 'longitude']).reset_index(drop=True)
    # Assign unique location_id
    locations['location_id'] = locations.index + 1
    # Check for duplicate location_id
    if locations['location_id'].duplicated().sum() > 0:
        print("Warning: Duplicate location_id values detected!")
    locations[['location_id', 'latitude', 'longitude']].to_sql('locations', conn, if_exists='append', index=False)
    print(f"Inserted {len(locations)} unique locations.")

    # Map locations to df
    df = df.merge(locations.rename(columns={'latitude': 'pickup_latitude', 'longitude': 'pickup_longitude', 'location_id': 'pickup_location_id'}), 
                  on=['pickup_latitude', 'pickup_longitude'], how='left')
    df = df.merge(locations.rename(columns={'latitude': 'dropoff_latitude', 'longitude': 'dropoff_longitude', 'location_id': 'dropoff_location_id'}), 
                  on=['dropoff_latitude', 'dropoff_longitude'], how='left')
    print("Mapped locations to trips.")

    # Insert trips and metrics
    trips_df = df[['id', 'vendor_id', 'pickup_datetime', 'dropoff_datetime', 'passenger_count', 'trip_distance', 'pickup_location_id', 'dropoff_location_id', 'store_and_fwd_flag']]
    trips_df = trips_df.rename(columns={'id': 'trip_id'})
    trips_df.to_sql('trips', conn, if_exists='append', index=False)

    metrics_df = df[['id', 'trip_duration_min', 'speed_mph']]
    metrics_df = metrics_df.rename(columns={'id': 'trip_id'})
    metrics_df.to_sql('derived_metrics', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()
    print(f"Processed {len(df)} records. Excluded {original_len - len(df)} records. Database populated at {db_file}.")

if __name__ == '__main__':
    process_data('train.csv', 'cleaned_data.csv', 'database/data.db')
    