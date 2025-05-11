from sqlalchemy import Column, Integer, String, Date, Time
from database import Base

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, index=True)
    action = Column(String)
    date = Column(String)
    time = Column(String)

    def as_dict(self):
        return {"UID": self.uid, "Action": self.action, "Date": self.date, "Time": self.time}

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
