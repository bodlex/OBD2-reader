# OBD2-reader

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
