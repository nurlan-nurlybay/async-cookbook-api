FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure execution rights
RUN chmod +x entrypoint.sh

# We use ENTRYPOINT so that the command in docker-compose is passed as an argument
ENTRYPOINT ["./entrypoint.sh"]
