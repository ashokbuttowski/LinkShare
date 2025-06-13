#!/usr/bin/env python3

import requests
import json
import sys
import time

def test_signup_with_debugging():
    """Test signup with detailed error analysis"""
    backend_url = "https://3ab3ee47-2d6b-4a12-bd71-9b461394abd1.preview.emergentagent.com"
    api_base = f"{backend_url}/api"
    
    # Test both login and register endpoints
    endpoints = [
        ('/auth/register', 'POST'),
        ('/auth/login', 'POST')
    ]
    
    test_user = {
        "email": "debugtest@example.com",
        "password": "testpassword123"
    }
    
    for endpoint, method in endpoints:
        url = f"{api_base}{endpoint}"
        print(f"\n{'='*60}")
        print(f"Testing {method} {url}")
        print(f"User data: {test_user}")
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Origin': 'https://3ab3ee47-2d6b-4a12-bd71-9b461394abd1.preview.emergentagent.com',
                'User-Agent': 'Mozilla/5.0 (compatible frontend test)'
            }
            
            if method == 'POST':
                response = requests.post(url, json=test_user, headers=headers, timeout=30)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.text:
                try:
                    response_json = response.json()
                    print(f"Response JSON: {json.dumps(response_json, indent=2)}")
                except json.JSONDecodeError:
                    print(f"Raw Response Text: {response.text}")
            
            # Check if there are any specific error details
            if response.status_code >= 400:
                print(f"ERROR: HTTP {response.status_code}")
                if response.headers.get('content-type', '').startswith('application/json'):
                    error_data = response.json()
                    print(f"Error detail: {error_data.get('detail', 'No detail provided')}")
                    
        except requests.exceptions.Timeout:
            print("ERROR: Request timed out")
        except requests.exceptions.ConnectionError as e:
            print(f"ERROR: Connection error: {str(e)}")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Request exception: {str(e)}")
        except Exception as e:
            print(f"ERROR: Unexpected error: {str(e)}")
    
    # Also test the health endpoint
    print(f"\n{'='*60}")
    print("Testing health endpoint...")
    try:
        health_url = f"{api_base}/health"
        response = requests.get(health_url, timeout=10)
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
        else:
            print(f"Health check failed: {response.text}")
    except Exception as e:
        print(f"Health check error: {str(e)}")

if __name__ == "__main__":
    test_signup_with_debugging()