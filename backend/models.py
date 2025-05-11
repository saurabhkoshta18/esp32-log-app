from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use Render's PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL")  # This should be set in Render's environment

# DO NOT use 'check_same_thread' for PostgreSQL
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String)
    action = Column(String)
    date = Column(String)
    time = Column(String)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

def create_database():
    Base.metadata.create_all(bind=engine)
