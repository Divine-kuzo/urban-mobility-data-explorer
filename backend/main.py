from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "Hello Divine"
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
