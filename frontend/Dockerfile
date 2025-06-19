FROM python:3.11-slim


# Kopiere die Abhängigkeiten und installiere sie
COPY frontend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir torch --upgrade

# Kopiere den gesamten shared-Ordner
COPY ./shared ./shared

# Kopiere den gesamten Frontend-Code
COPY frontend/. .

# Setze das Skript ausführbar (bereits im shared-Ordner enthalten)
RUN chmod +x ./shared/scripts/wait-for-it.sh

# Starte die Streamlit App
CMD ["./shared/scripts/wait-for-it.sh", "db:5432", "--", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]