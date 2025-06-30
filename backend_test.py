import requests
import unittest
import json
import time
from datetime import datetime, timedelta

# Use the public endpoint for testing
BACKEND_URL = "https://0570b8a0-8ac2-47c9-b54e-20b5abc9f354.preview.emergentagent.com/api"

class DirectTreeAPITest(unittest.TestCase):
    def setUp(self):
        self.admin_credentials = {
            "email": "admin@thedirecttree.com",
            "password": "admin123"
        }
        self.customer_credentials = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        self.business_owner_credentials = {
            "email": "business@example.com",
            "password": "testpass123"
        }
        
        # Generate unique test data
        timestamp = int(time.time())
        self.test_user_email = f"test_user_{timestamp}@example.com"
        self.test_business_name = f"Test Business {timestamp}"
        
        # Store tokens and IDs for use across tests
        self.admin_token = None
        self.customer_token = None
        self.business_owner_token = None
        self.test_business_id = None
        self.test_review_id = None

    def test_01_root_endpoint(self):
        """Test the root API endpoint"""
        print("\n🔍 Testing root API endpoint...")
        response = requests.get(f"{BACKEND_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        print("✅ Root API endpoint test passed")

    def test_02_get_islands(self):
        """Test retrieving islands list"""
        print("\n🔍 Testing islands endpoint...")
        response = requests.get(f"{BACKEND_URL}/islands")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("islands", data)
        self.assertIsInstance(data["islands"], list)
        self.assertGreater(len(data["islands"]), 0)
        print(f"✅ Islands endpoint test passed - Found {len(data['islands'])} islands")

    def test_03_get_categories(self):
        """Test retrieving business categories"""
        print("\n🔍 Testing categories endpoint...")
        response = requests.get(f"{BACKEND_URL}/categories")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("categories", data)
        self.assertIsInstance(data["categories"], list)
        self.assertGreater(len(data["categories"]), 0)
        print(f"✅ Categories endpoint test passed - Found {len(data['categories'])} categories")

    def test_04_admin_login(self):
        """Test admin login"""
        print("\n🔍 Testing admin login...")
        response = requests.post(f"{BACKEND_URL}/login", json=self.admin_credentials)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["role"], "admin")
        self.admin_token = data["token"]
        print("✅ Admin login test passed")

    def test_05_customer_login(self):
        """Test customer login"""
        print("\n🔍 Testing customer login...")
        response = requests.post(f"{BACKEND_URL}/login", json=self.customer_credentials)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["role"], "customer")
        self.customer_token = data["token"]
        print("✅ Customer login test passed")

    def test_06_business_owner_login(self):
        """Test business owner login"""
        print("\n🔍 Testing business owner login...")
        response = requests.post(f"{BACKEND_URL}/login", json=self.business_owner_credentials)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["role"], "business_owner")
        self.business_owner_token = data["token"]
        print("✅ Business owner login test passed")

    def test_07_register_new_user(self):
        """Test user registration"""
        print("\n🔍 Testing user registration...")
        user_data = {
            "email": self.test_user_email,
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
            "role": "customer",
            "phone": "1234567890"
        }
        response = requests.post(f"{BACKEND_URL}/register", json=user_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], self.test_user_email)
        print("✅ User registration test passed")

    def test_08_get_businesses(self):
        """Test retrieving businesses"""
        print("\n🔍 Testing businesses endpoint...")
        response = requests.get(f"{BACKEND_URL}/businesses")
        self.assertEqual(response.status_code, 200)
        businesses = response.json()
        self.assertIsInstance(businesses, list)
        print(f"✅ Businesses endpoint test passed - Found {len(businesses)} businesses")
        
        # Test filtering by island
        if len(businesses) > 0:
            island = businesses[0]["island"]
            response = requests.get(f"{BACKEND_URL}/businesses?island={island}")
            self.assertEqual(response.status_code, 200)
            filtered_businesses = response.json()
            self.assertIsInstance(filtered_businesses, list)
            for business in filtered_businesses:
                self.assertEqual(business["island"], island)
            print(f"✅ Business filtering by island test passed - Found {len(filtered_businesses)} businesses in {island}")
            
            # Test filtering by category
            category = businesses[0]["category"]
            response = requests.get(f"{BACKEND_URL}/businesses?category={category}")
            self.assertEqual(response.status_code, 200)
            filtered_businesses = response.json()
            self.assertIsInstance(filtered_businesses, list)
            for business in filtered_businesses:
                self.assertEqual(business["category"], category)
            print(f"✅ Business filtering by category test passed - Found {len(filtered_businesses)} businesses in {category} category")

    def test_09_create_business(self):
        """Test business creation"""
        if not self.business_owner_token:
            self.test_06_business_owner_login()
            
        print("\n🔍 Testing business creation...")
        business_data = {
            "business_name": self.test_business_name,
            "description": "This is a test business for API testing",
            "category": "Restaurant",
            "island": "New Providence",
            "address": "123 Test Street",
            "phone": "1234567890",
            "email": "test@business.com",
            "website": "https://testbusiness.com",
            "business_hours": {"Monday": "9AM-5PM", "Tuesday": "9AM-5PM"},
            "services": ["Service 1", "Service 2"],
            "license_number": "TEST12345",
            "accepts_appointments": True,
            "appointment_duration": 60
        }
        
        headers = {"Authorization": f"Bearer {self.business_owner_token}"}
        response = requests.post(f"{BACKEND_URL}/business/create", json=business_data, headers=headers)
        
        # If business already exists, this might fail
        if response.status_code == 400 and "already have a business registered" in response.json().get("detail", ""):
            print("⚠️ Business owner already has a business registered")
            # Get the existing business
            response = requests.get(f"{BACKEND_URL}/businesses", headers=headers)
            businesses = response.json()
            for business in businesses:
                if business.get("user_id") == self.business_owner_credentials.get("id"):
                    self.test_business_id = business.get("id")
                    break
        else:
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["business_name"], self.test_business_name)
            self.test_business_id = data["id"]
            print("✅ Business creation test passed")

    def test_10_get_business_by_id(self):
        """Test retrieving a business by ID"""
        # Skip if we don't have a business ID
        if not self.test_business_id:
            print("\n⚠️ Skipping business retrieval test - No business ID available")
            return
            
        print(f"\n🔍 Testing business retrieval by ID: {self.test_business_id}...")
        response = requests.get(f"{BACKEND_URL}/business/{self.test_business_id}")
        self.assertEqual(response.status_code, 200)
        business = response.json()
        self.assertEqual(business["id"], self.test_business_id)
        print("✅ Business retrieval test passed")

    def test_11_create_review(self):
        """Test creating a review"""
        if not self.customer_token:
            self.test_05_customer_login()
            
        # Skip if we don't have a business ID
        if not self.test_business_id:
            # Get the first business from the list
            response = requests.get(f"{BACKEND_URL}/businesses")
            businesses = response.json()
            if len(businesses) > 0:
                self.test_business_id = businesses[0]["id"]
            else:
                print("\n⚠️ Skipping review creation test - No businesses available")
                return
            
        print("\n🔍 Testing review creation...")
        review_data = {
            "business_id": self.test_business_id,
            "rating": 5,
            "comment": "This is a test review from the API test",
            "is_anonymous": False
        }
        
        headers = {"Authorization": f"Bearer {self.customer_token}"}
        response = requests.post(f"{BACKEND_URL}/review/create", json=review_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["business_id"], self.test_business_id)
        self.assertEqual(data["rating"], 5)
        self.test_review_id = data["id"]
        print("✅ Review creation test passed")

    def test_12_get_business_reviews(self):
        """Test retrieving business reviews"""
        # Skip if we don't have a business ID
        if not self.test_business_id:
            print("\n⚠️ Skipping business reviews test - No business ID available")
            return
            
        print(f"\n🔍 Testing business reviews retrieval for business ID: {self.test_business_id}...")
        response = requests.get(f"{BACKEND_URL}/business/{self.test_business_id}/reviews")
        self.assertEqual(response.status_code, 200)
        reviews = response.json()
        self.assertIsInstance(reviews, list)
        print(f"✅ Business reviews test passed - Found {len(reviews)} reviews")

    def test_13_admin_pending_businesses(self):
        """Test admin access to pending businesses"""
        if not self.admin_token:
            self.test_04_admin_login()
            
        print("\n🔍 Testing admin pending businesses endpoint...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(f"{BACKEND_URL}/admin/businesses/pending", headers=headers)
        self.assertEqual(response.status_code, 200)
        businesses = response.json()
        self.assertIsInstance(businesses, list)
        print(f"✅ Admin pending businesses test passed - Found {len(businesses)} pending businesses")

    def test_14_admin_pending_reviews(self):
        """Test admin access to pending reviews"""
        if not self.admin_token:
            self.test_04_admin_login()
            
        print("\n🔍 Testing admin pending reviews endpoint...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.get(f"{BACKEND_URL}/admin/reviews/pending", headers=headers)
        self.assertEqual(response.status_code, 200)
        reviews = response.json()
        self.assertIsInstance(reviews, list)
        print(f"✅ Admin pending reviews test passed - Found {len(reviews)} pending reviews")

    def test_15_approve_business(self):
        """Test approving a business as admin"""
        if not self.admin_token:
            self.test_04_admin_login()
            
        # Skip if we don't have a business ID
        if not self.test_business_id:
            print("\n⚠️ Skipping business approval test - No business ID available")
            return
            
        print(f"\n🔍 Testing business approval for business ID: {self.test_business_id}...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.put(f"{BACKEND_URL}/admin/business/{self.test_business_id}/approve", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        print("✅ Business approval test passed")

    def test_16_approve_review(self):
        """Test approving a review as admin"""
        if not self.admin_token:
            self.test_04_admin_login()
            
        # Skip if we don't have a review ID
        if not self.test_review_id:
            print("\n⚠️ Skipping review approval test - No review ID available")
            return
            
        print(f"\n🔍 Testing review approval for review ID: {self.test_review_id}...")
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        response = requests.put(f"{BACKEND_URL}/admin/review/{self.test_review_id}/approve", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        print("✅ Review approval test passed")

    def test_17_create_appointment(self):
        """Test creating an appointment"""
        if not self.customer_token:
            self.test_05_customer_login()
            
        # Skip if we don't have a business ID
        if not self.test_business_id:
            print("\n⚠️ Skipping appointment creation test - No business ID available")
            return
            
        print("\n🔍 Testing appointment creation...")
        appointment_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
        appointment_data = {
            "business_id": self.test_business_id,
            "appointment_date": appointment_date,
            "service": "Test Service",
            "notes": "This is a test appointment"
        }
        
        headers = {"Authorization": f"Bearer {self.customer_token}"}
        response = requests.post(f"{BACKEND_URL}/appointment/create", json=appointment_data, headers=headers)
        
        # This might fail if the business doesn't accept appointments
        if response.status_code == 400 and "does not accept appointments" in response.json().get("detail", ""):
            print("⚠️ Business does not accept appointments")
        else:
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["business_id"], self.test_business_id)
            print("✅ Appointment creation test passed")

    def test_18_paypal_create_plan(self):
        """Test creating a PayPal billing plan"""
        print("\n🔍 Testing PayPal billing plan creation...")
        response = requests.post(f"{BACKEND_URL}/paypal/create-plan")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("plan_id", data)
        self.assertIn("status", data)
        print("✅ PayPal billing plan creation test passed")

def run_tests():
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add tests in order
    test_cases = [
        DirectTreeAPITest('test_01_root_endpoint'),
        DirectTreeAPITest('test_02_get_islands'),
        DirectTreeAPITest('test_03_get_categories'),
        DirectTreeAPITest('test_04_admin_login'),
        DirectTreeAPITest('test_05_customer_login'),
        DirectTreeAPITest('test_06_business_owner_login'),
        DirectTreeAPITest('test_07_register_new_user'),
        DirectTreeAPITest('test_08_get_businesses'),
        DirectTreeAPITest('test_09_create_business'),
        DirectTreeAPITest('test_10_get_business_by_id'),
        DirectTreeAPITest('test_11_create_review'),
        DirectTreeAPITest('test_12_get_business_reviews'),
        DirectTreeAPITest('test_13_admin_pending_businesses'),
        DirectTreeAPITest('test_14_admin_pending_reviews'),
        DirectTreeAPITest('test_15_approve_business'),
        DirectTreeAPITest('test_16_approve_review'),
        DirectTreeAPITest('test_17_create_appointment'),
        DirectTreeAPITest('test_18_paypal_create_plan')
    ]
    
    for test_case in test_cases:
        suite.addTest(test_case)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    print("🚀 Starting The Direct Tree API Tests")
    print(f"🔗 Testing against: {BACKEND_URL}")
    print("=" * 80)
    run_tests()
    print("=" * 80)
    print("✅ API Tests Completed")