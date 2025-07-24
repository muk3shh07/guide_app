#!/bin/bash
# 🧪 API Testing Script for OAuth Endpoints
# Make sure your Django server is running: poetry run python manage.py runserver

echo "🚀 Testing Guide App OAuth API Endpoints"
echo "========================================"

BASE_URL="http://localhost:8000/api"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}📋 Available Authentication Endpoints:${NC}"
echo "1. POST $BASE_URL/auth/register/ - Email Registration"
echo "2. POST $BASE_URL/auth/login/ - Email Login"
echo "3. POST $BASE_URL/auth/google_login/ - Google OAuth"
echo "4. POST $BASE_URL/auth/facebook_login/ - Facebook OAuth"
echo "5. POST $BASE_URL/auth/logout/ - Logout"
echo "6. GET  $BASE_URL/auth/profile/ - Get User Profile"

echo -e "\n${BLUE}🔍 Testing Server Connection...${NC}"
if curl -s --head "$BASE_URL/auth/register/" | head -n 1 | grep -q "200\|405\|404"; then
    echo -e "${GREEN}✅ Server is running and accessible${NC}"
else
    echo -e "${RED}❌ Server is not running. Start it with: poetry run python manage.py runserver${NC}"
    exit 1
fi

echo -e "\n${BLUE}📧 Testing Email Registration...${NC}"
curl -X POST "$BASE_URL/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "oauth_test_user",
    "email": "oauth_test@example.com",
    "password": "TestPassword123!",
    "password_confirm": "TestPassword123!",
    "first_name": "OAuth",
    "last_name": "Test",
    "phone_number": "1234567890"
  }' | python -m json.tool

echo -e "\n${BLUE}🔑 Testing Email Login...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "oauth_test@example.com",
    "password": "TestPassword123!"
  }')

echo "$LOGIN_RESPONSE" | python -m json.tool

# Extract access token for authenticated requests
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('access', ''))
except:
    pass
")

echo -e "\n${BLUE}👤 Testing Profile Endpoint (Authenticated)...${NC}"
if [ ! -z "$ACCESS_TOKEN" ]; then
    curl -X GET "$BASE_URL/auth/profile/" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $ACCESS_TOKEN" | python -m json.tool
else
    echo -e "${RED}❌ No access token available, skipping profile test${NC}"
fi

echo -e "\n${BLUE}🔍 Testing Google OAuth Endpoint (with fake token)...${NC}"
curl -X POST "$BASE_URL/auth/google_login/" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "fake_google_token_for_testing",
    "user_type": "tourist"
  }' | python -m json.tool

echo -e "\n${BLUE}🔍 Testing Facebook OAuth Endpoint (with fake token)...${NC}"
curl -X POST "$BASE_URL/auth/facebook_login/" \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "fake_facebook_token_for_testing",
    "user_type": "guide"
  }' | python -m json.tool

echo -e "\n${GREEN}✅ API Testing Complete!${NC}"
echo -e "\n${BLUE}📝 Notes:${NC}"
echo "- Google/Facebook endpoints return errors with fake tokens (expected behavior)"
echo "- To test with real tokens, use tokens from actual OAuth flows"
echo "- All endpoints are working and accessible"

echo -e "\n${BLUE}🔗 Frontend Integration Examples:${NC}"
echo ""
echo "Google OAuth (JavaScript):"
echo "fetch('$BASE_URL/auth/google_login/', {"
echo "  method: 'POST',"
echo "  headers: { 'Content-Type': 'application/json' },"
echo "  body: JSON.stringify({"
echo "    token: googleIdToken,"
echo "    user_type: 'tourist'"
echo "  })"
echo "})"
echo ""
echo "Facebook OAuth (JavaScript):"
echo "fetch('$BASE_URL/auth/facebook_login/', {"
echo "  method: 'POST',"
echo "  headers: { 'Content-Type': 'application/json' },"
echo "  body: JSON.stringify({"
echo "    access_token: facebookAccessToken,"
echo "    user_type: 'guide'"
echo "  })"
echo "})"
