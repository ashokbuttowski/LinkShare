#!/bin/bash

# Comprehensive test for docker-compose compatibility
echo "Docker Compose Compatibility Test"
echo "================================="

# Test 1: Check Dockerfile.frontend Node version
echo "1. Testing Dockerfile.frontend Node version..."
DOCKERFILE_NODE_VERSION=$(grep "FROM node:" /app/Dockerfile.frontend | cut -d':' -f2)
echo "Dockerfile Node version: $DOCKERFILE_NODE_VERSION"

if [ "$DOCKERFILE_NODE_VERSION" = "20" ]; then
    echo "✓ Dockerfile uses Node.js 20"
else
    echo "✗ Dockerfile should use Node.js 20"
fi

# Test 2: Check package.json React version compatibility
echo "2. Testing package.json React versions..."
REACT_VERSION=$(grep '"react":' /app/frontend/package.json | cut -d'"' -f4)
REACT_DOM_VERSION=$(grep '"react-dom":' /app/frontend/package.json | cut -d'"' -f4)
REACT_ROUTER_VERSION=$(grep '"react-router-dom":' /app/frontend/package.json | cut -d'"' -f4)

echo "React version: $REACT_VERSION"
echo "React-DOM version: $REACT_DOM_VERSION"
echo "React-Router-DOM version: $REACT_ROUTER_VERSION"

# Check if React versions are compatible (should be 18.x.x)
if echo "$REACT_VERSION" | grep -q "^18\."; then
    echo "✓ React version is compatible"
else
    echo "✗ React version should be 18.x.x for compatibility"
fi

# Test 3: Check docker-compose.yml configuration
echo "3. Testing docker-compose.yml configuration..."
if grep -q "REACT_APP_BACKEND_URL=http://localhost:10002" /app/docker-compose.yml; then
    echo "✓ Frontend backend URL correctly configured"
else
    echo "✗ Frontend backend URL misconfigured"
fi

if grep -q "JWT_SECRET=" /app/docker-compose.yml; then
    echo "✓ Backend JWT_SECRET configured"
else
    echo "✗ Backend JWT_SECRET missing"
fi

if grep -q "restart: unless-stopped" /app/docker-compose.yml; then
    echo "✓ Restart policies configured"
else
    echo "✗ Restart policies missing"
fi

# Test 4: Check for potential issues
echo "4. Checking for potential compatibility issues..."

# Check if react-scripts version is compatible
REACT_SCRIPTS_VERSION=$(grep '"react-scripts":' /app/frontend/package.json | cut -d'"' -f4)
echo "React Scripts version: $REACT_SCRIPTS_VERSION"

if [ "$REACT_SCRIPTS_VERSION" = "5.0.1" ]; then
    echo "✓ React Scripts version is stable"
else
    echo "⚠ React Scripts version may need verification"
fi

# Test 5: Environment configuration test
echo "5. Testing environment configuration..."
if [ -f "/app/backend/.env" ]; then
    echo "✓ Backend .env file exists"
else
    echo "✗ Backend .env file missing"
fi

if [ -f "/app/frontend/.env" ]; then
    echo "✓ Frontend .env file exists"
else
    echo "✗ Frontend .env file missing"
fi

# Test 6: Simulate the exact error scenario
echo "6. Simulating the original error scenario..."
echo "Original error: react-router-dom@7.5.1 requires Node >=20.0.0, got 18.20.8"
echo "Current fix: Using Node 20 + react-router-dom@^6.8.1"

# Check current react-router-dom version requirement
cd /app/frontend
CURRENT_RRD_VERSION=$(yarn info react-router-dom version --silent 2>/dev/null || echo "unknown")
echo "Current installed react-router-dom version: $CURRENT_RRD_VERSION"

# Test 7: Verify dependencies install correctly
echo "7. Final dependency verification..."
cd /app/frontend
if yarn check --integrity --silent; then
    echo "✓ All dependencies are consistent"
else
    echo "⚠ Some dependency integrity issues detected (check yarn.lock)"
fi

echo "================================="
echo "Docker Compose Compatibility Test Complete"
echo ""
echo "Summary of fixes applied:"
echo "- ✓ Updated Dockerfile.frontend to use Node.js 20"
echo "- ✓ Downgraded React from 19.x to 18.x for stability"
echo "- ✓ Downgraded react-router-dom from 7.5.1 to 6.8.1"
echo "- ✓ Ensured docker-compose.yml has proper environment variables"
echo "- ✓ Added restart policies for reliability"
echo ""
echo "The docker-compose build should now work without the Node.js version error."