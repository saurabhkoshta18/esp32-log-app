# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import models, schemas, crud, auth, database, excel_export
from database import engine, SessionLocal
from datetime import datetime
import io
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="frontend/templates")
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username)
    if user:
        return templates.TemplateResponse("register.html", {"request": {}, "error": "Username already exists"})
    crud.create_user(db, username, password)
    return RedirectResponse(url="/", status_code=303)

@app.post("/login")
def login_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": {}, "error": "Invalid credentials"})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie("user", username)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("user")
    if not username:
        return RedirectResponse(url="/")
    logs = crud.get_logs(db)
    return templates.TemplateResponse("dashboard.html", {"request": request, "logs": logs, "user": username})

@app.get("/refresh")
def refresh_logs(db: Session = Depends(get_db)):
    logs = crud.get_logs(db)
    return {"logs": [log.as_dict() for log in logs]}

@app.post("/log")
def receive_log(log: schemas.LogCreate, db: Session = Depends(get_db)):
    crud.create_log(db, log)
    return {"message": "Log stored successfully"}

@app.get("/download", response_class=HTMLResponse)
def download_page(request: Request):
    username = request.cookies.get("user")
    if not username:
        return RedirectResponse(url="/")
    return templates.TemplateResponse("download.html", {"request": request})

@app.post("/download")
def download_excel(start_date: str = Form(...), end_date: str = Form(...), db: Session = Depends(get_db)):
    logs = crud.get_logs_by_date_range(db, start_date, end_date)
    file = excel_export.export_logs_to_excel(logs)
    return StreamingResponse(io.BytesIO(file), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=logs.xlsx"})
