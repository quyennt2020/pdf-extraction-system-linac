#!/usr/bin/env python3
"""
Test script for entity import functionality
Creates sample import data and tests the import API endpoints
"""

import json
import requests
import sys
from pathlib import Path

# Sample import data
sample_data = {
    "entities": [
        {
            "entity_type": "system",
            "label": "LINAC TrueBeam 001",
            "description": "Linear Accelerator for radiation therapy",
            "system_type": "linac",
            "model_number": "TrueBeam STx",
            "manufacturer": "Varian Medical Systems",
            "metadata": {
                "confidence_score": 0.9,
                "validation_status": "pending_review"
            }
        },
        {
            "entity_type": "subsystem", 
            "label": "Beam Delivery System",
            "description": "System responsible for beam generation and delivery",
            "subsystem_type": "beam_delivery",
            "parent_system_id": "system_001",
            "metadata": {
                "confidence_score": 0.85,
                "validation_status": "pending_review"
            }
        },
        {
            "entity_type": "component",
            "label": "Multi-Leaf Collimator",
            "description": "120-leaf collimator for beam shaping",
            "component_type": "Collimator",
            "part_number": "MLC-120",
            "manufacturer": "Varian",
            "parent_subsystem_id": "subsystem_001",
            "metadata": {
                "confidence_score": 0.8,
                "validation_status": "pending_review"
            }
        },
        {
            "entity_type": "spare_part",
            "label": "Leaf Drive Motor",
            "description": "Servo motor for individual leaf positioning",
            "parent_component_id": "component_001",
            "part_number": "LDM-001",
            "manufacturer": "Varian",
            "supplier": "Varian Medical Systems",
            "metadata": {
                "confidence_score": 0.75,
                "validation_status": "not_validated"
            }
        }
    ],
    "relationships": [
        {
            "relationship_type": "has_subsystem",
            "source_entity_id": "system_001",
            "target_entity_id": "subsystem_001",
            "description": "LINAC system contains beam delivery subsystem"
        },
        {
            "relationship_type": "has_component",
            "source_entity_id": "subsystem_001", 
            "target_entity_id": "component_001",
            "description": "Beam delivery subsystem contains MLC component"
        },
        {
            "relationship_type": "has_spare_part",
            "source_entity_id": "component_001",
            "target_entity_id": "spare_part_001",
            "description": "MLC component uses leaf drive motor"
        }
    ]
}

def create_sample_file():
    """Create sample import file"""
    sample_file = Path("sample_import_data.json")
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2)
    print(f"Created sample import file: {sample_file}")
    return sample_file

def test_validation_api():
    """Test the validation API endpoint"""
    print("\n=== Testing Validation API ===")
    
    url = "http://localhost:9000/api/expert-review/import-entities-json"
    payload = {
        "data": sample_data,
        "expert_id": "test_expert",
        "import_mode": "merge",
        "validate_only": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Validation Result:")
            print(f"  Success: {result['success']}")
            print(f"  Message: {result['message']}")
            
            stats = result.get('stats', {})
            print(f"  Entities processed: {stats.get('entities_processed', 0)}")
            print(f"  Entities valid: {stats.get('entities_imported', 0)}")
            print(f"  Relationships processed: {stats.get('relationships_processed', 0)}")
            
            if stats.get('errors'):
                print("  Errors:")
                for error in stats['errors']:
                    print(f"    - {error}")
                    
            if stats.get('warnings'):
                print("  Warnings:")
                for warning in stats['warnings']:
                    print(f"    - {warning}")
                    
            return result['success']
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

def test_import_api():
    """Test the actual import API endpoint"""
    print("\n=== Testing Import API ===")
    
    url = "http://localhost:9000/api/expert-review/import-entities-json"
    payload = {
        "data": sample_data,
        "expert_id": "test_expert", 
        "import_mode": "merge",
        "validate_only": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Import Result:")
            print(f"  Success: {result['success']}")
            print(f"  Message: {result['message']}")
            
            stats = result.get('stats', {})
            print(f"  Entities imported: {stats.get('entities_imported', 0)}")
            print(f"  Relationships imported: {stats.get('relationships_imported', 0)}")
            
            if stats.get('errors'):
                print("  Errors:")
                for error in stats['errors']:
                    print(f"    - {error}")
                    
            return result['success']
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

def test_file_upload_api():
    """Test the file upload API endpoint"""
    print("\n=== Testing File Upload API ===")
    
    # Create sample file
    sample_file = create_sample_file()
    
    url = "http://localhost:9000/api/expert-review/import-entities"
    
    try:
        with open(sample_file, 'rb') as f:
            files = {'file': ('sample_import_data.json', f, 'application/json')}
            data = {
                'expert_id': 'test_expert',
                'import_mode': 'merge'
            }
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("File Upload Result:")
            print(f"  Success: {result['success']}")
            print(f"  Message: {result['message']}")
            
            stats = result.get('stats', {})
            print(f"  Entities imported: {stats.get('entities_imported', 0)}")
            print(f"  Relationships imported: {stats.get('relationships_imported', 0)}")
            
            return result['success']
        else:
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    finally:
        # Clean up
        if sample_file.exists():
            sample_file.unlink()

def check_dashboard_status():
    """Check if dashboard is running"""
    try:
        response = requests.get("http://localhost:9000/api/expert-review/dashboard/overview", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("Entity Import Functionality Test")
    print("=" * 40)
    
    # Check if dashboard is running
    if not check_dashboard_status():
        print("ERROR: Dashboard is not running!")
        print("Please start the dashboard first with: python launch_dashboard.py")
        sys.exit(1)
    
    print("Dashboard is running ✓")
    
    # Create sample file for manual testing
    create_sample_file()
    
    # Test validation
    validation_success = test_validation_api()
    
    if validation_success:
        print("\nValidation test passed ✓")
        
        # Test import
        import_success = test_import_api()
        
        if import_success:
            print("Import test passed ✓")
        else:
            print("Import test failed ✗")
            
        # Test file upload
        upload_success = test_file_upload_api()
        
        if upload_success:
            print("File upload test passed ✓")
        else:
            print("File upload test failed ✗")
            
    else:
        print("Validation test failed ✗")
    
    print("\n" + "=" * 40)
    print("Test completed!")
    print("\nTo test the UI:")
    print("1. Open http://localhost:9000 in your browser")
    print("2. Click 'Import Data' button")
    print("3. Upload the generated 'sample_import_data.json' file")

if __name__ == "__main__":
    main()