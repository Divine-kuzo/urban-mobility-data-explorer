
from flask import Blueprint, jsonify, request
from database import get_db_connection
from queries import trips_queries



trips_bp = Blueprint("trips", __name__)

@trips_bp.route("/trips/duration-by-hour")
def duration_by_hour():
    conn = get_db_connection()
    rows = conn.execute(trips_queries.TRIP_DURATION_BY_HOUR).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@trips_bp.route("/trips/passenger-distribution")
def passenger_distribution():
    conn = get_db_connection()
    rows = conn.execute(trips_queries.PASSENGER_DISTRIBUTION).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@trips_bp.route("/trips/pickup-locations")
def pickup_locations():
    conn = get_db_connection()
    rows = conn.execute(trips_queries.PICKUP_LOCATIONS).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@trips_bp.route("/trips/vendor-summary")
def vendor_summary():
    conn = get_db_connection()
    rows = conn.execute(trips_queries.VENDOR_SUMMARY).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@trips_bp.route("/trips/search")
def search_trips():
    # Get query parameters from URL
    min_distance = request.args.get("min_distance", 0, type=float)
    max_distance = request.args.get("max_distance", 1000, type=float)
    start_time = request.args.get("start_time", "00:00")
    end_time = request.args.get("end_time", "23:59")

    # Convert times to full datetime format if needed
    # e.g., "2025-10-16 00:00:00" depending on your DB format
    start_datetime = f"2025-10-16 {start_time}:00"  # adjust date as needed
    end_datetime = f"2025-10-16 {end_time}:59"

    conn = get_db_connection()
    rows = conn.execute(
        trips_queries.FILTER_TRIPS,
        {
            "min_distance": min_distance,
            "max_distance": max_distance,
            "start_time": start_datetime,
            "end_time": end_datetime
        }
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])