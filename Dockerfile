FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system libraries needed by psycopg2 and Pillow
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

# Collect static files at build time (dummy key since no DB needed here)
RUN DJANGO_SECRET_KEY=build-collect-static python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
