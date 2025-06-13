#!/usr/bin/env python3

import requests
import json
import sys

# Test the signup endpoint
def test_signup():
    base_url = "http://localhost:8001"
    signup_url = f"{base_url}/api/auth/register"
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    print(f"Testing signup endpoint: {signup_url}")
    print(f"Test user: {test_user}")
    
    try:
        # Make the request
        response = requests.post(signup_url, json=test_user)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.text:
            try:
                response_json = response.json()
                print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response Text: {response.text}")
        else:
            print("Empty response")
            
    except Exception as e:
        print(f"Error making request: {str(e)}")

if __name__ == "__main__":
    test_signup()