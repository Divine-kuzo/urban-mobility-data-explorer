from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "Hello Divine"
    })

@app.route("/highest_passengers")
def get_highest_passengers():
    '''Endpoint to get the 5 highest number of passengers in a taxi ride.'''
    return jsonify({
        "status": "success",
        "message": "highest passengers"
    })

@app.route("/shortest_trip_duration")
def get_shortest_trip_duration():
    '''Endpoint to get the 5 shortest trip duration in a taxi ride.'''
    return jsonify({
        "status": "success",
        "message": "shortest trip duration"
    })

@app.route("/vendor")
def get_vendor():
    return jsonify({
        "status": "success",
        "message": "vendor info"
    })


if __name__ == "__main__":
    # debug=True enables automatic reloading and detailed error messages
    app.run(host="127.0.0.1", port=8000, debug=True)
