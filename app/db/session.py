from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from app.config.config import getAppConfig
from typing import Generator

Base = declarative_base()

config = getAppConfig()

# Remove schema query parameter from URL since psycopg2 doesn't understand it
db_url = config.database_url
if '?schema=' in db_url:
    db_url = db_url.split('?schema=')[0]

engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()