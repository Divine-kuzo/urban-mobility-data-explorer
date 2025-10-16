import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
CLEAN_FILE = os.path.join(DATA_DIR, "cleaned_trips.csv")
EXCLUDED_FILE = os.path.join(DATA_DIR, "excluded_trips.csv")
DB_PATH = os.path.join(DATA_DIR, "urban_mobility.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

with open(os.path.join(BASE_DIR, "schema.sql"), "r", encoding="utf-8") as f:
    cur.executescript(f.read())
conn.commit()

print("Loading cleaned data...")
df_clean = pd.read_csv(CLEAN_FILE)
df_excluded = pd.read_csv(EXCLUDED_FILE)

def insert_locations(df, lat_col, lon_col):
    unique_coords = (
        df[[lat_col, lon_col]]
        .dropna()
        .drop_duplicates()
        .round(6)
        .values.tolist()
    )
    cur.executemany(
        "INSERT OR IGNORE INTO locations (latitude, longitude) VALUES (?, ?);",
        unique_coords,
    )
    conn.commit()

insert_locations(df_clean, "pickup_latitude", "pickup_longitude")
insert_locations(df_clean, "dropoff_latitude", "dropoff_longitude")

def get_location_id(lat, lon):
    cur.execute(
        "SELECT location_id FROM locations WHERE latitude = ? AND longitude = ?;",
        (round(lat, 6), round(lon, 6)),
    )
    res = cur.fetchone()
    return res[0] if res else None

print("Inserting trips...")
cur.execute("SELECT trip_id FROM trips;")
existing_trip_ids = {row[0] for row in cur.fetchall()}

trip_rows = []
for _, row in df_clean.iterrows():
    trip_id = row["id"]
    if trip_id in existing_trip_ids:
        continue  # skip duplicates
    try:
        pickup_id = get_location_id(row["pickup_latitude"], row["pickup_longitude"])
        dropoff_id = get_location_id(row["dropoff_latitude"], row["dropoff_longitude"])
        trip_rows.append((
            trip_id,
            row["vendor_id"],
            row["pickup_datetime"],
            row["dropoff_datetime"],
            pickup_id,
            dropoff_id,
            row["passenger_count"],
            row["store_and_fwd_flag"],
            row["trip_duration"]
        ))
    except Exception as e:
        print("Skipping row due to error:", e)
        continue

if trip_rows:
    cur.executemany("""
        INSERT INTO trips (
            trip_id, vendor_id, pickup_datetime, dropoff_datetime,
            pickup_location_id, dropoff_location_id,
            passenger_count, store_and_fwd_flag, trip_duration_s
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, trip_rows)
    conn.commit()
print(f"✅ Inserted {len(trip_rows)} new trips (skipped existing ones)")

if not df_excluded.empty:
    print("Inserting excluded trips...")
    if "id" in df_excluded.columns:
        df_excluded = df_excluded.rename(columns={"id": "trip_id"})
    excluded_columns = [
        "excluded_id", "trip_id", "vendor_id", "pickup_datetime", "dropoff_datetime",
        "pickup_latitude", "pickup_longitude", "dropoff_latitude", "dropoff_longitude",
        "passenger_count", "store_and_fwd_flag", "trip_duration_s", "reason"
    ]
    df_excluded = df_excluded.reindex(columns=[col for col in excluded_columns if col in df_excluded.columns])
    df_excluded.to_sql("excluded_trips", conn, if_exists="append", index=False)
    conn.commit()
    print(f"✅ Inserted {len(df_excluded)} excluded trips")

conn.close()
print("✅ Database successfully updated:", DB_PATH)
