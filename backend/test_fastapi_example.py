"""
Simple test script to demonstrate the FastAPI example endpoints.
Run this after starting the FastAPI server to test the API.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    """Test various endpoints of the FastAPI example."""
    
    print("🧪 Testing FastAPI Example Endpoints\n")
    
    # Test root endpoint
    print("1. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # Test health check
    print("2. Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # Test creating items
    print("3. Creating sample items...")
    sample_items = [
        {
            "name": "Laptop",
            "description": "High-performance laptop",
            "price": 999.99,
            "is_available": True
        },
        {
            "name": "Mouse",
            "description": "Wireless optical mouse",
            "price": 29.99,
            "is_available": True
        },
        {
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "price": 149.99,
            "is_available": False
        }
    ]
    
    created_items = []
    for item in sample_items:
        response = requests.post(f"{BASE_URL}/items", json=item)
        if response.status_code == 200:
            created_item = response.json()
            created_items.append(created_item)
            print(f"   Created: {created_item['name']} (ID: {created_item['id']})")
        else:
            print(f"   Failed to create item: {response.text}")
    print()
    
    # Test getting all items
    print("4. Getting all items...")
    response = requests.get(f"{BASE_URL}/items")
    print(f"   Status: {response.status_code}")
    print(f"   Found {len(response.json())} items\n")
    
    # Test getting specific item
    if created_items:
        print("5. Getting specific item...")
        item_id = created_items[0]["id"]
        response = requests.get(f"{BASE_URL}/items/{item_id}")
        print(f"   Status: {response.status_code}")
        print(f"   Item: {response.json()}\n")
    
    # Test search functionality
    print("6. Testing search functionality...")
    response = requests.get(f"{BASE_URL}/items/search?min_price=50")
    print(f"   Items with price >= 50: {len(response.json())}")
    
    response = requests.get(f"{BASE_URL}/items/search?available_only=true")
    print(f"   Available items: {len(response.json())}\n")
    
    # Test updating an item
    if created_items:
        print("7. Updating an item...")
        item_id = created_items[0]["id"]
        update_data = {
            "name": "Updated Laptop",
            "description": "Updated description",
            "price": 1099.99,
            "is_available": True
        }
        response = requests.put(f"{BASE_URL}/items/{item_id}", json=update_data)
        print(f"   Status: {response.status_code}")
        print(f"   Updated item: {response.json()}\n")
    
    # Test user orders endpoint
    print("8. Testing user orders endpoint...")
    response = requests.get(f"{BASE_URL}/users/123/orders")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    # Test specific order endpoint
    print("9. Testing specific order endpoint...")
    response = requests.get(f"{BASE_URL}/users/123/orders/1?include_items=true")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}\n")
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    try:
        test_endpoints()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the FastAPI server.")
        print("   Make sure the server is running on http://localhost:8000")
        print("   Run: python run_fastapi_example.py")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
