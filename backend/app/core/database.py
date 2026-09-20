from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    try:
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=20, max_overflow=10)
        with engine.connect() as conn:
            pass
    except Exception as e:
        print(f"⚠️ Could not connect to PostgreSQL database ({e}). Falling back to local SQLite.")
        sqlite_url = "sqlite:///./pravi_id.db"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
