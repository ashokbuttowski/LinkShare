import requests
import unittest
import random
import string
import time
import json
from datetime import datetime

# Use the public endpoint from the frontend .env file
BASE_URL = "https://3ab3ee47-2d6b-4a12-bd71-9b461394abd1.preview.emergentagent.com/api"

def random_email():
    """Generate a random email for testing"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"test_{random_str}@example.com"

def random_password():
    """Generate a random password for testing"""
    return "TestPassword123!"  # Using a fixed password for consistency

# Test URLs for metadata extraction
TEST_URLS = {
    "github": "https://github.com",
    "stackoverflow": "https://stackoverflow.com",
    "example": "https://example.com",
    "httpbin": "https://httpbin.org/html",
    "nonexistent": "https://nonexistent-domain-for-testing-123456.com"
}

class LinkShareAPITest(unittest.TestCase):
    """Test suite for LinkShare API"""
    
    def setUp(self):
        """Setup for each test - create a test user"""
        self.email = random_email()
        self.password = random_password()
        self.token = None
        self.test_links = []
    
    def test_01_health_check(self):
        """Test the health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        print("✅ Health check endpoint is working")
    
    def test_02_register_user(self):
        """Test user registration"""
        data = {"email": self.email, "password": self.password}
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.token = data["access_token"]
        print(f"✅ User registration successful with email: {self.email}")
    
    def test_03_register_duplicate_email(self):
        """Test registration with duplicate email"""
        # First register a user
        email = random_email()
        password = random_password()
        data = {"email": email, "password": password}
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        self.assertEqual(response.status_code, 200)
        
        # Try to register again with the same email
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        
        # The API should return 400 for duplicate emails
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Email already registered")
        print("✅ Duplicate email registration properly rejected")
    
    def test_04_login_user(self):
        """Test user login"""
        # First register a user to ensure we have valid credentials
        email = random_email()
        password = random_password()
        register_data = {"email": email, "password": password}
        register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        self.assertEqual(register_response.status_code, 200)
        
        # Now try to login with those credentials
        login_data = {"email": email, "password": password}
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        # Debug output
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")
        
        self.assertEqual(login_response.status_code, 200)
        data = login_response.json()
        self.assertIn("access_token", data)
        self.token = data["access_token"]
        
        # Save the email for other tests
        self.email = email
        self.password = password
        
        print("✅ User login successful")
    
    def test_05_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {"email": random_email(), "password": "wrong_password"}
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Invalid email or password")
        print("✅ Invalid login credentials properly rejected")
    
    def test_06_get_current_user(self):
        """Test getting current user info"""
        # First ensure we have a valid token
        if not self.token:
            self.test_04_login_user()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        # Debug output
        print(f"Get user response status: {response.status_code}")
        print(f"Get user response: {response.text}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], self.email)
        print("✅ Get current user info successful")
    
    def test_07_get_current_user_invalid_token(self):
        """Test getting user info with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        self.assertEqual(response.status_code, 401)
        print("✅ Invalid token properly rejected")
    
    def test_08_create_link(self):
        """Test creating a link"""
        # First ensure we have a valid token
        if not self.token:
            self.test_04_login_user()
        
        link_data = {
            "url": "https://www.example.com",
            "title": "Example Website",
            "description": "This is an example website for testing",
            "image_url": "https://www.example.com/image.jpg"
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{BASE_URL}/links", json=link_data, headers=headers)
        
        # Debug output
        print(f"Create link response status: {response.status_code}")
        print(f"Create link response: {response.text}")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["url"], link_data["url"])
        self.assertEqual(data["title"], link_data["title"])
        self.assertEqual(data["description"], link_data["description"])
        self.assertEqual(data["image_url"], link_data["image_url"])
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        
        # Save link ID for later tests
        self.test_links.append(data["id"])
        print("✅ Link creation successful")
    
    def test_09_create_link_minimal_data(self):
        """Test creating a link with minimal data"""
        # First ensure we have a valid token
        if not self.token:
            self.test_04_login_user()
        
        link_data = {
            "url": "https://www.example.org"
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{BASE_URL}/links", json=link_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["url"], link_data["url"])
        
        # Note: With the new auto-extraction feature, metadata might be populated
        # So we don't assert that these fields are None anymore
        self.assertIn("id", data)
        
        # Save link ID for later tests
        self.test_links.append(data["id"])
        print("✅ Link creation with minimal data successful")
    
    def test_10_get_user_links(self):
        """Test getting user links"""
        # First ensure we have a valid token
        if not self.token:
            self.test_04_login_user()
        
        # Create links if none exist
        if not self.test_links:
            self.test_08_create_link()
            self.test_09_create_link_minimal_data()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{BASE_URL}/links", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
        # Debug output
        print(f"Get links response: {json.dumps(data[:2], indent=2)}")
        
        self.assertGreaterEqual(len(data), len(self.test_links))
        
        # Verify links are sorted by creation date (newest first)
        if len(data) >= 2:
            first_date = datetime.fromisoformat(data[0]["created_at"].replace("Z", "+00:00"))
            second_date = datetime.fromisoformat(data[1]["created_at"].replace("Z", "+00:00"))
            self.assertGreaterEqual(first_date, second_date)
        
        print(f"✅ Retrieved {len(data)} links successfully")
    
    def test_11_delete_link(self):
        """Test deleting a link"""
        # First ensure we have a valid token
        if not self.token:
            self.test_04_login_user()
        
        # Create a link if none exist
        if not self.test_links:
            self.test_08_create_link()
        
        link_id = self.test_links[0]
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(f"{BASE_URL}/links/{link_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Link deleted successfully")
        
        # Verify link is deleted
        response = requests.get(f"{BASE_URL}/links", headers=headers)
        data = response.json()
        link_ids = [link["id"] for link in data]
        self.assertNotIn(link_id, link_ids)
        
        # Remove from test_links
        self.test_links.remove(link_id)
        print("✅ Link deletion successful")
    
    def test_12_delete_nonexistent_link(self):
        """Test deleting a non-existent link"""
        # First ensure we have a valid token
        if not self.token:
            self.test_04_login_user()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.delete(f"{BASE_URL}/links/nonexistent_id", headers=headers)
        self.assertEqual(response.status_code, 404)
        print("✅ Non-existent link deletion properly rejected")
    
    def test_13_protected_routes_without_token(self):
        """Test accessing protected routes without token"""
        # Test GET /api/auth/me
        response = requests.get(f"{BASE_URL}/auth/me")
        self.assertEqual(response.status_code, 403)
        
        # Test GET /api/links
        response = requests.get(f"{BASE_URL}/links")
        self.assertEqual(response.status_code, 403)
        
        # Test POST /api/links
        link_data = {"url": "https://www.example.com"}
        response = requests.post(f"{BASE_URL}/links", json=link_data)
        self.assertEqual(response.status_code, 403)
        
        # Test DELETE /api/links/{link_id}
        response = requests.delete(f"{BASE_URL}/links/some_id")
        self.assertEqual(response.status_code, 403)
        
        print("✅ Protected routes properly reject requests without token")
    
    def test_14_extract_metadata_endpoint(self):
        """Test the metadata extraction endpoint with various URLs"""
        # First ensure we have a valid token
        if not self.token:
            self.test_04_login_user()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test with GitHub (should have good metadata)
        response = requests.post(
            f"{BASE_URL}/links/extract-metadata", 
            json={"url": TEST_URLS["github"]}, 
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        github_data = response.json()
        print(f"GitHub metadata: {json.dumps(github_data, indent=2)}")
        self.assertIsNotNone(github_data["title"])
        self.assertIsNotNone(github_data["description"])
        
        # Test with Stack Overflow (should have good metadata)
        response = requests.post(
            f"{BASE_URL}/links/extract-metadata", 
            json={"url": TEST_URLS["stackoverflow"]}, 
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        stackoverflow_data = response.json()
        print(f"Stack Overflow metadata: {json.dumps(stackoverflow_data, indent=2)}")
        self.assertIsNotNone(stackoverflow_data["title"])
        
        # Test with example.com (minimal metadata)
        response = requests.post(
            f"{BASE_URL}/links/extract-metadata", 
            json={"url": TEST_URLS["example"]}, 
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        example_data = response.json()
        print(f"Example.com metadata: {json.dumps(example_data, indent=2)}")
        self.assertIsNotNone(example_data["title"])
        
        # Test with httpbin (test HTML page)
        response = requests.post(
            f"{BASE_URL}/links/extract-metadata", 
            json={"url": TEST_URLS["httpbin"]}, 
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        httpbin_data = response.json()
        print(f"Httpbin metadata: {json.dumps(httpbin_data, indent=2)}")
        
        # Test with non-existent URL (should handle gracefully)
        response = requests.post(
            f"{BASE_URL}/links/extract-metadata", 
            json={"url": TEST_URLS["nonexistent"]}, 
            headers=headers
        )
        self.assertEqual(response.status_code, 200)
        nonexistent_data = response.json()
        print(f"Non-existent URL metadata: {json.dumps(nonexistent_data, indent=2)}")
        
        print("✅ Metadata extraction endpoint tested with various URLs")
    
    def test_15_create_link_with_auto_extraction(self):
        """Test creating a link with automatic metadata extraction"""
        # First ensure we have a valid token
        if not self.token:
            self.test_04_login_user()
        
        # Create a link with only URL (should trigger auto-extraction)
        link_data = {
            "url": TEST_URLS["github"]
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{BASE_URL}/links", json=link_data, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(f"Auto-extracted link data: {json.dumps(data, indent=2)}")
        
        self.assertEqual(data["url"], link_data["url"])
        self.assertIsNotNone(data["title"])
        self.assertIsNotNone(data["description"])
        self.assertIn("id", data)
        
        # Save link ID for later tests
        self.test_links.append(data["id"])
        print("✅ Link creation with auto-extraction successful")
    
    def test_16_create_link_with_partial_metadata(self):
        """Test creating a link with partial metadata"""
        # First ensure we have a valid token
        if not self.token:
            self.test_04_login_user()
        
        # Create a link with partial metadata
        link_data = {
            "url": TEST_URLS["stackoverflow"],
            "title": "Custom Stack Overflow Title"
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{BASE_URL}/links", json=link_data, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        print(f"Partial metadata link data: {json.dumps(data, indent=2)}")
        
        self.assertEqual(data["url"], link_data["url"])
        self.assertEqual(data["title"], link_data["title"])  # Should use provided title
        self.assertIn("id", data)
        
        # Save link ID for later tests
        self.test_links.append(data["id"])
        print("✅ Link creation with partial metadata successful")

def run_tests():
    """Run all tests in order"""
    test_suite = unittest.TestSuite()
    test_loader = unittest.TestLoader()
    test_loader.sortTestMethodsUsing = None  # Use the order defined in the class
    test_suite.addTests(test_loader.loadTestsFromTestCase(LinkShareAPITest))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    
    return len(result.errors) + len(result.failures) == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
