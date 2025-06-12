from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from shared.config import DATABASE_URL  # Zentrale Konfiguration

engine = create_engine(DATABASE_URL, connect_args={
                       "check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()