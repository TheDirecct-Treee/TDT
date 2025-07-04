#!/usr/bin/env python3
import requests
import json
import time

API_BASE = "https://12f9c8c1-4cbd-43be-9ad4-a09db48b290e.preview.emergentagent.com/api"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMGMxNjVjMDgtYTgyMi00MDVkLTg4NzQtYzQyZWJmYTk5MjkyIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzUzOTAxNjU4fQ.vGKSvqBh1ulNDC_kA3Nk2tvzB5fd3zhhpu_prP1Np_I"

sample_businesses = [
    {
        "email": "diving@example.com",
        "business": {
            "business_name": "Island Diving Adventures",
            "description": "Professional scuba diving and snorkeling tours to the most beautiful coral reefs",
            "category": "Tour Operator",
            "island": "Exuma",
            "address": "789 Marina Way, Georgetown",
            "phone": "242-555-9876",
            "email": "info@islanddiving.bs",
            "license_number": "BS-TOUR-2024-003",
            "accepts_appointments": True
        }
    },
    {
        "email": "salon@example.com",
        "business": {
            "business_name": "Tropical Glow Spa & Salon",
            "description": "Full-service spa and salon offering relaxation and beauty treatments in paradise",
            "category": "Beauty & Spa",
            "island": "Eleuthera",
            "address": "321 Wellness Road, Governor's Harbour",
            "phone": "242-555-2468",
            "email": "hello@tropicalglow.bs",
            "license_number": "BS-SPA-2024-004",
            "accepts_appointments": True
        }
    },
    {
        "email": "mechanic@example.com",
        "business": {
            "business_name": "Island Auto Care",
            "description": "Reliable automotive repair and maintenance services for all vehicle types",
            "category": "Automotive",
            "island": "Abaco",
            "address": "654 Repair Street, Marsh Harbour",
            "phone": "242-555-1357",
            "email": "service@islandauto.bs",
            "license_number": "BS-AUTO-2024-005",
            "accepts_appointments": True
        }
    },
    {
        "email": "market@example.com",
        "business": {
            "business_name": "Island Fresh Market",
            "description": "Local grocery store featuring fresh produce, Bahamian specialties, and daily essentials",
            "category": "Retail",
            "island": "Cat Island",
            "address": "147 Market Square, Arthur's Town",
            "phone": "242-555-8642",
            "email": "info@islandfresh.bs",
            "license_number": "BS-RETAIL-2024-006",
            "accepts_appointments": False
        }
    },
    {
        "email": "transport@example.com",
        "business": {
            "business_name": "Bahamas Express Transport",
            "description": "Reliable inter-island transportation and taxi services throughout the Bahamas",
            "category": "Transportation",
            "island": "Andros",
            "address": "258 Transport Hub, Andros Town",
            "phone": "242-555-7531",
            "email": "rides@bahamasexpress.bs",
            "license_number": "BS-TRANSPORT-2024-007",
            "accepts_appointments": True
        }
    }
]

def create_user_and_business(email, business_data):
    # Create user
    user_data = {
        "email": email,
        "password": "testpass123",
        "first_name": business_data["business_name"].split()[0],
        "last_name": "Owner",
        "role": "business_owner"
    }
    
    try:
        response = requests.post(f"{API_BASE}/register", json=user_data)
        if response.status_code == 200:
            user_info = response.json()
            token = user_info["token"]
            
            # Create business
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(f"{API_BASE}/business/create", json=business_data, headers=headers)
            
            if response.status_code == 200:
                business_info = response.json()
                business_id = business_info["id"]
                
                # Approve business
                admin_headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
                response = requests.put(f"{API_BASE}/admin/business/{business_id}/approve", headers=admin_headers)
                
                if response.status_code == 200:
                    print(f"✅ Created and approved: {business_data['business_name']} on {business_data['island']}")
                    return True
                else:
                    print(f"❌ Failed to approve: {business_data['business_name']}")
            else:
                print(f"❌ Failed to create business: {business_data['business_name']}")
        else:
            print(f"❌ Failed to create user: {email}")
    except Exception as e:
        print(f"❌ Error creating {business_data['business_name']}: {str(e)}")
    
    return False

if __name__ == "__main__":
    print("🏝️ Creating sample businesses for The Direct Tree...")
    success_count = 0
    
    for item in sample_businesses:
        if create_user_and_business(item["email"], item["business"]):
            success_count += 1
        time.sleep(1)  # Rate limiting
    
    print(f"\n🎉 Successfully created {success_count}/{len(sample_businesses)} businesses!")
    print("Your platform now has businesses across multiple islands! 🌴")