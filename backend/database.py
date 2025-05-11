


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base

# Replace this with your actual PostgreSQL URL from Render
DATABASE_URL = "postgresql://esp32logs_user:MCnzmWkm1M8jtVWPw3SQd5AHhyP0wr0E@dpg-d0gff5q4d50c73fq54c0-a.oregon-postgres.render.com/esp32logs"

# Create engine and session maker for PostgreSQL
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

