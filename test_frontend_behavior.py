#!/usr/bin/env python3

import requests
import json
import sys
import os

# Test the exact same call that the frontend makes
def test_frontend_behavior():
    # Use the exact same URL that the frontend would use
    backend_url = "https://3ab3ee47-2d6b-4a12-bd71-9b461394abd1.preview.emergentagent.com"
    api_base = f"{backend_url}/api"
    signup_url = f"{api_base}/auth/register"
    
    # Test data - same as frontend would send
    test_user = {
        "email": "frontendtest@example.com", 
        "password": "testpassword123"
    }
    
    print(f"Testing frontend behavior...")
    print(f"Backend URL: {backend_url}")
    print(f"API Base: {api_base}")
    print(f"Signup URL: {signup_url}")
    print(f"Test user: {test_user}")
    
    try:
        # Headers similar to what a browser would send
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (compatible test)'
        }
        
        # Make the request with timeout
        response = requests.post(
            signup_url, 
            json=test_user,
            headers=headers,
            timeout=30
        )
        
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
            
    except requests.exceptions.Timeout:
        print("Request timed out")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {str(e)}")
    except Exception as e:
        print(f"Error making request: {str(e)}")

if __name__ == "__main__":
    test_frontend_behavior()