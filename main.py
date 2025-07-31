import sqlite3
from datetime import datetime
import obd
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from numpy import interp

app = Flask(__name__)
app.secret_key = 'jvb32$%v512%!7yB^&78V@V#'

# GLOBAL
obd_connection = None

def init_obd():
    global obd_connection
    try:
        obd_connection = obd.OBD("COM8", fast=False, timeout=1)
        print("OBD connected")
    except Exception as e:
        print("OBD connection failed:", e)

init_obd()

# Inițializare baza de date
def init_db():
    conn = sqlite3.connect("obd_data.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        fuel_type TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS date_extinse (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TEXT,
        rpm INTEGER,
        speed INTEGER,
        torque REAL,
        coolant_temp INTEGER,
        intake_pressure INTEGER,
        battery_voltage REAL,
        fuel_consumption REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")

    conn.commit()
    conn.close()

init_db()
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("obd_data.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["logged_in"] = True
            session["username"] = username
            session["user_id"] = user[0]
            session["fuel_type"] = user[3]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials.")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        fuel_type = request.form["fuel_type"]

        hashed = generate_password_hash(password)

        try:
            conn = sqlite3.connect("obd_data.db")
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, fuel_type) VALUES (?, ?, ?)",
                      (username, hashed, fuel_type))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already exists.")
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/lambda_chart")
def lambda_chart():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("lambda_temp_chart.html", username=session["username"])

@app.route("/lambda_data")
def lambda_data():
    if not session.get("logged_in") or not obd_connection or not obd_connection.is_connected():
        return jsonify([])
    try:
        senzor = obd_connection.query(obd.commands.O2_S1_WR_VOLTAGE)
        valoare = senzor.value.magnitude if senzor and senzor.value else 0
        return jsonify([[datetime.now().isoformat(), valoare]])
    except Exception as e:
        print("Eroare la citirea lambda:", e)
        return jsonify([])


@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])

def calculate_power_and_torque(maf, rpm, fuel_type):
    try:
        if maf is None or rpm is None or rpm == 0:
            return None, None

        fuel_settings = {
            'diesel': {
                'afr': 14.5,
                'energy_density': 45.4,
                'eff_map': [(0, 0.0), (500, 0.20), (1000, 0.30), (2000, 0.38),
                            (3000, 0.43), (4000, 0.33), (5000, 0.26), (6000, 0.22)]
            },
            'gasoline': {
                'afr': 14.7,
                'energy_density': 43.4,
                'eff_map': [(0, 0.0), (500, 0.13), (1000, 0.20), (2000, 0.27),
                            (3000, 0.30), (4000, 0.27), (5000, 0.23), (6000, 0.18)]
            }
        }

        fuel = fuel_settings.get(fuel_type.lower())
        if not fuel:
            return None, None

        efficiency = interp(rpm, [pt[0] for pt in fuel['eff_map']], [pt[1] for pt in fuel['eff_map']])
        fuel_flow_kgh = (maf * 3600) / (fuel['afr'] * 1000)
        thermal_power_kw = (fuel_flow_kgh * fuel['energy_density']) / 3.6
        engine_power_kw = thermal_power_kw * efficiency
        torque = (engine_power_kw * 9550) / rpm

        return round(engine_power_kw,2), round(torque, 2)

    except:
        return None, None


@app.route("/extended")
def extended():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("extended.html", username=session["username"])


@app.route("/extended/data")
def extended_data():
    if not session.get("logged_in") or not obd_connection or not obd_connection.is_connected():
        return jsonify([])

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_value(cmd):
        try:
            response = obd_connection.query(cmd)
            return response.value.magnitude if response and response.value else None
        except:
            return None

    vin = None
    try:
        vin_response = obd_connection.query(obd.commands.VIN)
        if vin_response and vin_response.value:
            vin_raw = vin_response.value
            if isinstance(vin_raw, bytearray):
                vin = vin_raw.decode("utf-8")
            else:
                vin = str(vin_raw)
            session["vin"] = vin
    except Exception as e:
        print("Could not read VIN:", e)

    # Citire parametri
    rpm = get_value(obd.commands.RPM)
    speed = get_value(obd.commands.SPEED)
    try:
        response = obd_connection.query(obd.commands.COOLANT_TEMP)
        if response and response.value is not None:
            coolant_temp = int(response.value.to("celsius").magnitude)
        else:
            coolant_temp = 0
    except Exception as e:
        print("Eroare coolant_temp:", e)
        coolant_temp = 0
    intake_pressure = get_value(obd.commands.INTAKE_PRESSURE)
    battery_voltage = get_value(obd.commands.CONTROL_MODULE_VOLTAGE)
    maf = get_value(obd.commands.MAF)

    battery_voltage = round(battery_voltage, 2) if battery_voltage else None
    fuel_type = session.get("fuel_type", "gasoline")

    # Calcule
    consum_combustibil = None
    if maf:
        if fuel_type == "diesel":
            densitate = 0.85
            afr = 14.5
        else:
            densitate = 0.74
            afr = 14.7

        consum_combustibil = round(maf / (densitate * afr), 2)

    power, torque = calculate_power_and_torque(maf, rpm, fuel_type)

    user_id = session["user_id"]

    conn = sqlite3.connect("obd_data.db")
    c = conn.cursor()

    c.execute('''
        INSERT INTO date_extinse (
            user_id, timestamp, rpm, speed, torque, coolant_temp,
            intake_pressure, battery_voltage, fuel_consumption
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, timestamp, rpm or 0, speed or 0, torque or 0,
        coolant_temp or 0, intake_pressure or 0, battery_voltage or 0,
        consum_combustibil or 0
    ))
    conn.commit()

    c.execute('''
        SELECT timestamp, rpm, speed, torque, coolant_temp,
               intake_pressure, battery_voltage, fuel_consumption
        FROM date_extinse
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 10
    ''', (user_id,))
    data = c.fetchall()
    conn.close()

    return jsonify(data)
@app.route("/istoric")
def istoric():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    vin = session.get("vin", "VIN unavailable")  # default daca nu a fost citit
    conn = sqlite3.connect("obd_data.db")
    c = conn.cursor()
    c.execute('''
        SELECT timestamp, rpm, speed, torque, coolant_temp,
               intake_pressure, battery_voltage, fuel_consumption
        FROM date_extinse
        WHERE user_id = ?
        ORDER BY timestamp DESC
    ''', (user_id,))
    data = c.fetchall()
    conn.close()

    return render_template("istoric.html", data=data, vin=vin)

@app.route("/check")
def check():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("obd_data.db")
    c = conn.cursor()
    c.execute('''
        SELECT coolant_temp, battery_voltage, intake_pressure
        FROM date_extinse
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (session["user_id"],))
    row = c.fetchone()
    conn.close()

    if not row:
        verdict = "No data available."
        issues = []
    else:
        coolant, voltage, intake = row
        issues = []

        if not (70 <= coolant <= 110):
            issues.append(f"Coolant Temp: {coolant}°C")
        if not (12.0 <= voltage <= 14.5):
            issues.append(f"Battery Voltage: {voltage}V")
        if not (20 <= intake <= 180):
            issues.append(f"Intake Pressure: {intake} kPa")

        if not issues:
            verdict = "Your car is running fine."
        else:
            verdict = "Your car should be checked by a specialist."

    return render_template("check.html", verdict=verdict, issues=issues)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)