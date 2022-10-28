import atexit

from flask import (
    Flask,
    jsonify,
    render_template,
)

from hardware import Hardware
from json_encoder import FlaskDatetimeJSONEncoder

# Web configuration
app = Flask(__name__, static_url_path="", static_folder="static")
app.json_encoder = FlaskDatetimeJSONEncoder

# Hardware manager
hardware = Hardware()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    status = {}
    return jsonify(status)


@app.route("/api/test1", methods=["POST"])
def api_test1():
    return jsonify({"status": "ok"})


@app.route("/api/test2")
def api_test2():
    return jsonify({"status": "ok"})


def on_exit():
    hardware.stop()


if __name__ == "__main__":
    atexit.register(on_exit)

    # Init the hardware layer
    hardware.start()
    hardware.play_sequence(hardware.ANIMATION_SEQUENCE)

    # Start the web server
    app.run(host="0.0.0.0", port=5000)
