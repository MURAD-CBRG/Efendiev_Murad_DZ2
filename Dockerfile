FROM python:3.12-slim

WORKDIR /app

# Сначала зависимости — кэшируется
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем код + конфиг
COPY main.py .
COPY config.json .

CMD ["python", "-u", "main.py"]