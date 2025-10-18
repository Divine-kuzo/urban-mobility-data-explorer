from flask import Flask, request, jsonify
import sqlite3
import os
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db():
    # Use absolute path to database
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, '../database/data.db')
    print(f"Database path: {db_path}")  # Debug line
    
    # Check if database exists
    if not os.path.exists(db_path):
        raise Exception(f"Database file not found at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return jsonify({'message': 'Urban Mobility Explorer API'})

@app.route('/api/trips', methods=['GET'])
def get_trips():
    start_time = time.time()
    try:
        conn = get_db()
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        offset = (page - 1) * per_page
        
        # Base query for trips data
        base_query = """
        SELECT t.trip_id, t.pickup_datetime, t.trip_distance, 
               dm.speed_mph, dm.trip_duration_min
        FROM trips t
        JOIN derived_metrics dm ON t.trip_id = dm.trip_id
        WHERE 1=1
        """
        
        # Count query for pagination
        count_query = """
        SELECT COUNT(*) as total
        FROM trips t
        JOIN derived_metrics dm ON t.trip_id = dm.trip_id
        WHERE 1=1
        """
        
        params = []
        
        # Add filters if provided
        if 'date' in request.args:
            filter_condition = " AND date(t.pickup_datetime) = ?"
            base_query += filter_condition
            count_query += filter_condition
            params.append(request.args['date'])
            
        if 'min_distance' in request.args:
            filter_condition = " AND t.trip_distance >= ?"
            base_query += filter_condition
            count_query += filter_condition
            params.append(float(request.args['min_distance']))
        
        # Add pagination to main query
        base_query += " ORDER BY t.pickup_datetime DESC LIMIT ? OFFSET ?"
        pagination_params = params + [per_page, offset]
        
        # Get total count (without pagination params)
        count_result = conn.execute(count_query, params).fetchone()
        total_trips = count_result['total'] if count_result else 0
        total_pages = (total_trips + per_page - 1) // per_page if per_page > 0 else 1
        
        # Get paginated trips
        rows = conn.execute(base_query, pagination_params).fetchall()
        trips = [dict(row) for row in rows]
        
        conn.close()
        
        execution_time = time.time() - start_time
        print(f"Query executed in {execution_time:.2f}s, returned {len(trips)} trips (page {page})")
        
        return jsonify({
            'success': True,
            'trips': trips,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_trips': total_trips,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            },
            'execution_time': execution_time
        })
        
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"Error after {execution_time:.2f} seconds: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'execution_time': execution_time
        }), 500

@app.route('/api/summary', methods=['GET'])
def get_summary():
    start_time = time.time()
    try:
        conn = get_db()
        
        # Use sampling for large datasets - much faster!
        sample_size = 100000  # Sample 100k records for charts
        
        query = """
        WITH sampled_trips AS (
            SELECT t.trip_id, t.pickup_datetime, dm.speed_mph
            FROM trips t
            JOIN derived_metrics dm ON t.trip_id = dm.trip_id
            WHERE dm.speed_mph > 0 AND dm.speed_mph < 100  -- Reasonable speed range
            ORDER BY RANDOM()
            LIMIT ?
        )
        SELECT 
            strftime('%H', pickup_datetime) AS hour, 
            COUNT(*) AS trip_count,
            AVG(speed_mph) AS avg_speed
        FROM sampled_trips
        GROUP BY hour
        ORDER BY hour
        """
        
        rows = conn.execute(query, [sample_size]).fetchall()
        summary = [dict(row) for row in rows]
        
        conn.close()
        
        execution_time = time.time() - start_time
        print(f"Summary query executed in {execution_time:.2f}s (sampled {sample_size} records)")
        
        return jsonify({
            'success': True,
            'summary': summary,
            'sampling_info': {
                'sample_size': sample_size,
                'method': 'random_sampling'
            },
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = time.time() - start_time
        return jsonify({
            'success': False,
            'error': str(e),
            'execution_time': execution_time
        }), 500

@app.route('/api/insights', methods=['GET'])
def get_insights():
    start_time = time.time()
    try:
        conn = get_db()
        insights = []

        # Insight 1: Busiest hours (use daily aggregates for speed)
        query1 = """
        SELECT strftime('%H', pickup_datetime) AS hour, COUNT(*) AS trip_count
        FROM trips
        GROUP BY hour
        ORDER BY trip_count DESC
        LIMIT 3
        """
        rows1 = conn.execute(query1).fetchall()
        insights.append({
            'name': 'Busiest Hours', 
            'data': [{'hour': row['hour'], 'trip_count': row['trip_count']} for row in rows1], 
            'description': 'Top 3 hours with most trips, indicating peak demand.'
        })

        # Insight 2: Slowest hours by speed (use sampling)
        query2 = """
        WITH speed_sample AS (
            SELECT strftime('%H', pickup_datetime) AS hour, speed_mph
            FROM trips t
            JOIN derived_metrics dm ON t.trip_id = dm.trip_id
            WHERE speed_mph > 0 AND speed_mph < 100
            LIMIT 50000
        )
        SELECT hour, ROUND(AVG(speed_mph), 2) AS avg_speed
        FROM speed_sample
        GROUP BY hour
        ORDER BY avg_speed ASC
        LIMIT 3
        """
        rows2 = conn.execute(query2).fetchall()
        insights.append({
            'name': 'Slowest Hours', 
            'data': [{'hour': row['hour'], 'avg_speed': row['avg_speed']} for row in rows2], 
            'description': 'Hours with lowest average speed, likely due to congestion.'
        })

        # Insight 3: Longest trips by distance
        query3 = """
        SELECT trip_id, ROUND(trip_distance, 2) as trip_distance
        FROM trips
        WHERE trip_distance > 0
        ORDER BY trip_distance DESC
        LIMIT 5
        """
        rows3 = conn.execute(query3).fetchall()
        insights.append({
            'name': 'Longest Trips', 
            'data': [{'trip_id': row['trip_id'], 'trip_distance': row['trip_distance']} for row in rows3], 
            'description': 'Trips with the longest distances.'
        })

        conn.close()
        
        execution_time = time.time() - start_time
        print(f"Insights query executed in {execution_time:.2f}s")
        
        return jsonify({
            'success': True,
            'insights': insights,
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = time.time() - start_time
        return jsonify({
            'success': False,
            'error': str(e),
            'execution_time': execution_time
        }), 500

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to check database status"""
    start_time = time.time()
    try:
        conn = get_db()
        
        # Count records in each table
        tables = ['trips', 'locations', 'derived_metrics']
        counts = {}
        
        for table in tables:
            try:
                count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
                counts[table] = count
            except Exception as e:
                counts[table] = f'Error: {str(e)}'
        
        # Check database size
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, '../database/data.db')
        db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        
        # Check if we have any data
        sample_trips = conn.execute('SELECT trip_id FROM trips LIMIT 1').fetchall()
        
        conn.close()
        
        execution_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'database_status': 'connected',
            'database_size_mb': round(db_size / (1024 * 1024), 2),
            'table_counts': counts,
            'has_data': len(sample_trips) > 0,
            'sample_trips_count': len(sample_trips),
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = time.time() - start_time
        return jsonify({
            'success': False,
            'error': str(e),
            'database_status': 'failed',
            'execution_time': execution_time
        }), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint that doesn't use database"""
    return jsonify({
        'success': True,
        'message': 'API is working',
        'timestamp': time.time()
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get basic statistics about the dataset"""
    start_time = time.time()
    try:
        conn = get_db()
        
        stats = {}
        
        # Basic trip statistics
        stats_query = """
        SELECT 
            COUNT(*) as total_trips,
            MIN(pickup_datetime) as earliest_trip,
            MAX(pickup_datetime) as latest_trip,
            AVG(trip_distance) as avg_distance,
            AVG(speed_mph) as avg_speed,
            AVG(trip_duration_min) as avg_duration
        FROM trips t
        JOIN derived_metrics dm ON t.trip_id = dm.trip_id
        WHERE trip_distance > 0 AND speed_mph > 0
        """
        
        stats_result = conn.execute(stats_query).fetchone()
        stats = dict(stats_result) if stats_result else {}
        
        conn.close()
        
        execution_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'stats': stats,
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = time.time() - start_time
        return jsonify({
            'success': False,
            'error': str(e),
            'execution_time': execution_time
        }), 500

@app.route('/api/quick-summary', methods=['GET'])
def get_quick_summary():
    """Ultra-fast summary using pre-aggregated data or sampling"""
    start_time = time.time()
    try:
        conn = get_db()
        
        # Even faster approach - use hourly aggregates if available, otherwise minimal sampling
        query = """
        SELECT 
            strftime('%H', pickup_datetime) AS hour, 
            COUNT(*) AS trip_count,
            (SELECT AVG(speed_mph) 
             FROM derived_metrics dm 
             JOIN trips t2 ON dm.trip_id = t2.trip_id 
             WHERE strftime('%H', t2.pickup_datetime) = strftime('%H', trips.pickup_datetime) 
             LIMIT 1000) AS avg_speed
        FROM trips 
        GROUP BY hour
        ORDER BY hour
        """
        
        rows = conn.execute(query).fetchall()
        summary = []
        
        for row in rows:
            summary.append({
                'hour': row['hour'],
                'trip_count': row['trip_count'],
                'avg_speed': row['avg_speed'] or 0
            })
        
        conn.close()
        
        execution_time = time.time() - start_time
        print(f"Quick summary executed in {execution_time:.2f}s")
        
        return jsonify({
            'success': True,
            'summary': summary,
            'method': 'hourly_aggregates',
            'execution_time': execution_time
        })
    except Exception as e:
        execution_time = time.time() - start_time
        return jsonify({
            'success': False,
            'error': str(e),
            'execution_time': execution_time
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    