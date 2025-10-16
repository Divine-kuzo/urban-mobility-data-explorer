import os
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

# --- Setup paths (script-relative, robust to working dir) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# ensure script works regardless of where it's launched from
os.chdir(current_dir)

DATA_DIR = os.path.abspath(os.path.join(current_dir, "..", "data"))
RAW_FILE = os.path.join(DATA_DIR, "train.csv")
CLEAN_FILE = os.path.join(DATA_DIR, "cleaned_trips.csv")
EXCLUDED_FILE = os.path.join(DATA_DIR, "excluded_trips.csv")

# NYC bounding box (for basic coordinate validation)
MIN_LAT, MAX_LAT = 40.4774, 40.9176
MIN_LON, MAX_LON = -74.2591, -73.7004

# --- helper functions ---
def is_valid_coord(lat, lon):
    try:
        lat = float(lat); lon = float(lon)
    except Exception:
        return False
    return MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON

def haversine_km(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two coordinates (Haversine)."""
    # Guard against None/NaN
    try:
        lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    except Exception:
        return None
    R = 6371.0  # Earth radius in km
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1) * cos(phi2) * sin(dlambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# --- Manual duplicate detection algorithm (no pandas.drop_duplicates) ---
# We'll consider duplicates as trips with identical signature: pickup_datetime, dropoff_datetime,
# pickup_lat, pickup_lon, dropoff_lat, dropoff_lon, passenger_count
# We'll implement this with a Python set to track seen signatures.
def make_signature(row):
    # build a normalized tuple signature (strings to avoid float key pitfalls)
    return (
        str(row.get("pickup_datetime")),
        str(row.get("dropoff_datetime")),
        str(row.get("pickup_latitude")),
        str(row.get("pickup_longitude")),
        str(row.get("dropoff_latitude")),
        str(row.get("dropoff_longitude")),
        str(row.get("passenger_count"))
    )

def process_chunk(chunk, seen_signatures):
    cleaned = []
    excluded = []

    # iterate rows (we keep using row access to mirror existing style)
    for _, row in chunk.iterrows():
        reasons = []

        # --- timestamps: parse if present ---
        pickup = None
        dropoff = None
        try:
            if pd.notnull(row.get("pickup_datetime")):
                pickup = pd.to_datetime(row["pickup_datetime"], errors="coerce")
            if pd.notnull(row.get("dropoff_datetime")):
                dropoff = pd.to_datetime(row["dropoff_datetime"], errors="coerce")
        except Exception:
            pickup = None
            dropoff = None

        if pickup is None or pd.isna(pickup) or dropoff is None or pd.isna(dropoff):
            reasons.append("invalid_datetime")
            # still attempt to continue because dataset also contains trip_duration
        else:
            if pickup >= dropoff:
                reasons.append("nonpositive_duration_from_timestamps")

        # --- use trip_duration column if present ---
        trip_duration_s = None
        if "trip_duration" in row.index and pd.notnull(row["trip_duration"]):
            # trip_duration in dataset is usually in seconds
            try:
                trip_duration_s = float(row["trip_duration"])
                if trip_duration_s <= 0:
                    reasons.append("nonpositive_duration")
            except Exception:
                trip_duration_s = None
                reasons.append("bad_trip_duration_value")

        # If trip_duration is missing but timestamps are valid, compute it
        if trip_duration_s is None and pickup is not None and dropoff is not None and not pd.isna(pickup) and not pd.isna(dropoff):
            try:
                trip_duration_s = (dropoff - pickup).total_seconds()
                if trip_duration_s <= 0:
                    reasons.append("nonpositive_duration")
            except Exception:
                trip_duration_s = None
                reasons.append("cannot_compute_duration")

        # --- coordinates validation ---
        pickup_lat = row.get("pickup_latitude") if "pickup_latitude" in row.index else row.get("pickup_lat")
        pickup_lon = row.get("pickup_longitude") if "pickup_longitude" in row.index else row.get("pickup_lon")
        dropoff_lat = row.get("dropoff_latitude") if "dropoff_latitude" in row.index else row.get("dropoff_lat")
        dropoff_lon = row.get("dropoff_longitude") if "dropoff_longitude" in row.index else row.get("dropoff_lon")

        if pd.isnull(pickup_lat) or pd.isnull(pickup_lon):
            reasons.append("missing_pickup_coord")
        elif not is_valid_coord(pickup_lat, pickup_lon):
            reasons.append("invalid_pickup_coord")

        if pd.isnull(dropoff_lat) or pd.isnull(dropoff_lon):
            reasons.append("missing_dropoff_coord")
        elif not is_valid_coord(dropoff_lat, dropoff_lon):
            reasons.append("invalid_dropoff_coord")

        # --- compute trip_distance (Haversine) ---
        trip_distance_km = None
        if pd.notnull(pickup_lat) and pd.notnull(pickup_lon) and pd.notnull(dropoff_lat) and pd.notnull(dropoff_lon):
            trip_distance_km = haversine_km(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
            if trip_distance_km is None:
                reasons.append("cannot_compute_distance")
            else:
                # filter out zero-ish distances (very small distances can be noise)
                if trip_distance_km <= 0:
                    reasons.append("bad_distance")

        else:
            # if coords missing we already flagged missing; we may still exclude later
            pass

        # --- compute speed (km/h) if both duration and distance exist ---
        trip_speed_kmph = None
        if trip_distance_km is not None and trip_duration_s is not None and trip_duration_s > 0:
            trip_speed_kmph = trip_distance_km / (trip_duration_s / 3600.0)
            # unrealistic speed guard
            if trip_speed_kmph > 200:  # threshold for taxi speeds in city
                reasons.append("outlier_speed")

        # --- manual duplicate detection ---
        sig = make_signature(row)
        if sig in seen_signatures:
            reasons.append("duplicate")
        else:
            seen_signatures.add(sig)

        # --- final decision: exclude if any reasons ---
        record = dict(row)  # convert to plain dict
        # append derived fields even if excluded for transparency
        record.update({
            "trip_duration_s": trip_duration_s,
            "trip_distance_km": trip_distance_km,
            "trip_speed_kmph": trip_speed_kmph
        })

        if reasons:
            record["reason"] = ";".join(reasons)
            excluded.append(record)
        else:
            cleaned.append(record)

    return cleaned, excluded

def main():
    print("RAW_FILE path:", RAW_FILE)
    print("CLEAN_FILE path:", CLEAN_FILE)
    print("EXCLUDED_FILE path:", EXCLUDED_FILE)

    if not os.path.exists(RAW_FILE):
        print("ERROR: Raw file not found at:", RAW_FILE)
        return

    cleaned_all = []
    excluded_all = []
    seen_signatures = set()  # for manual duplicate detection

    try:
        # read in chunks to handle large files
        for chunk in pd.read_csv(RAW_FILE, chunksize=100000):
            print(f"Processing chunk of size {len(chunk)}")
            cleaned, excluded = process_chunk(chunk, seen_signatures)
            cleaned_all.extend(cleaned)
            excluded_all.extend(excluded)
    except pd.errors.EmptyDataError:
        print("ERROR: CSV is empty or malformed.")
        return
    except Exception as e:
        print("ERROR during processing:", e)
        return

    # ensure output dir exists
    os.makedirs(os.path.dirname(CLEAN_FILE), exist_ok=True)

    # Save results
    pd.DataFrame(cleaned_all).to_csv(CLEAN_FILE, index=False)
    pd.DataFrame(excluded_all).to_csv(EXCLUDED_FILE, index=False)
    print(f"✅ Saved {len(cleaned_all)} cleaned trips, {len(excluded_all)} excluded trips")

if __name__ == "__main__":
    main()
