The files of the project to be found on the branch master

# OBD2-Reader

A Python-based OBD-II live data logger that collects and stores real-time vehicle sensor data using an ELM327 adapter and `python-OBD`. It features a live dashboard, data storage, and web interface for monitoring engine and vehicle parameters.

---

## Features

- Read live vehicle data from OBD-II interface using ELM327
- Supports common sensors: RPM, speed, coolant temp, intake pressure, voltage, etc.
- Store data in a local SQLite database
- Flask-powered web dashboard for live data viewing
- Sensor chart visualizations with real-time updates
- Logging and export capabilities

---

## Requirements

- Python 3.8+
- ELM327-compatible Bluetooth/USB/Wi-Fi OBD-II adapter
- Supported OBD-II vehicle

### Python Dependencies

Install required libraries:

```bash
pip install -r requirements.txt

# OBD2 Reader Project

## 📦 Project Structure

```
licenta/
├── static/
│   ├── dashboardBG.png
│   ├── loginBG.jpg
│   └── registerBG.jpg
├── templates/
│   ├── check.html
│   ├── dashboard.html
│   ├── extended.html
│   ├── istoric.html
│   ├── lambda_temp_chart.html
│   ├── login.html
│   ├── register.html
├── venv/ (virtual environment)
├── main.py (main application file)
└── obd_data.db (SQLite database)
```

## Getting Started

### 1. Connect Your ELM327 Adapter
* Plug in your ELM327 to the OBD-II port (usually under the steering column)
* Pair via Bluetooth or connect via USB/Wi-Fi
* Note the port name (e.g., `COM3`, `/dev/ttyUSB0`, etc.)

### 2. Set Serial Port in line 17
Modify the port line if needed:

```python
obd_connection = obd.OBD("COM8", fast=False, timeout=1)  # Change this to match your adapter
```

### 3. Start the Reader and Web App

```bash
python main.py
```

The app will start reading data and serve a dashboard at:

```
http://127.0.0.1:5000/
```

## Web Dashboard

The dashboard displays live sensor readings with dynamic updates:
* RPM
* Speed
* Coolant temperature
* Fuel trim
* Battery voltage
* Intake pressure
* Engine load

## Data Storage

All sensor data is logged into an SQLite database (`obd_data.db`) for persistence and analysis.
You can query or export the data using Python or any SQLite browser.

## Troubleshooting

* Ensure your ELM327 is compatible and fully plugged in
* Double-check serial port name and permissions
* Use `obd.scan_serial()` in a Python shell to find available ports

## License

This project is licensed under the MIT License.

## Credits

Developed by bodlex  
Uses python-OBD

## Contact

Feel free to open an issue or contribute via pull requests.

---

Let me know if you'd like me to customize this further — for example, if you want Docker support, screenshots, or additional features!
