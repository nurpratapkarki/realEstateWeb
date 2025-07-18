#!/usr/bin/env python3

import requests
import json

# Test property creation API
def test_property_creation():
    base_url = "http://localhost:8000/api"
    
    # First, login to get token
    login_data = {
        "username": "admin",
        "password": "admin123"  # Assuming this is the password
    }
    
    print("1. Attempting to login...")
    login_response = requests.post(f"{base_url}/auth/login/", json=login_data)
    print(f"Login response status: {login_response.status_code}")
    print(f"Login response: {login_response.text}")
    
    if login_response.status_code != 200:
        print("Login failed, trying different password...")
        login_data["password"] = "admin"
        login_response = requests.post(f"{base_url}/auth/login/", json=login_data)
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")
    
    if login_response.status_code == 200:
        token = login_response.json().get('token')
        print(f"Login successful, token: {token}")
        
        # Test property creation
        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }
        
        # Test with minimal data (like frontend sends after fix - with proper null handling)
        property_data_minimal_fixed = {
            "title": "",
            "description": "",
            "property_type": None,
            "price": None,
            "bedrooms": None,
            "bathrooms": 0,
            "area": None,
            "area_unit": "aana",
            "property_purpose": "land",
            "land_ropani": None,
            "land_aana": None,
            "land_paisa": None,
            "land_daam": None,
            "google_maps_embed_url": None,
            "location": "",
            "address": "",
            "latitude": None,
            "longitude": None,
            "is_featured": False,
            "is_active": True
        }

        # Test with proper data (like frontend sends with filled form)
        property_data_filled = {
            "title": "Test Property",
            "description": "A test property for debugging",
            "property_type": 1,
            "price": 5000000.0,
            "bedrooms": None,  # For land property
            "bathrooms": 2,
            "area": 100.0,
            "area_unit": "aana",
            "property_purpose": "land",
            "land_ropani": None,
            "land_aana": None,
            "land_paisa": None,
            "land_daam": None,
            "google_maps_embed_url": None,
            "location": "Test Location",
            "address": "Test Address",
            "latitude": None,
            "longitude": None,
            "is_featured": False,
            "is_active": True
        }
        
        print("\n2. Testing with minimal/empty data (simulating frontend after fix)...")
        print(f"Minimal data (fixed): {json.dumps(property_data_minimal_fixed, indent=2)}")

        create_response_minimal = requests.post(f"{base_url}/admin/properties/",
                                              json=property_data_minimal_fixed,
                                              headers=headers)
        print(f"Minimal data response status: {create_response_minimal.status_code}")
        print(f"Minimal data response: {create_response_minimal.text}")

        print("\n3. Testing with filled data...")
        print(f"Filled data: {json.dumps(property_data_filled, indent=2)}")

        create_response_filled = requests.post(f"{base_url}/admin/properties/",
                                             json=property_data_filled,
                                             headers=headers)
        print(f"Filled data response status: {create_response_filled.status_code}")
        print(f"Filled data response: {create_response_filled.text}")
        
    else:
        print("Could not login to test property creation")

if __name__ == "__main__":
    test_property_creation()
