FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy static files first
COPY static/ /app/static/

# Then copy the application code
COPY app.py .

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 5000

# Start FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]