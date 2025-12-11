from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings
from urllib.parse import urlparse

# Use connect_args={"check_same_thread": False} only for SQLite
connect_args = {}
if "sqlite" in settings.DATABASE_URL:
    connect_args = {"check_same_thread": False}
else:
    # Enable TLS for Railway MySQL proxy if detected
    parsed = urlparse(settings.DATABASE_URL)
    host = parsed.hostname or ""
    if parsed.scheme.startswith("mysql+pymysql") and (
        "proxy.rlwy.net" in host or "railway" in host
    ):
        connect_args = {"ssl": {"ssl": {}}}

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
