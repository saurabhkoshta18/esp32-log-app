
from sqlalchemy.orm import Session
from backend.models import User


def get_user(db: Session, username: str, password: str):
    return db.query(User).filter(User.username == username, User.password == password).first()

def create_user(db: Session, username: str, password: str):
    if db.query(User).filter(User.username == username).first():
        return False
    db.add(User(username=username, password=password))
    db.commit()
    return True
