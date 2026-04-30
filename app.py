from flask import Flask, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "root"),          
        password=os.getenv("DB_PASSWORD", "password"),  
        database=os.getenv("DB_NAME", "flask_demo") 
    )

# ---------- BASIC ROUTES ----------
@app.route("/ping", methods=["GET"])
def ping():
    return "pong from Intelligent IoT Flask API in Docker"

@app.route("/")
def index():
    return "Mini API med MySQL kører. Prøv /api/devices"

# ---------- DEVICES API ----------

@app.route("/api/devices", methods=["GET"])
def get_devices():
    """
    Henter alle enheder inklusiv de nye domæne-data: battery_health, yaw_error og error_code.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        # Vi tilføjer de nye kolonner her i SELECT-sætningen:
        cursor.execute("""
            SELECT id, name, location, status, customer_name, last_seen, 
                   temperature, vibration_level, battery_health, yaw_error, error_code 
            FROM devices
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/devices/diagnostics", methods=["GET"])
def get_diagnostics():
    """
    Enhanced diagnostics based on the new statuses from the Domain Model.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, status, temperature, vibration_level FROM devices")
        devices = cursor.fetchall()
        
        for device in devices:
            if device["status"] == "emergency_stop":
                device["urgency"] = "CRITICAL"
                device["action"] = "Pitch Control active. High wind safety triggered."
            elif device["status"] == "misaligned":
                device["urgency"] = "MEDIUM"
                device["action"] = "Jaw Control adjustment required for optimal wind capture."
            elif device["status"] == "low_power":
                device["urgency"] = "HIGH"
                device["action"] = "Battery Health critical. Check charging circuit."
            elif device["status"] == "maintenance" or device["temperature"] > 50:
                device["urgency"] = "HIGH"
                device["action"] = "Check gear oil and cooling system."
            elif device["vibration_level"] == "heavy":
                device["urgency"] = "CRITICAL"
                device["action"] = "Mechanical inspection required."
            else:
                device["urgency"] = "Low"
                device["action"] = "Standard monitoring."
                
        cursor.close()
        conn.close()
        return jsonify(devices), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- SENSOR EVENT (Merged Business Logic) ----------

@app.route("/api/sensor-event", methods=["POST"])
def sensor_event():
    data = request.get_json()
    if not data or "device_id" not in data:
        return jsonify({"error": "Missing device_id"}), 400

    device_id = data.get("device_id")
    value = float(data.get("value", 0)) # Wind Speed
    meta = data.get("metadata", {})
    
    temp = float(meta.get("temperature", 0.0))
    vibration = meta.get("vibration_level", "normal")
    battery = float(meta.get("battery_health", 100.0)) 
    yaw_error = float(meta.get("yaw_error", 0.0))     

    # INTELLIGENT STATUS & ERROR LOGIC
    status = "online"
    error_code = None

    if value > 90:
        status = "emergency_stop"
        error_code = "ERR_WND_03" # Pitch Control safety
    elif battery < 20:
        status = "low_power"
        error_code = "ERR_PWR_05" # Battery Health alert
    elif yaw_error > 15:
        status = "misaligned"
        error_code = "ERR_YAW_04" # Jaw Control adjustment
    elif vibration == "heavy":
        status = "maintenance"
        error_code = "ERR_VIB_01" # Vibration Warn
    elif temp > 50:
        status = "maintenance"
        error_code = "ERR_TMP_02" # Heat Warning
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Note: Added battery_health, yaw_error, and error_code to the UPDATE
        query = """
            UPDATE devices 
            SET status = %s, last_seen = NOW(), temperature = %s, vibration_level = %s,
                battery_health = %s, yaw_error = %s, error_code = %s
            WHERE id = %s
        """
        cursor.execute(query, (status, temp, vibration, battery, yaw_error, error_code, device_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "decision": status, 
            "error_code": error_code,
            "system_check": {
                "pitch": "feathered" if status == "emergency_stop" else "active",
                "battery": battery,
                "yaw": yaw_error
            }
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)