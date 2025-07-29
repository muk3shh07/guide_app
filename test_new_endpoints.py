#!/usr/bin/env python3
"""
Test script for the updated Guide App API endpoints
Run this after starting the Django server to test the new functionality
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_user_registration():
    """Test user registration with different user types"""
    print("Testing User Registration...")
    
    # Test tourist registration
    tourist_data = {
        "username": "test_tourist",
        "email": "tourist@test.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "Tourist",
        "phone_number": "+1234567890",
        "user_type": "tourist"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=tourist_data)
    print(f"Tourist Registration: {response.status_code}")
    if response.status_code == 201:
        print("✅ Tourist registration successful")
        tourist_token = response.json()['access']
    else:
        print(f"❌ Tourist registration failed: {response.text}")
        return None, None
    
    # Test agency registration
    agency_data = {
        "username": "test_agency",
        "email": "agency@test.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "Agency",
        "phone_number": "+1234567891", 
        "user_type": "agency"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", json=agency_data)
    print(f"Agency Registration: {response.status_code}")
    if response.status_code == 201:
        print("✅ Agency registration successful")
        agency_token = response.json()['access']
    else:
        print(f"❌ Agency registration failed: {response.text}")
        return tourist_token, None
    
    return tourist_token, agency_token

def test_homepage_content():
    """Test homepage content endpoint"""
    print("\nTesting Homepage Content...")
    
    response = requests.get(f"{BASE_URL}/homepage/content/")
    print(f"Homepage Content: {response.status_code}")
    if response.status_code == 200:
        content = response.json()
        print(f"✅ Homepage loaded with {len(content['packages'])} packages, {len(content['guides'])} guides, {len(content['agencies'])} agencies")
    else:
        print(f"❌ Homepage content failed: {response.text}")

def test_public_endpoints():
    """Test public browsing endpoints"""
    print("\nTesting Public Endpoints...")
    
    endpoints = [
        "/packages/",
        "/guides/", 
        "/agencies/"
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"{endpoint}: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ {endpoint} working")
        else:
            print(f"❌ {endpoint} failed: {response.text}")

def test_profile_management(tourist_token, agency_token):
    """Test profile management endpoints"""
    print("\nTesting Profile Management...")
    
    headers_tourist = {"Authorization": f"Bearer {tourist_token}"}
    headers_agency = {"Authorization": f"Bearer {agency_token}"}
    
    # Test tourist profile
    response = requests.get(f"{BASE_URL}/profile/tourist/", headers=headers_tourist)
    print(f"Tourist Profile GET: {response.status_code}")
    if response.status_code == 200:
        print("✅ Tourist profile accessible")
    else:
        print(f"❌ Tourist profile failed: {response.text}")
    
    # Test agency profile
    if agency_token:
        response = requests.get(f"{BASE_URL}/profile/agency/", headers=headers_agency)
        print(f"Agency Profile GET: {response.status_code}")
        if response.status_code == 200:
            print("✅ Agency profile accessible")
        else:
            print(f"❌ Agency profile failed: {response.text}")

def test_booking_endpoints(tourist_token):
    """Test booking endpoints"""
    print("\nTesting Booking Endpoints...")
    
    headers = {"Authorization": f"Bearer {tourist_token}"}
    
    # Test getting bookings
    response = requests.get(f"{BASE_URL}/tourist/bookings/", headers=headers)
    print(f"Tourist Bookings GET: {response.status_code}")
    if response.status_code == 200:
        print("✅ Tourist bookings accessible")
    else:
        print(f"❌ Tourist bookings failed: {response.text}")

def test_rating_endpoints(tourist_token):
    """Test rating endpoints"""
    print("\nTesting Rating Endpoints...")
    
    headers = {"Authorization": f"Bearer {tourist_token}"}
    
    # Test getting ratings
    response = requests.get(f"{BASE_URL}/tourist/ratings/", headers=headers)
    print(f"Tourist Ratings GET: {response.status_code}")
    if response.status_code == 200:
        print("✅ Tourist ratings accessible")
    else:
        print(f"❌ Tourist ratings failed: {response.text}")

def test_agency_management(agency_token):
    """Test agency management endpoints"""
    print("\nTesting Agency Management...")
    
    if not agency_token:
        print("❌ No agency token available")
        return
    
    headers = {"Authorization": f"Bearer {agency_token}"}
    
    # Test agency package management
    response = requests.get(f"{BASE_URL}/agency/manage/packages/", headers=headers)
    print(f"Agency Packages GET: {response.status_code}")
    if response.status_code == 200:
        print("✅ Agency package management accessible")
    else:
        print(f"❌ Agency package management failed: {response.text}")
    
    # Test agency guide management
    response = requests.get(f"{BASE_URL}/agency/manage/guides/", headers=headers)
    print(f"Agency Guides GET: {response.status_code}")
    if response.status_code == 200:
        print("✅ Agency guide management accessible")
    else:
        print(f"❌ Agency guide management failed: {response.text}")

def main():
    """Run all tests"""
    print("🚀 Starting Guide App API Tests...")
    print("=" * 50)
    
    # Test user registration
    tourist_token, agency_token = test_user_registration()
    
    # Test public endpoints
    test_homepage_content()
    test_public_endpoints()
    
    if tourist_token:
        # Test authenticated endpoints
        test_profile_management(tourist_token, agency_token)
        test_booking_endpoints(tourist_token)
        test_rating_endpoints(tourist_token)
        
        if agency_token:
            test_agency_management(agency_token)
    
    print("\n" + "=" * 50)
    print("🏁 Tests completed!")
    print("\nNote: Some tests may fail if:")
    print("- The Django server is not running")
    print("- Database hasn't been migrated")
    print("- Users already exist with the same email")

if __name__ == "__main__":
    main()
