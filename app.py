import atexit

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
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


@app.route("/api/options", methods=["GET", "POST"])
def api_options():
    if request.method == "POST":
        fog_enabled = request.form["fog"]
        music_enabled = request.form["music"]
        motion_enabled = request.form["motion"]
        hardware.set_fog_enabled(fog_enabled)
        hardware.set_music_enabled(music_enabled)
        hardware.set_motion_enabled(motion_enabled)
    status = {
        "fog": hardware.is_fog_enabled(),
        "music": hardware.is_music_enabled(),
        "motion": hardware.is_motion_enabled()
    }
    return jsonify(status)


@app.route("/api/gpio/<device>/on", methods=["POST"])
def api_gpio_on(device):
    hardware.set_gpio(device, True)
    return jsonify({"status": "ok"})


@app.route("/api/gpio/<device>/off", methods=["POST"])
def api_gpio_off(device):
    hardware.set_gpio(device, False)
    return jsonify({"status": "ok"})


@app.route("/api/led")
def api_led():
    mode = int(request.form["mode"])
    r = request.form["r"]
    g = request.form["g"]
    b = request.form["b"]
    hardware.leds.set_mode(mode, (r, g, b))
    return jsonify({"status": "ok"})


@app.route("/api/animation/trigger", methods=["POST"])
def api_animation_trigger(device):
    hardware.animate()
    return jsonify({"status": "ok"})


def on_exit():
    hardware.stop()


if __name__ == "__main__":
    atexit.register(on_exit)

    # Init the hardware layer
    hardware.start()

    # Start the web server
    app.run(host="0.0.0.0", port=5000)
