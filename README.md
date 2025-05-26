# ESP32 Log Dashboard

This is a Flask-based web application that:

- Accepts logs from ESP32 via HTTP
- Displays logs in a web dashboard
- Supports user login and registration
- Allows log download by date range (CSV)
- Automatically refreshes logs every 5 seconds

## 📦 Features

- Flask + SQLite backend
- Flask-Login user authentication
- HTML/CSS frontend with auto-refresh
- Download logs in CSV format
- Ready to deploy on Render (free tier)

## 🚀 Setup Instructions

1. Clone this repo and create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
