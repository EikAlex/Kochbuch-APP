FROM python:3.11-slim

# Installiere die PostgreSQL-Entwicklungsbibliotheken
# RUN apt-get update && apt-get install -y libpq-dev gcc

# Installiere die Python-Abhängigkeiten 
RUN pip install sqlalchemy psycopg2-binary

COPY ../shared ./shared
COPY services/init_service/init_db.py .

# COPY ./wait-for-it.sh /wait-for-it.sh
# RUN chmod +x /wait-for-it.sh
CMD ["python", "/init_db.py"]