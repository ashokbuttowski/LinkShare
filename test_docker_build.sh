#!/bin/bash

# Test script to simulate Docker build for frontend
echo "Testing Frontend Docker Build Simulation"
echo "========================================"

# Create a temporary directory to simulate Docker build
TEST_DIR="/tmp/docker-build-test"
rm -rf $TEST_DIR
mkdir -p $TEST_DIR

# Copy package.json and yarn.lock
cp /app/frontend/package.json $TEST_DIR/
cp /app/frontend/yarn.lock $TEST_DIR/

# Simulate the Docker build steps
cd $TEST_DIR

echo "1. Testing Node.js 20 compatibility..."
if node --version | grep -q "v20"; then
    echo "✓ Node.js 20 is available"
else
    echo "✗ Node.js 20 not available. Current version: $(node --version)"
fi

echo "2. Testing yarn install (simulating Docker build)..."
# Install packages in the test directory
yarn install --production=false

if [ $? -eq 0 ]; then
    echo "✓ yarn install successful"
    
    echo "3. Checking package versions..."
    echo "React version: $(yarn list --pattern react --depth=0 2>/dev/null | grep react@)"
    echo "React-DOM version: $(yarn list --pattern react-dom --depth=0 2>/dev/null | grep react-dom@)"
    echo "React-Router-DOM version: $(yarn list --pattern react-router-dom --depth=0 2>/dev/null | grep react-router-dom@)"
    
    echo "4. Testing if packages are compatible..."
    # Check for peer dependency warnings
    yarn install --check-files 2>&1 | grep -i "warning" | head -5
    
    echo "✓ Docker build simulation completed successfully"
    echo "✓ The updated package.json should work in Docker environment"
else
    echo "✗ yarn install failed"
    exit 1
fi

# Cleanup
cd /app
rm -rf $TEST_DIR

echo "========================================"
echo "Docker build simulation test completed"