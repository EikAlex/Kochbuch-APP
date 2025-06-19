from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={
                       "check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# # Initialize test data
# def initialize_database():
#     db = SessionLocal()
#     try:
#         initialize_default_zutaten(db)
#         initialize_test_rezept(db)
#     except Exception as e:
#         print(f"Error initializing database: {e}")
#     finally:
#         db.close()

# # Call the initialization function
# initialize_database()
