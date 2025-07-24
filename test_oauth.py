#!/usr/bin/env python
"""
Test script for Google and Facebook OAuth authentication
"""
import os
import sys
import django
import json
import requests

# Add the project directory to the Python path
sys.path.append('/home/mukesh/Documents/guide_app')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import User
from core.serializers import GoogleOAuthSerializer, FacebookOAuthSerializer


def test_google_oauth():
    """Test Google OAuth authentication endpoint"""
    print("🔍 Testing Google OAuth Authentication...")
    
    # This would normally be a real Google ID token from the frontend
    # For testing purposes, you would need to get a real token
    test_data = {
        'token': 'fake_google_token_for_testing',
        'user_type': 'tourist'
    }
    
    try:
        serializer = GoogleOAuthSerializer(data=test_data)
        if serializer.is_valid():
            print("✅ Google OAuth serializer validation passed")
        else:
            print("❌ Google OAuth serializer validation failed:")
            print(json.dumps(serializer.errors, indent=2))
    except Exception as e:
        print(f"❌ Google OAuth test failed: {str(e)}")


def test_facebook_oauth():
    """Test Facebook OAuth authentication endpoint"""
    print("\n🔍 Testing Facebook OAuth Authentication...")
    
    # This would normally be a real Facebook access token from the frontend
    # For testing purposes, you would need to get a real token
    test_data = {
        'access_token': 'fake_facebook_token_for_testing',
        'user_type': 'guide'
    }
    
    try:
        serializer = FacebookOAuthSerializer(data=test_data)
        if serializer.is_valid():
            print("✅ Facebook OAuth serializer validation passed")
        else:
            print("❌ Facebook OAuth serializer validation failed:")
            print(json.dumps(serializer.errors, indent=2))
    except Exception as e:
        print(f"❌ Facebook OAuth test failed: {str(e)}")


def test_api_endpoints():
    """Test the API endpoints are accessible"""
    print("\n🔍 Testing API endpoint accessibility...")
    
    base_url = "http://localhost:8000/api"
    
    endpoints = [
        f"{base_url}/auth/google_login/",
        f"{base_url}/auth/facebook_login/",
        f"{base_url}/auth/register/",
        f"{base_url}/auth/login/",
    ]
    
    for endpoint in endpoints:
        try:
            # Just test that the endpoint exists (should return 405 for GET when POST is expected)
            response = requests.get(endpoint, timeout=5)
            if response.status_code in [200, 405]:  # 405 = Method Not Allowed is expected
                print(f"✅ Endpoint accessible: {endpoint}")
            else:
                print(f"⚠️  Endpoint returned {response.status_code}: {endpoint}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Server not running or endpoint not accessible: {endpoint}")
        except Exception as e:
            print(f"❌ Error testing endpoint {endpoint}: {str(e)}")


def show_user_models():
    """Show existing users and their authentication methods"""
    print("\n👥 Current Users in Database:")
    
    users = User.objects.all()
    if not users.exists():
        print("No users found in database")
        return
    
    for user in users:
        print(f"📧 {user.email}")
        print(f"   - Username: {user.username}")
        print(f"   - Provider: {user.provider}")
        print(f"   - User Type: {user.user_type}")
        print(f"   - Google ID: {user.google_id or 'Not linked'}")
        print(f"   - Facebook ID: {user.facebook_id or 'Not linked'}")
        print(f"   - Verified: {user.is_verified}")
        print("-" * 50)


def main():
    """Main test function"""
    print("🚀 Starting OAuth Authentication Tests\n")
    
    # Test serializers
    test_google_oauth()
    test_facebook_oauth()
    
    # Test API endpoints (only if server is running)
    test_api_endpoints()
    
    # Show current users
    show_user_models()
    
    print("\n📋 Test Summary:")
    print("1. OAuth serializers have been created")
    print("2. API endpoints have been configured")
    print("3. Database models have been updated")
    print("4. Migration has been applied")
    
    print("\n📝 Next Steps:")
    print("1. Set up your Google OAuth2 credentials in .env file")
    print("2. Set up your Facebook App credentials in .env file") 
    print("3. Start the Django server: poetry run python manage.py runserver")
    print("4. Test the endpoints with real tokens from your frontend")
    
    print("\n🔗 New API Endpoints:")
    print("POST /api/auth/google_login/")
    print("   Body: {\"token\": \"google_id_token\", \"user_type\": \"tourist\"}")
    print("POST /api/auth/facebook_login/")
    print("   Body: {\"access_token\": \"facebook_access_token\", \"user_type\": \"guide\"}")


if __name__ == "__main__":
    main()
