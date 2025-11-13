FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV APP_IP=0.0.0.0

ENV APP_PORT=5000

EXPOSE ${APP_PORT}

ENV FLASK_ENV=production

CMD ["python", "app.py"]