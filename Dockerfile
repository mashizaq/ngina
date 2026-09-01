FROM python:3.11-slim

# Create a non-root user for security
RUN useradd -m appuser

WORKDIR /app

# Upgrade pip and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files and change ownership
COPY --chown=appuser:appuser . /app

# Switch to the non-root user
USER appuser

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

# Use python to run Flask directly for better signal handling
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
