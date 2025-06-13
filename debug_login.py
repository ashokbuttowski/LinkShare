import requests
import json

# Use the public endpoint from the frontend .env file
BASE_URL = "https://3ab3ee47-2d6b-4a12-bd71-9b461394abd1.preview.emergentagent.com/api"

def test_register_and_login():
    """Test registration and login with detailed output"""
    # Generate a unique email
    import random
    import string
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"test_{random_str}@example.com"
    password = "TestPassword123!"
    
    print(f"\n=== Testing with email: {email}, password: {password} ===\n")
    
    # 1. Register a new user
    print("1. Registering a new user...")
    register_data = {"email": email, "password": password}
    register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    print(f"Status code: {register_response.status_code}")
    print(f"Response headers: {json.dumps(dict(register_response.headers), indent=2)}")
    
    try:
        register_json = register_response.json()
        print(f"Response body: {json.dumps(register_json, indent=2)}")
        
        if "access_token" in register_json:
            token = register_json["access_token"]
            print(f"Token received: {token[:10]}...")
        else:
            print("No token received in registration response")
            return
    except Exception as e:
        print(f"Error parsing JSON response: {str(e)}")
        print(f"Raw response: {register_response.text}")
        return
    
    # 2. Try to login with the same credentials
    print("\n2. Logging in with registered credentials...")
    login_data = {"email": email, "password": password}
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    print(f"Status code: {login_response.status_code}")
    print(f"Response headers: {json.dumps(dict(login_response.headers), indent=2)}")
    
    try:
        login_json = login_response.json()
        print(f"Response body: {json.dumps(login_json, indent=2)}")
    except Exception as e:
        print(f"Error parsing JSON response: {str(e)}")
        print(f"Raw response: {login_response.text}")
    
    # 3. Try to get user info with the token
    if "access_token" in register_json:
        print("\n3. Getting user info with token...")
        headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        print(f"Status code: {me_response.status_code}")
        print(f"Response headers: {json.dumps(dict(me_response.headers), indent=2)}")
        
        try:
            me_json = me_response.json()
            print(f"Response body: {json.dumps(me_json, indent=2)}")
        except Exception as e:
            print(f"Error parsing JSON response: {str(e)}")
            print(f"Raw response: {me_response.text}")

if __name__ == "__main__":
    test_register_and_login()
