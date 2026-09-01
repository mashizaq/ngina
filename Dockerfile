FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps
RUN apt-get update \
    && apt-get install -y build-essential gcc libpq-dev git curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# create data dir
RUN mkdir -p /app/data

EXPOSE 5000

CMD ["gunicorn", "wsgi:app", "-w", "4", "-b", "0.0.0.0:5000", "--log-level", "info"]
