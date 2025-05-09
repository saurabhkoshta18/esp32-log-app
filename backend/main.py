from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime
import pandas as pd

from backend.database import get_db
from backend.models import Log

app = FastAPI()

# Path setup
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend/templates"
STATIC_DIR = BASE_DIR / "frontend/static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# Fake login session (to be replaced with real auth)
def get_current_user(request: Request):
    return "user"


# Login page
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Register page
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    logs = db.query(Log).order_by(Log.date.desc(), Log.time.desc()).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "logs": logs})


# Download form page
@app.get("/download", response_class=HTMLResponse)
def download_page(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("download.html", {"request": request})


# Handle Excel download
@app.post("/download")
def download_logs(request: Request, start_date: str = Form(...), end_date: str = Form(...), db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    try:
        filename = generate_excel_logs(start_date, end_date, db)
        return FileResponse(filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="logs.xlsx")
    except Exception as e:
        return templates.TemplateResponse("download.html", {"request": request, "error": str(e)})


# Generate Excel from filtered logs
def generate_excel_logs(start_date: str, end_date: str, db: Session) -> str:
    # Convert to comparable format
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    # Load all logs and filter in Python
    all_logs = db.query(Log).all()
    filtered = []
    for log in all_logs:
        try:
            log_date = datetime.strptime(log.date, "%Y-%m-%d").date()
            if start <= log_date <= end:
                filtered.append(log)
        except ValueError:
            continue  # Skip malformed dates

    # Convert to DataFrame
    df = pd.DataFrame([{
        "UID": log.uid,
        "Action": log.action,
        "Date": log.date,
        "Time": log.time
    } for log in filtered])

    output_file = BASE_DIR / "logs.xlsx"
    df.to_excel(output_file, index=False)
    return str(output_file)
