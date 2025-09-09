#!/usr/bin/env python3
"""
Test import endpoints after server restart
"""

import requests
import json
import time

def test_endpoints():
    """Test if import endpoints are available"""
    base_url = "http://localhost:9000/api/expert-review"
    
    # Test data
    test_data = {
        "data": {
            "entities": [
                {
                    "entity_type": "component",
                    "label": "HTTP Test Component",
                    "description": "Component for HTTP endpoint testing",
                    "component_type": "Test",
                    "metadata": {
                        "confidence_score": 0.8,
                        "validation_status": "pending_review"
                    }
                }
            ],
            "relationships": []
        },
        "expert_id": "test_expert",
        "import_mode": "merge",
        "validate_only": True
    }
    
    print("Testing import endpoints...")
    
    # Test validation endpoint
    try:
        response = requests.post(
            f"{base_url}/import-entities-json",
            json=test_data,
            timeout=10
        )
        
        print(f"Validation endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Validation success: {result.get('success', False)}")
            print("✓ Import endpoints are working!")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

def check_server():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:9000/api/expert-review/dashboard/overview", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    if check_server():
        print("Server is running ✓")
        if test_endpoints():
            print("\n🎉 Import functionality is ready!")
            print("\nTo test in the browser:")
            print("1. Open http://localhost:9000")
            print("2. Click 'Import Data' button")
            print("3. Upload the sample_import_data.json file")
        else:
            print("\n⚠️  Import endpoints not available yet")
            print("The server may need to be restarted to pick up new endpoints")
    else:
        print("❌ Server is not running")
        print("Please start with: python launch_dashboard.py")