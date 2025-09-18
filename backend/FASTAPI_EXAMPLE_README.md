# Simple FastAPI Example

This is a basic FastAPI application demonstrating common patterns and features.

## Features

- **Basic CRUD operations** for items (Create, Read, Update, Delete)
- **Pydantic models** for request/response validation
- **Path parameters** and **query parameters**
- **Error handling** with HTTP exceptions
- **Automatic API documentation** (Swagger UI and ReDoc)
- **Type hints** throughout the codebase

## Available Endpoints

### Core Endpoints
- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint

### Item Management
- `GET /items` - Get all items
- `GET /items/{item_id}` - Get specific item by ID
- `POST /items` - Create new item
- `PUT /items/{item_id}` - Update existing item
- `DELETE /items/{item_id}` - Delete item by ID
- `GET /items/search` - Search items with filters

### Example Endpoints
- `GET /users/{user_id}/orders` - Get user orders
- `GET /users/{user_id}/orders/{order_id}` - Get specific order

## Quick Start

### 1. Install Dependencies
The required dependencies are already in your `pyproject.toml`, but if you need to install them:

```bash
cd backend
uv sync
```

### 2. Run the FastAPI Server

```bash
# Option 1: Using the run script
python run_fastapi_example.py

# Option 2: Direct uvicorn command
uvicorn simple_fastapi_example:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative Documentation (ReDoc)**: http://localhost:8000/redoc

### 4. Test the API

```bash
# Run the test script (make sure the server is running first)
python test_fastapi_example.py
```

## Example Usage

### Create an Item
```bash
curl -X POST "http://localhost:8000/items" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Laptop",
       "description": "High-performance laptop",
       "price": 999.99,
       "is_available": true
     }'
```

### Get All Items
```bash
curl -X GET "http://localhost:8000/items"
```

### Search Items
```bash
# Search by minimum price
curl -X GET "http://localhost:8000/items/search?min_price=100"

# Search available items only
curl -X GET "http://localhost:8000/items/search?available_only=true"

# Search by name
curl -X GET "http://localhost:8000/items/search?name=laptop"
```

## Key FastAPI Concepts Demonstrated

1. **Automatic Request Validation**: FastAPI automatically validates request bodies using Pydantic models
2. **Type Hints**: All function parameters and return types are annotated
3. **Automatic Documentation**: OpenAPI schema is generated automatically
4. **Dependency Injection**: Query parameters are handled automatically
5. **Error Handling**: HTTP exceptions for proper error responses
6. **Response Models**: Automatic serialization of response data

## Project Structure

```
backend/
├── simple_fastapi_example.py    # Main FastAPI application
├── run_fastapi_example.py       # Script to run the server
├── test_fastapi_example.py      # Test script for the API
└── FASTAPI_EXAMPLE_README.md    # This file
```

## Next Steps

To extend this example, you could:

1. **Add a Database**: Replace the in-memory storage with a real database (SQLite, PostgreSQL, etc.)
2. **Add Authentication**: Implement JWT or OAuth2 authentication
3. **Add Middleware**: CORS, logging, rate limiting
4. **Add Background Tasks**: For long-running operations
5. **Add WebSocket Support**: For real-time communication
6. **Add File Upload**: For handling file uploads
7. **Add Testing**: Unit tests with pytest
8. **Add Docker**: Containerize the application

## Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
