from flask import Flask, render_template
from routes.trips_routes import trips_bp

app = Flask(__name__)
app.register_blueprint(trips_bp)

@app.route("/")
def dashboard():
    return render_template("index.html")  # serves frontend

if __name__ == "__main__":
    app.run(debug=True, port=5000)
