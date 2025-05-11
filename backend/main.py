from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime
import pandas as pd

from backend.database import get_db
from backend.models import Log, User, create_database

create_database()

app = FastAPI()

# Path setup
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "frontend/templates"
STATIC_DIR = BASE_DIR / "frontend/static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Fake session
def get_current_user(request: Request):
    return "user"  # Placeholder

# Home - Login
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})

# Register
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    try:
        new_user = User(username=username, password=password)
        db.add(new_user)
        db.commit()
        return templates.TemplateResponse("login.html", {"request": request, "message": "Registration successful! Please log in."})
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse("register.html", {"request": request, "error": str(e)})

# Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Logs for dashboard refresh (AJAX)
@app.get("/api/logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(Log).order_by(Log.date.desc(), Log.time.desc()).all()
    return JSONResponse(content=[
        {
            "uid": log.uid,
            "action": log.action,
            "date": log.date,
            "time": log.time
        }
        for log in logs
    ])

# Download logs page
@app.get("/download", response_class=HTMLResponse)
def download_page(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("download.html", {"request": request})

# Handle download
@app.post("/download")
def download_logs(request: Request, start_date: str = Form(...), end_date: str = Form(...), db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    try:
        filename = generate_excel_logs(start_date, end_date, db)
        return FileResponse(filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="logs.xlsx")
    except Exception as e:
        return templates.TemplateResponse("download.html", {"request": request, "error": str(e)})

# Generate Excel file
def generate_excel_logs(start_date: str, end_date: str, db: Session) -> str:
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format")

    all_logs = db.query(Log).all()
    filtered = []
    for log in all_logs:
        try:
            log_date = datetime.strptime(log.date, "%Y-%m-%d").date()
            if start <= log_date <= end:
                filtered.append(log)
        except ValueError:
            continue

    df = pd.DataFrame([{
        "UID": log.uid,
        "Action": log.action,
        "Date": log.date,
        "Time": log.time
    } for log in filtered])

    output_file = BASE_DIR / "logs.xlsx"
    df.to_excel(output_file, index=False)
    return str(output_file)

# Webhook from IoT device
@app.post("/api/logs")
async def receive_log(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        uid = data.get('uid')
        action = data.get('action')
        date = data.get('date')
        time = data.get('time')

        if not (uid and action and date and time):
            return {"error": "Missing data"}

        new_log = Log(uid=uid, action=action, date=date, time=time)
        db.add(new_log)
        db.commit()

        return {"message": "Log received successfully"}
    except Exception as e:
        return {"error": str(e)}
