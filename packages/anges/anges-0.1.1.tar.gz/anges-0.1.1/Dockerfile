FROM python:3.12.7-slim

RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

EXPOSE 5005

# Updated entry point to use new anges ui command
CMD anges ui --password ${APP_PASSWORD} --port 5005 --host 0.0.0.0
