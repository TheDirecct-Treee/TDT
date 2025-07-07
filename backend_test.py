import requests
import unittest
import json
import time
import os
from datetime import datetime, timedelta

# Use the public endpoint for testing
BACKEND_URL = "https://01f16dc2-4be8-4f34-b29a-a8f7b50340e0.preview.emergentagent.com/api"

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
        
        # Verify new categories are present
        self.assertIn("Gym", data["categories"])
        self.assertIn("Personal Trainers", data["categories"])
        
        print(f"✅ Categories endpoint test passed - Found {len(data['categories'])} categories including 'Gym' and 'Personal Trainers'")

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
        
    def test_19_get_event_categories(self):
        """Test retrieving event categories including 'Happy Hour'"""
        print("\n🔍 Testing event categories endpoint...")
        response = requests.get(f"{BACKEND_URL}/event-categories")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("categories", data)
        self.assertIsInstance(data["categories"], list)
        self.assertGreater(len(data["categories"]), 0)
        self.assertIn("Happy Hour", data["categories"])
        print(f"✅ Event categories endpoint test passed - Found {len(data['categories'])} categories including 'Happy Hour'")
        
    def test_20_business_search(self):
        """Test business search functionality"""
        print("\n🔍 Testing business search endpoint...")
        
        # Test basic search
        response = requests.get(f"{BACKEND_URL}/businesses/search?q=test")
        self.assertEqual(response.status_code, 200)
        businesses = response.json()
        self.assertIsInstance(businesses, list)
        print(f"✅ Business search test passed - Found {len(businesses)} businesses matching 'test'")
        
        # Test search with island filter
        if len(businesses) > 0:
            island = businesses[0]["island"]
            response = requests.get(f"{BACKEND_URL}/businesses/search?q=test&island={island}")
            self.assertEqual(response.status_code, 200)
            filtered_businesses = response.json()
            self.assertIsInstance(filtered_businesses, list)
            for business in filtered_businesses:
                self.assertEqual(business["island"], island)
            print(f"✅ Business search with island filter test passed")
            
        # Test search with category filter
        response = requests.get(f"{BACKEND_URL}/businesses/search?q=test&category=Restaurant")
        self.assertEqual(response.status_code, 200)
        filtered_businesses = response.json()
        self.assertIsInstance(filtered_businesses, list)
        for business in filtered_businesses:
            self.assertEqual(business["category"], "Restaurant")
        print(f"✅ Business search with category filter test passed")
        
    def test_21_business_profile_photo_upload(self):
        """Test business profile photo upload"""
        if not self.business_owner_token:
            self.test_06_business_owner_login()
            
        # Skip if we don't have a business ID
        if not self.test_business_id:
            print("\n⚠️ Skipping profile photo upload test - No business ID available")
            return
            
        print("\n🔍 Testing business profile photo upload...")
        
        # Create a test image file
        test_image_path = "/tmp/test_profile_photo.jpg"
        with open(test_image_path, "wb") as f:
            f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13\"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfe\xfe(\xa2\x8a\x00\xff\xd9")
        
        headers = {"Authorization": f"Bearer {self.business_owner_token}"}
        
        # Test profile photo upload
        with open(test_image_path, "rb") as f:
            files = {"file": ("test_profile.jpg", f, "image/jpeg")}
            response = requests.post(
                f"{BACKEND_URL}/business/{self.test_business_id}/upload-profile-photo",
                headers=headers,
                files=files
            )
            
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("photo_url", data)
        print("✅ Business profile photo upload test passed")
        
        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            
    def test_22_business_cover_photo_upload(self):
        """Test business cover photo upload"""
        if not self.business_owner_token:
            self.test_06_business_owner_login()
            
        # Skip if we don't have a business ID
        if not self.test_business_id:
            print("\n⚠️ Skipping cover photo upload test - No business ID available")
            return
            
        print("\n🔍 Testing business cover photo upload...")
        
        # Create a test image file
        test_image_path = "/tmp/test_cover_photo.jpg"
        with open(test_image_path, "wb") as f:
            f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13\"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfe\xfe(\xa2\x8a\x00\xff\xd9")
        
        headers = {"Authorization": f"Bearer {self.business_owner_token}"}
        
        # Test cover photo upload
        with open(test_image_path, "rb") as f:
            files = {"file": ("test_cover.jpg", f, "image/jpeg")}
            response = requests.post(
                f"{BACKEND_URL}/business/{self.test_business_id}/upload-cover-photo",
                headers=headers,
                files=files
            )
            
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("photo_url", data)
        print("✅ Business cover photo upload test passed")
        
        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            
    def test_23_business_logo_upload(self):
        """Test business logo upload"""
        if not self.business_owner_token:
            self.test_06_business_owner_login()
            
        # Skip if we don't have a business ID
        if not self.test_business_id:
            print("\n⚠️ Skipping logo upload test - No business ID available")
            return
            
        print("\n🔍 Testing business logo upload...")
        
        # Create a test image file
        test_image_path = "/tmp/test_logo.jpg"
        with open(test_image_path, "wb") as f:
            f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13\"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfe\xfe(\xa2\x8a\x00\xff\xd9")
        
        headers = {"Authorization": f"Bearer {self.business_owner_token}"}
        
        # Test logo upload
        with open(test_image_path, "rb") as f:
            files = {"file": ("test_logo.jpg", f, "image/jpeg")}
            response = requests.post(
                f"{BACKEND_URL}/business/{self.test_business_id}/upload-logo",
                headers=headers,
                files=files
            )
            
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("photo_url", data)
        print("✅ Business logo upload test passed")
        
        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            
    def test_24_business_model_fields(self):
        """Test BusinessProfile model has new fields"""
        if not self.test_business_id:
            # Get the first business from the list
            response = requests.get(f"{BACKEND_URL}/businesses")
            businesses = response.json()
            if len(businesses) > 0:
                self.test_business_id = businesses[0]["id"]
            else:
                print("\n⚠️ Skipping business model fields test - No businesses available")
                return
                
        print("\n🔍 Testing BusinessProfile model fields...")
        response = requests.get(f"{BACKEND_URL}/business/{self.test_business_id}")
        self.assertEqual(response.status_code, 200)
        business = response.json()
        
        # Check for new fields
        self.assertIn("profile_photo", business)
        self.assertIn("cover_photo", business)
        self.assertIn("logo", business)
        
        print("✅ BusinessProfile model fields test passed")
        
    def test_25_create_apartment_listing(self):
        """Test apartment listing creation"""
        print("\n🔍 Testing apartment listing creation...")
        
        # Generate unique test data
        timestamp = int(time.time())
        test_apartment_title = f"Test Apartment {timestamp}"
        
        apartment_data = {
            "title": test_apartment_title,
            "description": "Spacious 2-bedroom apartment with ocean view",
            "address": "123 Ocean Drive",
            "island": "New Providence",
            "bedrooms": 2,
            "bathrooms": 1,
            "monthly_rent": 1200.00,
            "property_type": "Apartment",
            "furnishing": "Furnished",
            "amenities": ["Pool", "Gym", "A/C", "Parking"],
            "utilities_included": ["Water", "Internet"],
            "lease_duration": "1 Year",
            "available_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "contact_name": "John Smith",
            "contact_email": "john.smith@example.com",
            "contact_phone": "1234567890"
        }
        
        response = requests.post(f"{BACKEND_URL}/apartment/create", json=apartment_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], test_apartment_title)
        self.test_apartment_id = data["id"]
        print("✅ Apartment listing creation test passed")
        
    def test_26_get_apartment_listing(self):
        """Test retrieving a specific apartment listing"""
        # Skip if we don't have an apartment ID
        if not hasattr(self, 'test_apartment_id'):
            print("\n⚠️ Skipping apartment retrieval test - No apartment ID available")
            return
            
        print(f"\n🔍 Testing apartment retrieval by ID: {self.test_apartment_id}...")
        response = requests.get(f"{BACKEND_URL}/apartment/{self.test_apartment_id}")
        self.assertEqual(response.status_code, 200)
        apartment = response.json()
        self.assertEqual(apartment["id"], self.test_apartment_id)
        print("✅ Apartment retrieval test passed")
        
    def test_27_get_apartments_with_filtering(self):
        """Test retrieving apartments with filtering"""
        print("\n🔍 Testing apartments endpoint with filtering...")
        
        # Test basic retrieval
        response = requests.get(f"{BACKEND_URL}/apartments")
        self.assertEqual(response.status_code, 200)
        apartments = response.json()
        self.assertIsInstance(apartments, list)
        print(f"✅ Apartments endpoint test passed - Found {len(apartments)} apartments")
        
        # Skip further tests if no apartments available
        if len(apartments) == 0:
            print("⚠️ No apartments available for filter testing")
            return
            
        # Test filtering by island
        island = apartments[0]["island"]
        response = requests.get(f"{BACKEND_URL}/apartments?island={island}")
        self.assertEqual(response.status_code, 200)
        filtered_apartments = response.json()
        self.assertIsInstance(filtered_apartments, list)
        if len(filtered_apartments) > 0:
            for apartment in filtered_apartments:
                self.assertEqual(apartment["island"], island)
            print(f"✅ Apartment filtering by island test passed")
        
        # Test filtering by property_type
        property_type = apartments[0]["property_type"]
        response = requests.get(f"{BACKEND_URL}/apartments?property_type={property_type}")
        self.assertEqual(response.status_code, 200)
        filtered_apartments = response.json()
        self.assertIsInstance(filtered_apartments, list)
        if len(filtered_apartments) > 0:
            for apartment in filtered_apartments:
                self.assertEqual(apartment["property_type"], property_type)
            print(f"✅ Apartment filtering by property_type test passed")
        
        # Test filtering by rent range
        min_rent = 500
        max_rent = 2000
        response = requests.get(f"{BACKEND_URL}/apartments?min_rent={min_rent}&max_rent={max_rent}")
        self.assertEqual(response.status_code, 200)
        filtered_apartments = response.json()
        self.assertIsInstance(filtered_apartments, list)
        if len(filtered_apartments) > 0:
            for apartment in filtered_apartments:
                self.assertGreaterEqual(apartment["monthly_rent"], min_rent)
                self.assertLessEqual(apartment["monthly_rent"], max_rent)
            print(f"✅ Apartment filtering by rent range test passed")
        
        # Test filtering by bedrooms
        bedrooms = apartments[0]["bedrooms"]
        response = requests.get(f"{BACKEND_URL}/apartments?bedrooms={bedrooms}")
        self.assertEqual(response.status_code, 200)
        filtered_apartments = response.json()
        self.assertIsInstance(filtered_apartments, list)
        if len(filtered_apartments) > 0:
            for apartment in filtered_apartments:
                self.assertEqual(apartment["bedrooms"], bedrooms)
            print(f"✅ Apartment filtering by bedrooms test passed")
        
    def test_28_apartment_photo_upload(self):
        """Test apartment photo upload"""
        # Skip if we don't have an apartment ID
        if not hasattr(self, 'test_apartment_id'):
            print("\n⚠️ Skipping apartment photo upload test - No apartment ID available")
            return
            
        print("\n🔍 Testing apartment photo upload...")
        
        # Create a test image file
        test_image_path = "/tmp/test_apartment_photo.jpg"
        with open(test_image_path, "wb") as f:
            f.write(b"\xff\xd8\xff\xe0\x10JFIF\x01\x01\x01HH\xff\xdbC\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xdbC\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x11\x08\x01\x01\x03\x01\"\x02\x11\x01\x03\x11\x01\xff\xc4\x1f\x01\x05\x01\x01\x01\x01\x01\x01\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\xb5\x10\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x01}\x01\x02\x03\x04\x11\x05\x12!1A\x06\x13Qa\x07\"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x1f\x01\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\xb5\x11\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x01\x02w\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13\"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x0c\x03\x01\x02\x11\x03\x11?\xfe\xfe(\xa2\x8a\xff\xd9")
        
        # Test photo upload
        with open(test_image_path, "rb") as f:
            files = {"file": ("test_apartment.jpg", f, "image/jpeg")}
            data = {"contact_email": "john.smith@example.com"}
            response = requests.post(
                f"{BACKEND_URL}/apartment/{self.test_apartment_id}/upload-photo",
                files=files,
                data=data
            )
            
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        print("✅ Apartment photo upload test passed")
        
        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            
    def test_29_apartment_payment_creation(self):
        """Test apartment payment creation"""
        # Skip if we don't have an apartment ID
        if not hasattr(self, 'test_apartment_id'):
            print("\n⚠️ Skipping apartment payment creation test - No apartment ID available")
            return
            
        print("\n🔍 Testing apartment payment creation...")
        response = requests.post(f"{BACKEND_URL}/apartment/{self.test_apartment_id}/create-payment")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("payment_id", data)
        self.assertIn("approval_url", data)
        print("✅ Apartment payment creation test passed")
        
    def test_30_user_registration_with_agreements(self):
        """Test user registration with agreements"""
        print("\n🔍 Testing user registration with agreements...")
        
        # Generate unique test data
        timestamp = int(time.time())
        test_user_email = f"test_user_agreements_{timestamp}@example.com"
        
        user_data = {
            "email": test_user_email,
            "password": "TestPass123!",
            "first_name": "Test",
            "last_name": "User",
            "role": "customer",
            "phone": "1234567890"
        }
        
        response = requests.post(f"{BACKEND_URL}/register", json=user_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["email"], test_user_email)
        print("✅ User registration with agreements test passed")

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
        DirectTreeAPITest('test_18_paypal_create_plan'),
        DirectTreeAPITest('test_19_get_event_categories'),
        DirectTreeAPITest('test_20_business_search'),
        DirectTreeAPITest('test_21_business_profile_photo_upload'),
        DirectTreeAPITest('test_22_business_cover_photo_upload'),
        DirectTreeAPITest('test_23_business_logo_upload'),
        DirectTreeAPITest('test_24_business_model_fields')
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