from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json

from mqtt_publisher import publish_timetable

app = Flask(__name__)
CORS(app)

# ===== PATH CONFIG =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "timetables")

os.makedirs(DATA_DIR, exist_ok=True)


# =========================================================
# GET LIST OF CLASSES
# =========================================================
@app.route("/api/classes", methods=["GET"])
def get_classes():
    classes = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".json"):
            classes.append(file.replace(".json", ""))
    return jsonify(classes), 200


# =========================================================
# GET TIMETABLE FOR A CLASS
# =========================================================
@app.route("/api/timetable/<class_name>", methods=["GET"])
def get_timetable(class_name):
    path = os.path.join(DATA_DIR, f"{class_name}.json")

    if not os.path.exists(path):
        return jsonify({}), 200

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return jsonify(data), 200


# =========================================================
# SAVE TIMETABLE (NO MQTT)
# =========================================================
@app.route("/api/timetable/<class_name>", methods=["POST"])
def save_timetable(class_name):
    data = request.json
    path = os.path.join(DATA_DIR, f"{class_name}.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"💾 Timetable saved for {class_name}")

    return jsonify({
        "status": "ok",
        "message": "saved"
    }), 200


# =========================================================
# SAVE + PUBLISH TIMETABLE (MQTT)
# =========================================================
@app.route("/api/timetable/<class_name>/publish", methods=["POST"])
def publish_timetable_api(class_name):
    data = request.json

    # 🔍 DEBUG LOGS
    print("\n==============================")
    print("📤 PUBLISH API HIT")
    print("📘 Class:", class_name)
    print("📦 Data received from publisher:")
    print(json.dumps(data, indent=2))
    print("==============================\n")

    # 1️⃣ Save to file
    path = os.path.join(DATA_DIR, f"{class_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # 2️⃣ Publish to MQTT (NON-BLOCKING)
    try:
        publish_timetable(class_name, data)
        print("📡 MQTT published successfully")
    except Exception as e:
        print("❌ MQTT publish failed:", e)

    # 3️⃣ IMPORTANT: RETURN RESPONSE
    return jsonify({
        "status": "ok",
        "message": "published"
    }), 200


# =========================================================
# ROOT
# =========================================================
@app.route("/")
def index():
    return "E-Display Backend is running", 200


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
