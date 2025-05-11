from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_log(db: Session, log: schemas.LogCreate):
    db_log = models.Log(uid=log.UID, action=log.Action, date=log.Date, time=log.Time)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Log).offset(skip).limit(limit).all()

def get_logs_by_date_range(db: Session, start_date: str, end_date: str):
    return db.query(models.Log).filter(models.Log.date >= start_date, models.Log.date <= end_date).all()
