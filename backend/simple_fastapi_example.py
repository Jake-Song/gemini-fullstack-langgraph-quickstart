"""
Simple FastAPI Example

This is a basic FastAPI application demonstrating common patterns:
- Basic GET endpoints
- POST endpoints with request body validation
- Path parameters
- Query parameters
- Pydantic models for data validation
- Error handling
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import uvicorn

# Create FastAPI instance
app = FastAPI(
    title="Simple FastAPI Example",
    description="A basic FastAPI application with common endpoints",
    version="1.0.0"
)

# Pydantic models for request/response validation
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

class ItemResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool

# In-memory storage (replace with database in production)
items_db = []
next_id = 1

# Root endpoint
@app.get("/")
async def read_root():
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to the Simple FastAPI Example!", "version": "1.0.0"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "fastapi-example"}

# GET all items
@app.get("/items", response_model=List[ItemResponse])
async def get_items():
    """Get all items from the database."""
    return items_db

# GET item by ID
@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get a specific item by its ID."""
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# POST new item
@app.post("/items", response_model=ItemResponse)
async def create_item(item: Item):
    """Create a new item."""
    global next_id
    new_item = item.dict()
    new_item["id"] = next_id
    next_id += 1
    items_db.append(new_item)
    return new_item

# PUT update item
@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: Item):
    """Update an existing item."""
    for i, existing_item in enumerate(items_db):
        if existing_item["id"] == item_id:
            updated_item = item.dict()
            updated_item["id"] = item_id
            items_db[i] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

# DELETE item
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Delete an item by its ID."""
    for i, item in enumerate(items_db):
        if item["id"] == item_id:
            deleted_item = items_db.pop(i)
            return {"message": f"Item {item_id} deleted successfully", "deleted_item": deleted_item}
    raise HTTPException(status_code=404, detail="Item not found")

# GET items with query parameters
@app.get("/items/search", response_model=List[ItemResponse])
async def search_items(
    name: Optional[str] = Query(None, description="Filter by item name"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    available_only: bool = Query(False, description="Show only available items")
):
    """Search items with various filters."""
    filtered_items = items_db.copy()
    
    if name:
        filtered_items = [item for item in filtered_items if name.lower() in item["name"].lower()]
    
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] >= min_price]
    
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] <= max_price]
    
    if available_only:
        filtered_items = [item for item in filtered_items if item["is_available"]]
    
    return filtered_items

# Example endpoint with path parameters
@app.get("/users/{user_id}/orders")
async def get_user_orders(user_id: int):
    """Example endpoint with path parameters."""
    return {
        "user_id": user_id,
        "orders": [
            {"order_id": 1, "total": 25.99, "status": "completed"},
            {"order_id": 2, "total": 15.50, "status": "pending"}
        ]
    }

# Example endpoint with both path and query parameters
@app.get("/users/{user_id}/orders/{order_id}")
async def get_specific_order(
    user_id: int, 
    order_id: int,
    include_items: bool = Query(False, description="Include order items")
):
    """Get a specific order for a user."""
    order_data = {
        "user_id": user_id,
        "order_id": order_id,
        "total": 25.99,
        "status": "completed",
        "date": "2024-01-15"
    }
    
    if include_items:
        order_data["items"] = [
            {"item_id": 1, "name": "Sample Item", "quantity": 2, "price": 12.99}
        ]
    
    return order_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
