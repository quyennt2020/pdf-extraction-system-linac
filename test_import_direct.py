#!/usr/bin/env python3
"""
Direct test of import functionality without HTTP requests
Tests the import logic directly by calling the functions
"""

import json
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.append('.')

# Import the functions directly
from backend.api.expert_review_api import process_import_data, ontology_data

# Sample data
sample_data = {
    "entities": [
        {
            "entity_type": "component",
            "label": "Test Component 1",
            "description": "A test component for import testing",
            "component_type": "Test",
            "part_number": "TC-001",
            "manufacturer": "Test Corp",
            "metadata": {
                "confidence_score": 0.8,
                "validation_status": "pending_review"
            }
        },
        {
            "entity_type": "component",
            "label": "Test Component 2", 
            "description": "Another test component",
            "component_type": "Test",
            "part_number": "TC-002",
            "manufacturer": "Test Corp",
            "metadata": {
                "confidence_score": 0.9,
                "validation_status": "expert_approved"
            }
        }
    ],
    "relationships": [
        {
            "relationship_type": "connected_to",
            "source_entity_id": "test_comp_1",
            "target_entity_id": "test_comp_2",
            "description": "Test components are connected"
        }
    ]
}

async def test_import_validation():
    """Test import validation"""
    print("=== Testing Import Validation ===")
    
    # Clear existing data
    ontology_data["components"].clear()
    ontology_data["relationships"].clear()
    
    result = await process_import_data(
        sample_data, 
        "test_expert", 
        "merge", 
        validate_only=True
    )
    
    print(f"Validation Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    stats = result['stats']
    print(f"Entities processed: {stats['entities_processed']}")
    print(f"Entities valid: {stats['entities_imported']}")
    print(f"Relationships processed: {stats['relationships_processed']}")
    print(f"Relationships valid: {stats['relationships_imported']}")
    
    if stats['errors']:
        print("Errors:")
        for error in stats['errors']:
            print(f"  - {error}")
    
    if stats['warnings']:
        print("Warnings:")
        for warning in stats['warnings']:
            print(f"  - {warning}")
    
    return result['success']

async def test_import_actual():
    """Test actual import"""
    print("\n=== Testing Actual Import ===")
    
    # Clear existing data
    ontology_data["components"].clear()
    ontology_data["relationships"].clear()
    
    print(f"Components before import: {len(ontology_data['components'])}")
    print(f"Relationships before import: {len(ontology_data['relationships'])}")
    
    result = await process_import_data(
        sample_data,
        "test_expert",
        "merge",
        validate_only=False
    )
    
    print(f"Import Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    stats = result['stats']
    print(f"Entities imported: {stats['entities_imported']}")
    print(f"Relationships imported: {stats['relationships_imported']}")
    
    print(f"Components after import: {len(ontology_data['components'])}")
    print(f"Relationships after import: {len(ontology_data['relationships'])}")
    
    # Show imported entities
    if ontology_data['components']:
        print("\nImported Components:")
        for comp in ontology_data['components']:
            print(f"  - {comp.label} ({comp.component_type})")
            print(f"    Confidence: {comp.metadata.confidence_score}")
            print(f"    Status: {comp.metadata.validation_status.value}")
    
    if ontology_data['relationships']:
        print("\nImported Relationships:")
        for rel in ontology_data['relationships']:
            print(f"  - {rel.relationship_type.value}: {rel.source_entity_id} -> {rel.target_entity_id}")
    
    if stats['errors']:
        print("Errors:")
        for error in stats['errors']:
            print(f"  - {error}")
    
    return result['success']

async def test_duplicate_detection():
    """Test duplicate detection"""
    print("\n=== Testing Duplicate Detection ===")
    
    # Import the same data again to test duplicate detection
    result = await process_import_data(
        sample_data,
        "test_expert",
        "merge",  # Should skip duplicates
        validate_only=False
    )
    
    print(f"Duplicate Import Success: {result['success']}")
    stats = result['stats']
    print(f"Entities processed: {stats['entities_processed']}")
    print(f"Entities imported: {stats['entities_imported']}")
    print(f"Entities skipped: {stats['entities_skipped']}")
    
    print(f"Total components after duplicate test: {len(ontology_data['components'])}")
    
    return result['success']

async def main():
    """Main test function"""
    print("Direct Import Functionality Test")
    print("=" * 40)
    
    try:
        # Test validation
        validation_success = await test_import_validation()
        
        if validation_success:
            print("✓ Validation test passed")
            
            # Test actual import
            import_success = await test_import_actual()
            
            if import_success:
                print("✓ Import test passed")
                
                # Test duplicate detection
                duplicate_success = await test_duplicate_detection()
                
                if duplicate_success:
                    print("✓ Duplicate detection test passed")
                else:
                    print("✗ Duplicate detection test failed")
            else:
                print("✗ Import test failed")
        else:
            print("✗ Validation test failed")
    
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 40)
    print("Direct test completed!")

if __name__ == "__main__":
    asyncio.run(main())