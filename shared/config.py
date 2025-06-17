import os

# Zentrale Datenbank-URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:example@db:5432/cocking_db")