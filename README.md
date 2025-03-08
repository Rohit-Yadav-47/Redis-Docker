# Item Manager API

A containerized FastAPI application for managing items with Redis caching.


## Features

- RESTful API for CRUD operations on items
- Web interface for managing items
- Redis caching for improved performance
- Docker and Kubernetes deployment options
- Static file serving
- Health check endpoint

## Quick Start

The easiest way to run the application is using Docker Compose:

```bash
docker-compose up
```

Then visit [http://localhost:5000](http://localhost:5000) in your browser.

## Project Structure

```
.
├── app.py              # FastAPI application
├── Dockerfile          # Container definition
├── requirements.txt    # Python dependencies
├── start.sh            # Startup script
├── docker-compose.yml  # Docker Compose configuration
├── skaffold.yaml       # Skaffold configuration for Kubernetes
├── static/             # Static web files
│   └── index.html      # Web interface
```

## API Endpoints

### Item Management

- `GET /items/` - List all items
- `GET /items/{item_id}` - Get a specific item
- `POST /items/` - Create a new item
- `PUT /items/{item_id}` - Update an item
- `DELETE /items/{item_id}` - Delete an item

### Redis Management

- `GET /redis/stats` - Get Redis statistics
- `GET /redis/keys` - List all Redis keys

### Other Endpoints

- `GET /health` - Health check
- `GET /random` - Generate random number (just for fun)
- `GET /` - Web interface

## Development

### Prerequisites

- Python 3.9+
- Redis
- Docker (optional)

### Local Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start Redis:
   ```bash
   redis-server
   ```
4. Start the application:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 5000
   ```

### Environment Variables

- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)

## Docker

### Build the image

```bash
docker build -t item-manager .
```

### Run the container

```bash
docker run -p 5000:5000 -e REDIS_HOST=redis item-manager
```


## Data Models

### Item

```json
{
  "id": 1,
  "name": "Item name",
  "description": "Optional item description",
  "price": 19.99,
  "is_active": true
}
```

### ItemCreate (without ID)

```json
{
  "name": "Item name",
  "description": "Optional item description",
  "price": 19.99,
  "is_active": true
}
```

