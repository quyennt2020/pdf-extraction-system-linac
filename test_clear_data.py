"""
Test script to check the clear-data endpoint
"""

import requests
import json

def test_clear_data():
    """Test the clear-data endpoint"""
    
    base_url = "http://localhost:9000/api/expert-review"
    
    try:
        # Test clear-data endpoint
        print("Testing clear-data endpoint...")
        response = requests.post(f"{base_url}/clear-data")
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Clear data endpoint works correctly")
            else:
                print(f"❌ Clear data failed: {result.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the dashboard is running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_clear_data()