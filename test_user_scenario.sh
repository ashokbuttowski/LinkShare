#!/bin/bash

# Test script to simulate the exact user scenario
echo "Testing LinkShare Application - User Signup Flow"
echo "================================================="

# Test 1: Check if backend is accessible via the docker-compose URL
echo "1. Testing backend accessibility via docker-compose URL..."
BACKEND_URL="http://localhost:10002"
echo "Testing: $BACKEND_URL/api/health"

curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" "$BACKEND_URL/api/health" 2>/dev/null || echo "Backend not accessible via docker-compose URL"

# Test 2: Check if current backend is accessible
echo "2. Testing current backend setup..."
CURRENT_BACKEND="https://3ab3ee47-2d6b-4a12-bd71-9b461394abd1.preview.emergentagent.com"
echo "Testing: $CURRENT_BACKEND/api/health"

curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" "$CURRENT_BACKEND/api/health" 2>/dev/null || echo "Current backend not accessible"

# Test 3: Test signup with current backend
echo "3. Testing signup with current backend..."
SIGNUP_URL="$CURRENT_BACKEND/api/auth/register"
TEST_USER='{"email": "scriptest@example.com", "password": "testpassword123"}'

RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$TEST_USER" \
  "$SIGNUP_URL" 2>/dev/null)

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✓ Signup successful with current backend"
else
    echo "✗ Signup failed with current backend"
    echo "Response: $RESPONSE"
fi

# Test 4: Check docker-compose configuration
echo "4. Checking docker-compose configuration..."
if [ -f "docker-compose.yml" ]; then
    echo "✓ docker-compose.yml exists"
    
    # Check if the backend URL is correctly configured
    COMPOSE_BACKEND_URL=$(grep -A 5 "environment:" docker-compose.yml | grep "REACT_APP_BACKEND_URL" | cut -d'=' -f2)
    echo "Docker-compose backend URL: $COMPOSE_BACKEND_URL"
    
    if [ "$COMPOSE_BACKEND_URL" = "http://localhost:10002" ]; then
        echo "✓ Backend URL correctly configured for docker-compose"
    else
        echo "✗ Backend URL misconfigured for docker-compose"
    fi
else
    echo "✗ docker-compose.yml not found"
fi

# Test 5: Check for potential issues
echo "5. Checking for potential issues..."

# Check if MongoDB is running
if pgrep mongod > /dev/null; then
    echo "✓ MongoDB is running"
else
    echo "✗ MongoDB is not running"
fi

# Check if current services are running
if pgrep -f "uvicorn" > /dev/null; then
    echo "✓ Backend (uvicorn) is running"
else
    echo "✗ Backend (uvicorn) is not running"
fi

if pgrep -f "react-scripts" > /dev/null; then
    echo "✓ Frontend (react-scripts) is running"
else
    echo "✗ Frontend (react-scripts) is not running"
fi

echo "================================================="
echo "Test completed. If user is running docker-compose and getting auth errors,"
echo "the issue is likely that the backend is not accessible at http://localhost:10002"
echo "when running in docker-compose mode."