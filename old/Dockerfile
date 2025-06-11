FROM python:3.10.17-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY scripts/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD ["/wait-for-it.sh", "db:5432", "--", "python", "init_db.py", "&&", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
