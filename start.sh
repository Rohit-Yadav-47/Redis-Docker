#!/bin/bash
# Start Redis server in the background
redis-server --daemonize yes

# Start the FastAPI application
uvicorn app:app --host 0.0.0.0 --port 5000
