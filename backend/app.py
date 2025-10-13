from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)
DB = "database/dump.db"

def q(sql, params=()):
    try:
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    except sqlite3.Error as e:
        return [{"error": str(e)}]
    finally:
        conn.close()

@app.route('/')
def home():
    return jsonify({
        "message": "Flask app is running!",
        "routes": [
            "/avg_fare_by_hour",
            "/top_dropoffs"
        ]
    })

@app.route('/avg_fare_by_hour')
def avg_fare_by_hour():
    sql = """
    SELECT 
        strftime('%H', pickup_datetime) AS hour,
        COUNT(*) AS trips_count,
        ROUND(AVG(p.fare_amount), 2) AS avg_fare
    FROM trips t
    JOIN payments p ON t.trip_id = p.trip_id
    GROUP BY hour
    ORDER BY hour;
    """
    result = q(sql)
    if not result:
        return jsonify({"message": "No data available"})
    return jsonify(result)

@app.route('/top_dropoffs')
def top_dropoffs():
    sql = """
    SELECT 
        l.location_id,
        printf("Lat: %.5f, Lon: %.5f", l.latitude, l.longitude) AS location_label,
        COUNT(*) AS trips_count,
        ROUND(AVG(p.fare_amount), 2) AS avg_fare,
        ROUND(AVG(t.trip_distance_km), 2) AS avg_dist_km
    FROM trips t
    JOIN locations l ON t.dropoff_location_id = l.location_id
    JOIN payments p ON t.trip_id = p.trip_id
    GROUP BY l.location_id
    ORDER BY avg_fare DESC
    LIMIT 10;
    """
    result = q(sql)
    if not result:
        return jsonify({"message": "No data available"})
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
