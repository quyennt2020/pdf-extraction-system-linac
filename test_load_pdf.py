#!/usr/bin/env python3
"""
Test Load PDF Results Functionality
"""

import requests
import json

API_BASE = "http://localhost:9000/api/expert-review"

def test_load_pdf_results():
    """Test the load PDF results endpoint"""
    
    print("🔍 Testing Load PDF Results")
    print("=" * 40)
    
    # Test load PDF results
    print("1. Testing load PDF results endpoint...")
    try:
        response = requests.post(f"{API_BASE}/load-pdf-results", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Entities loaded: {result.get('entities_loaded', 0)}")
            print(f"   Relationships loaded: {result.get('relationships_loaded', 0)}")
            
            if result.get('success'):
                print("   ✅ Load PDF results working!")
            else:
                print("   ❌ Load failed")
                
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection error - is server running?")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test get entities after loading
    print("\n2. Testing entities endpoint after load...")
    try:
        response = requests.get(f"{API_BASE}/entities", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            entities = result.get('entities', [])
            print(f"   Entities found: {len(entities)}")
            
            if entities:
                print("   ✅ Entities loaded successfully!")
                for i, entity in enumerate(entities[:3]):  # Show first 3
                    print(f"     {i+1}. {entity.get('label', 'No label')}")
            else:
                print("   ❌ No entities found")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    test_load_pdf_results()

if __name__ == "__main__":
    main()