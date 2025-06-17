FROM python:3.11-slim


# Kopiere die Abhängigkeiten und installiere sie
COPY services/vorrat_service/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den gesamten shared-Ordner
COPY shared ./shared

# Kopiere den restlichen Code des Services
COPY services/vorrat_service/. .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]