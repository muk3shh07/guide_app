#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000/api"

echo -e "${BLUE}🧪 Profile Management API Testing Script${NC}"
echo "========================================="

# Function to make HTTP requests and display results
make_request() {
    local method=$1
    local url=$2
    local data=$3
    local headers=$4
    local description=$5
    
    echo -e "\n${YELLOW}📋 Testing: $description${NC}"
    echo -e "${BLUE}$method $url${NC}"
    
    if [ -n "$data" ]; then
        echo -e "${BLUE}Data:${NC} $data"
    fi
    
    if [ -n "$headers" ]; then
        response=$(curl -s -X $method "$url" -H "Content-Type: application/json" -H "$headers" -d "$data")
    else
        response=$(curl -s -X $method "$url" -H "Content-Type: application/json" -d "$data")
    fi
    
    echo -e "${GREEN}Response:${NC}"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    echo "----------------------------------------"
}

# Step 1: Register a new user (Tourist)
echo -e "\n${BLUE}🔐 Step 1: User Registration${NC}"
tourist_data='{
    "username": "test_tourist",
    "email": "tourist@test.com",
    "password": "testpass123",
    "user_type": "tourist",
    "first_name": "John",
    "last_name": "Doe"
}'

make_request "POST" "$BASE_URL/auth/register/" "$tourist_data" "" "Register Tourist User"

# Step 2: Login to get JWT token
echo -e "\n${BLUE}🔑 Step 2: User Login${NC}"
login_data='{
    "email": "tourist@test.com",
    "password": "testpass123"
}'

login_response=$(curl -s -X POST "$BASE_URL/auth/login/" -H "Content-Type: application/json" -d "$login_data")
echo -e "${GREEN}Login Response:${NC}"
echo "$login_response" | python3 -m json.tool

# Extract access token
access_token=$(echo "$login_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)

if [ -z "$access_token" ]; then
    echo -e "${RED}❌ Failed to get access token. Please check login response.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Access token obtained successfully${NC}"
auth_header="Authorization: Bearer $access_token"

# Step 3: Test Tourist Profile Management
echo -e "\n${BLUE}👤 Step 3: Tourist Profile Management${NC}"

# Get tourist profile (should create one if doesn't exist)
make_request "GET" "$BASE_URL/profile/tourist/" "" "$auth_header" "Get Tourist Profile"

# Update tourist profile
tourist_profile_data='{
    "travel_interests": ["beaches", "mountains", "culture"],
    "emergency_contact": "+1234567890",
    "nationality": "American",
    "date_of_birth": "1990-01-15"
}'

make_request "PUT" "$BASE_URL/profile/tourist/" "$tourist_profile_data" "$auth_header" "Update Tourist Profile"

# Step 4: Register a Guide user
echo -e "\n${BLUE}🗺️ Step 4: Guide User Registration${NC}"
guide_data='{
    "username": "test_guide",
    "email": "guide@test.com",
    "password": "testpass123",
    "user_type": "guide",
    "first_name": "Jane",
    "last_name": "Smith"
}'

make_request "POST" "$BASE_URL/auth/register/" "$guide_data" "" "Register Guide User"

# Step 5: Login as Guide
echo -e "\n${BLUE}🔑 Step 5: Guide Login${NC}"
guide_login_data='{
    "email": "guide@test.com",
    "password": "testpass123"
}'

guide_login_response=$(curl -s -X POST "$BASE_URL/auth/login/" -H "Content-Type: application/json" -d "$guide_login_data")
echo -e "${GREEN}Guide Login Response:${NC}"
echo "$guide_login_response" | python3 -m json.tool

# Extract guide access token
guide_access_token=$(echo "$guide_login_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)
guide_auth_header="Authorization: Bearer $guide_access_token"

# Step 6: Test Guide Profile Management
echo -e "\n${BLUE}🗺️ Step 6: Guide Profile Management${NC}"

# Get guide profile
make_request "GET" "$BASE_URL/profile/guide/" "" "$guide_auth_header" "Get Guide Profile"

# Update guide profile
guide_profile_data='{
    "languages": ["English", "Spanish", "French"],
    "specializations": ["City Tours", "Historical Sites", "Food Tours"],
    "hourly_rate": "50.00",
    "daily_rate": "350.00",
    "experience_years": 5,
    "bio": "Experienced local guide with passion for sharing culture and history."
}'

make_request "PUT" "$BASE_URL/profile/guide/" "$guide_profile_data" "$guide_auth_header" "Update Guide Profile"

# Step 7: Register an Agency user
echo -e "\n${BLUE}🏢 Step 7: Agency User Registration${NC}"
agency_data='{
    "username": "test_agency",
    "email": "agency@test.com",
    "password": "testpass123",
    "user_type": "agency",
    "first_name": "Travel",
    "last_name": "Agency"
}'

make_request "POST" "$BASE_URL/auth/register/" "$agency_data" "" "Register Agency User"

# Step 8: Login as Agency
echo -e "\n${BLUE}🔑 Step 8: Agency Login${NC}"
agency_login_data='{
    "email": "agency@test.com",
    "password": "testpass123"
}'

agency_login_response=$(curl -s -X POST "$BASE_URL/auth/login/" -H "Content-Type: application/json" -d "$agency_login_data")
echo -e "${GREEN}Agency Login Response:${NC}"
echo "$agency_login_response" | python3 -m json.tool

# Extract agency access token
agency_access_token=$(echo "$agency_login_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)
agency_auth_header="Authorization: Bearer $agency_access_token"

# Step 9: Test Agency Profile Management
echo -e "\n${BLUE}🏢 Step 9: Agency Profile Management${NC}"

# Get agency profile
make_request "GET" "$BASE_URL/profile/agency/" "" "$agency_auth_header" "Get Agency Profile"

# Update agency profile
agency_profile_data='{
    "company_name": "Best Travel Agency",
    "registration_number": "REG123456",
    "address": "123 Travel Street, Tourism City, TC 12345",
    "website": "https://www.besttravelagency.com",
    "commission_rate": "20.00"
}'

make_request "PUT" "$BASE_URL/profile/agency/" "$agency_profile_data" "$agency_auth_header" "Update Agency Profile"

# Step 10: Test Cross-User Type Access (Should Fail)
echo -e "\n${BLUE}🚫 Step 10: Test Access Control${NC}"

make_request "GET" "$BASE_URL/profile/guide/" "" "$auth_header" "Tourist trying to access Guide profile (should fail)"
make_request "GET" "$BASE_URL/profile/agency/" "" "$auth_header" "Tourist trying to access Agency profile (should fail)"

# Step 11: Test Guide Listing (Public Endpoint)
echo -e "\n${BLUE}📋 Step 11: Public Guide Listing${NC}"

make_request "GET" "$BASE_URL/guides/" "" "" "Get All Guides (Public)"

# Step 12: Test Profile Retrieval via Auth Profile Endpoint
echo -e "\n${BLUE}👤 Step 12: General Profile Endpoint${NC}"

make_request "GET" "$BASE_URL/auth/profile/" "" "$auth_header" "Get Tourist Profile via Auth"
make_request "GET" "$BASE_URL/auth/profile/" "" "$guide_auth_header" "Get Guide Profile via Auth"
make_request "GET" "$BASE_URL/auth/profile/" "" "$agency_auth_header" "Get Agency Profile via Auth"

echo -e "\n${GREEN}✅ All tests completed!${NC}"
echo -e "${BLUE}📝 Summary of Endpoints Tested:${NC}"
echo "1. POST /api/auth/register/ - User Registration"
echo "2. POST /api/auth/login/ - User Login"
echo "3. GET /api/profile/tourist/ - Get Tourist Profile"
echo "4. PUT /api/profile/tourist/ - Update Tourist Profile"
echo "5. GET /api/profile/guide/ - Get Guide Profile"
echo "6. PUT /api/profile/guide/ - Update Guide Profile"
echo "7. GET /api/profile/agency/ - Get Agency Profile"
echo "8. PUT /api/profile/agency/ - Update Agency Profile"
echo "9. GET /api/guides/ - List All Guides (Public)"
echo "10. GET /api/auth/profile/ - Get User Profile with Type-specific Data"
echo -e "\n${YELLOW}💡 Use this script as reference for Postman collection setup!${NC}"
