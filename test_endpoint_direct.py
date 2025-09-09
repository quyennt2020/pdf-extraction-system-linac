#!/usr/bin/env python3
"""
Test Image Upload Endpoint Directly
"""

import requests
import json

API_BASE = "http://localhost:3000/api/expert-review"

def test_endpoints():
    """Test if endpoints exist"""
    
    print("🔍 Testing API Endpoints")
    print("=" * 40)
    
    # Test basic entities endpoint
    print("1. Testing entities endpoint...")
    try:
        response = requests.get(f"{API_BASE}/entities")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            entities = data.get('entities', [])
            print(f"   Entities found: {len(entities)}")
            if entities:
                entity_id = entities[0]['id']
                print(f"   Test entity ID: {entity_id}")
                return entity_id
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    return None

def test_image_endpoint(entity_id):
    """Test image endpoint"""
    print(f"\n2. Testing image endpoint for entity {entity_id}...")
    
    # Test GET image info
    try:
        response = requests.get(f"{API_BASE}/entities/{entity_id}/image")
        print(f"   GET /image status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test POST upload (without file to see if endpoint exists)
    try:
        response = requests.post(f"{API_BASE}/entities/{entity_id}/upload-image")
        print(f"   POST /upload-image status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

def main():
    entity_id = test_endpoints()
    if entity_id:
        test_image_endpoint(entity_id)
    else:
        print("❌ No entities found to test with")

if __name__ == "__main__":
    main()