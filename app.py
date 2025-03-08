from fastapi import FastAPI, HTTPException, Query, Path, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import random
import redis
import json
import os

# Initialize Redis connection
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

app = FastAPI(
    title="Sample API",
    description="A sample API with multiple endpoints",
    version="1.0.0"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Sample data models
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    is_active: bool = True

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_active: bool = True

# Sample database (in-memory)
items_db = [
    Item(id=1, name="Item 1", description="This is item 1", price=19.99),
    Item(id=2, name="Item 2", description="This is item 2", price=29.99),
    Item(id=3, name="Item 3", description="This is item 3", price=39.99),
]

# Cache middleware helper
def get_cache_item(item_id: int):
    cached_item = redis_client.get(f"item:{item_id}")
    if cached_item:
        return json.loads(cached_item)
    return None

def set_cache_item(item_id: int, item_data):
    redis_client.setex(f"item:{item_id}", 3600, json.dumps(item_data))  # Cache for 1 hour

# Serve index.html at the root URL
@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse('static/index.html')

# Health check endpoint
@app.get("/health")
async def health_check():
    redis_status = "healthy" if redis_client.ping() else "unhealthy"
    return {"status": "healthy", "redis": redis_status}

# Get all items
@app.get("/items/", response_model=List[Item])
async def get_all_items(skip: int = 0, limit: int = 10):
    return items_db[skip:skip + limit]

# Get a specific item by ID
@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int = Path(..., description="The ID of the item to retrieve")):
    # Try to get item from cache first
    cached_item = get_cache_item(item_id)
    if cached_item:
        return Item(**cached_item)
        
    # If not in cache, get from database
    for item in items_db:
        if item.id == item_id:
            # Store in cache for future requests
            set_cache_item(item_id, item.dict())
            return item
            
    raise HTTPException(status_code=404, detail="Item not found")

# Create a new item
@app.post("/items/", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    # Generate a new ID
    new_id = max([i.id for i in items_db]) + 1 if items_db else 1
    new_item = Item(id=new_id, **item.dict())
    items_db.append(new_item)
    
    # Update cache
    set_cache_item(new_id, new_item.dict())
    
    return new_item

# Update an item
@app.put("/items/{item_id}", response_model=Item)
async def update_item(
    item_id: int = Path(..., description="The ID of the item to update"),
    item_update: ItemCreate = ...,
):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            updated_item = Item(id=item_id, **item_update.dict())
            items_db[i] = updated_item
            
            # Update cache
            set_cache_item(item_id, updated_item.dict())
            
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

# Delete an item
@app.delete("/items/{item_id}", response_model=dict)
async def delete_item(item_id: int = Path(..., description="The ID of the item to delete")):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            del items_db[i]
            
            # Delete from cache
            redis_client.delete(f"item:{item_id}")
            
            return {"message": f"Item {item_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")

# Redis specific endpoints
@app.get("/redis/stats")
async def get_redis_stats():
    info = redis_client.info()
    return {
        "used_memory": info.get("used_memory_human", "N/A"),
        "clients": info.get(    "connected_clients", "N/A"),
        "uptime": info.get("uptime_in_seconds", "N/A")
    }

@app.get("/redis/keys")
async def get_redis_keys():
    keys = redis_client.keys("*")
    return {"keys": keys}

# Random endpoint for fun
@app.get("/random")
async def get_random_number(min_val: int = 1, max_val: int = 100):
    # Use Redis to store and return the last generated number
    random_number = random.randint(min_val, max_val)
    redis_client.set("last_random", str(random_number))
    return {
        "random_number": random_number,
        "last_random": redis_client.get("last_random")
    }

# Just for demonstration purposes
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "current_user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
