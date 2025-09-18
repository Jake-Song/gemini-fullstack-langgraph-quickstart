#!/usr/bin/env python3
"""
Simple script to run the FastAPI example application.
"""

import uvicorn
from simple_fastapi_example import app

if __name__ == "__main__":
    print("Starting FastAPI example server...")
    print("Visit http://localhost:8000 for the API")
    print("Visit http://localhost:8000/docs for interactive API documentation")
    print("Visit http://localhost:8000/redoc for alternative API documentation")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
