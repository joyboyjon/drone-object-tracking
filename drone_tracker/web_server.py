import logging
import threading
import time

import cv2
from flask import Flask, Response, jsonify, render_template, request


class SharedState:
    """Datele comune intre bucla de procesare si serverul web."""

    def __init__(self, max_events=200):
        self.lock = threading.Lock()
        self.playing = threading.Event()       # setat = clipul ruleaza, sters = pauza
        self.restart_requested = False         # s-a apasat "Reia testul"
        self.frame_jpeg = None                 # ultima imagine, codificata JPEG
        self.status = {"fps": 0, "objects": 0, "frame": 0,
                       "target": "Apasa Start", "motion": ""}
        self.events = []                       # mesajele din consola
        self.max_events = max_events
        self.click = None                      # ultimul click primit din pagina

    def set_frame(self, frame):
        ok, buffer = cv2.imencode(".jpg", frame)
        if ok:
            with self.lock:
                self.frame_jpeg = buffer.tobytes()

    def set_status(self, status):
        with self.lock:
            self.status = status

    def add_event(self, text):
        print(text)
        with self.lock:
            self.events.append(text)
            self.events = self.events[-self.max_events:]

    def pop_click(self):
        with self.lock:
            point = self.click
            self.click = None
            return point

    def request_restart(self):
        with self.lock:
            self.restart_requested = True
        self.playing.set()

    def take_restart(self):
        """Returneaza True daca s-a cerut reluarea (si sterge cererea)."""
        with self.lock:
            requested = self.restart_requested
            self.restart_requested = False
            return requested    


def generate_frames(state):
    """Trimite continuu ultima imagine catre browser (format MJPEG)."""
    while True:
        with state.lock:
            jpeg = state.frame_jpeg
        if jpeg is not None:
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n")
        time.sleep(0.05)


def create_app(state):
    app = Flask(__name__)
    # Ascundem mesajele serverului pentru fiecare cerere, ca sa nu acopere consola
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/video")
    def video():
        return Response(generate_frames(state),
                        mimetype="multipart/x-mixed-replace; boundary=frame")

    @app.route("/status")
    def status():
        with state.lock:
            return jsonify(status=state.status, events=state.events,
                           running=state.playing.is_set())

    @app.route("/click", methods=["POST"])
    def click():
        data = request.get_json()
        with state.lock:
            state.click = (int(data["x"]), int(data["y"]))
        return jsonify(ok=True)

    @app.route("/control", methods=["POST"])
    def control():
        action = request.get_json()["action"]
        if action == "start":
            state.playing.set()
        elif action == "pause":
            state.playing.clear()
        elif action == "restart":
            state.request_restart()
        return jsonify(ok=True)

    return app