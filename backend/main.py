from pydantic import BaseModel
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend import auth
from backend.auth import get_user, create_user
from backend import models
from backend.models import Base, engine, Log, User
from backend import database
from backend.database import get_db
from datetime import datetime
import uvicorn
import pandas as pd
import os

class LogInput(BaseModel):
    UID: str
    Action: str
    Date: str
    Time: str

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

@app.get("/", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": ""})

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = get_user(db, username, password)
    if user:
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie("username", username)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "message": "Invalid credentials"})

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "message": ""})

@app.post("/register", response_class=HTMLResponse)
def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    success = create_user(db, username, password)
    if success:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request, "message": "User already exists"})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    logs = db.query(Log).order_by(Log.id.desc()).limit(50).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "logs": logs})

@app.get("/download", response_class=HTMLResponse)
def download_page(request: Request):
    return templates.TemplateResponse("download.html", {"request": request})

@app.post("/download", response_class=HTMLResponse)
def download(request: Request, start_date: str = Form(...), end_date: str = Form(...), db: Session = Depends(get_db)):
    logs = db.query(Log).filter(Log.date >= start_date, Log.date <= end_date).all()
    filename = "logs.xlsx"
    df = pd.DataFrame([{
        "UID": log.uid,
        "Action": log.action,
        "Date": log.date,
        "Time": log.time
    } for log in logs])
    df.to_excel(filename, index=False)
    return templates.TemplateResponse("download.html", {"request": request, "download_link": f"/static/{filename}"})

@app.post("/api/logs")
def receive_log(log: LogInput, db: Session = Depends(get_db)):
    new_log = Log(
        uid=log.UID,
        action=log.Action,
        date=log.Date,
        time=log.Time
    )
    db.add(new_log)
    db.commit()
    return {"status": "received"}
