import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_user_login():
    """Test user login endpoint"""
    print("\n=== Testing User Login ===")
    
    login_data = {
        "username": "tourist_user",
        "password": "testpass123"
    }
    
    print(f"Logging in user: {login_data['username']}")
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"User: {data['user']['username']}")
        print(f"Token: {data['token']}")
        print(f"User Type: {data['user']['user_type']}")
        return data['token']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Error: {response.json()}")
        return None