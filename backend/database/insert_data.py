#!/usr/bin/env python3
"""Simple data insertion example that mirrors what we used in tests.
Run this if you want to (re)populate the database at /mnt/data/trips_demo.db (it will overwrite)."""
import sqlite3, random
from datetime import datetime, timedelta
DB_PATH = "database/dump.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
# This script assumes schema.sql has already been applied.
# For brevity it inserts 10 sample trips only.
cur.execute("INSERT INTO passengers(passenger_id, passenger_count) VALUES(?,?)", (9999, 2))
cur.execute("INSERT INTO locations(location_id, latitude, longitude) VALUES(?,?,?)", (9999, -1.94, 30.06))
cur.execute("INSERT INTO payments(payment_id, payment_type, fare_amount) VALUES(?,?,?)", (9999, 'card', 12.50))
pickup = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
dropoff = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
cur.execute("""INSERT INTO trips(trip_id, pickup_datetime, dropoff_datetime, trip_duration_s, trip_distance_km, trip_speed_kmph,
                pickup_location_id, dropoff_location_id, passenger_id, payment_id)
                VALUES(?,?,?,?,?,?,?,?,?,?)""", (9999, pickup, dropoff, 600, 5.0, 30.0, 9999, 9999, 9999, 9999))
conn.commit()
conn.close()
print('Inserted demo trip id=9999')