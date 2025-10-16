
# Trip duration by hour
TRIP_DURATION_BY_HOUR = """
SELECT
    strftime('%H', pickup_datetime) AS hour,
    AVG(trip_duration_s) AS avg_duration
FROM trips
GROUP BY hour
ORDER BY hour;
"""

# Passenger count distribution
PASSENGER_DISTRIBUTION = """
SELECT
    passenger_count,
    COUNT(*) AS trip_count
FROM trips
GROUP BY passenger_count
ORDER BY passenger_count;
"""

# Heatmap of pickup locations
PICKUP_LOCATIONS = """
SELECT
    l.latitude AS pickup_latitude,
    l.longitude AS pickup_longitude,
    COUNT(*) AS pickups
FROM trips t
JOIN locations l ON t.pickup_location_id = l.location_id
GROUP BY t.pickup_location_id;
"""

# Vendor performance (average trip duration + total trips)
VENDOR_SUMMARY = """
SELECT
    vendor_id,
    COUNT(*) AS total_trips,
    ROUND(AVG(trip_duration_s), 2) AS avg_trip_duration
FROM trips
GROUP BY vendor_id;
"""
# Add your new filtering query here 
FILTER_TRIPS = """
SELECT *
FROM trips
WHERE trip_distance_km BETWEEN :min_distance AND :max_distance
AND pickup_datetime BETWEEN :start_time AND :end_time
ORDER BY pickup_datetime ASC;
"""
