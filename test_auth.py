"""
Test authentication endpoints
"""
import requests
import json
# from rest_framework.authtoken.models import Token

BASE_URL = "http://localhost:8000/api"

def test_user_registration():
    """Test user registration endpoint"""
    print("=== Testing User Registration ===")
    
    # Test data for different user types
    test_users = [
        {
            "username": "tourist_user",
            "email": "tourist@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "user_type": "tourist",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+9779841234567"
        },
        {
            "username": "guide_user",
            "email": "guide@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "user_type": "guide",
            "first_name": "Ram",
            "last_name": "Bahadur",
            "phone_number": "+9779841234568"
        },
        {
            "username": "agency_user",
            "email": "agency@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "user_type": "agency",
            "first_name": "Agency",
            "last_name": "Owner",
            "phone_number": "+9779841234569"
        }
    ]
    
    for user_data in test_users:
        print(f"\nRegistering {user_data['user_type']}: {user_data['username']}")
        
        response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Registration successful!")
            print(f"User ID: {data['user']['id']}")
            print(f"Token: {data['token'][:20]}...")
            print(f"User Type: {data['user']['user_type']}")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Error: {response.json()}")
        
        print("-" * 50)

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

def test_authenticated_request(token):
    """Test making authenticated requests"""
    print("\n=== Testing Authenticated Request ===")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    # Test getting user's tourist profile
    response = requests.get(f"{BASE_URL}/tourists/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Authenticated request successful!")
        print(f"Tourist profile data: {json.dumps(data, indent=2)}")
    else:
        print(f"❌ Authenticated request failed: {response.status_code}")
        print(f"Error: {response.json()}")

def test_logout(token):
    """Test user logout"""
    print("\n=== Testing User Logout ===")
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/auth/logout/", headers=headers)
    
    if response.status_code == 200:
        print("✅ Logout successful!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Logout failed: {response.status_code}")
        print(f"Error: {response.json()}")

def test_invalid_login():
    """Test login with invalid credentials"""
    print("\n=== Testing Invalid Login ===")
    
    invalid_data = {
        "username": "nonexistent_user",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", json=invalid_data)
    
    if response.status_code == 400:
        print("✅ Invalid login correctly rejected!")
        print(f"Error message: {response.json()}")
    else:
        print(f"❌ Unexpected response: {response.status_code}")

def main():
    print("🚀 Starting Authentication Tests")
    print("Make sure your Django server is running on http://localhost:8000")
    print("=" * 60)
    
    try:
        # Test registration
        test_user_registration()
        
        # Test login
        token = test_user_login()
        
        if token:
            # Test authenticated request
            test_authenticated_request(token)
            
            # Test logout
            test_logout(token)
        
        # Test invalid login
        test_invalid_login()
        
        print("\n" + "=" * 60)
        print("🎉 Authentication tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Django server.")
        print("Make sure the server is running: python manage.py runserver")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
