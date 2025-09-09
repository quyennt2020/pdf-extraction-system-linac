#!/usr/bin/env python3
"""
Complete test workflow for import functionality using sample PDF
1. Creates sample PDF content
2. Processes it through the extraction pipeline  
3. Tests the import functionality with the extracted data
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append('.')

def create_sample_content():
    """Create sample service manual content and save as text"""
    print("📄 Step 1: Creating sample service manual content...")
    
    from create_sample_pdf import save_as_text_file, create_simple_html_version
    
    # Create both text and HTML versions
    text_file = save_as_text_file()
    html_file = create_simple_html_version()
    
    print(f"✅ Sample content created:")
    print(f"   - Text: {text_file}")
    print(f"   - HTML: {html_file}")
    
    return text_file, html_file

def simulate_pdf_extraction():
    """Simulate PDF extraction by creating entities from the sample content"""
    print("\n🔍 Step 2: Simulating PDF extraction...")
    
    # Read the sample content
    text_file = "data/input_pdfs/sample_service_manual.txt"
    if not os.path.exists(text_file):
        print("❌ Sample text file not found. Creating it first...")
        create_sample_content()
    
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract entities manually (simulating AI extraction)
    entities = []
    relationships = []
    
    # Systems
    entities.append({
        "id": "system_001",
        "entity_type": "system",
        "label": "TrueBeam STx Linear Accelerator",
        "description": "Linear Accelerator for radiation therapy",
        "system_type": "linac",
        "model_number": "TrueBeam STx",
        "manufacturer": "Varian Medical Systems",
        "metadata": {
            "confidence_score": 0.95,
            "validation_status": "pending_review",
            "source_document": "sample_service_manual.txt",
            "extraction_method": "simulated"
        }
    })
    
    # Subsystems
    entities.append({
        "id": "subsystem_001",
        "entity_type": "subsystem",
        "label": "Multi-Leaf Collimator System",
        "description": "120 tungsten leaves arranged in two banks for precise beam shaping",
        "subsystem_type": "beam_delivery",
        "parent_system_id": "system_001",
        "metadata": {
            "confidence_score": 0.92,
            "validation_status": "pending_review",
            "source_document": "sample_service_manual.txt"
        }
    })
    
    entities.append({
        "id": "subsystem_002", 
        "entity_type": "subsystem",
        "label": "Gantry System",
        "description": "Gantry rotation system with servo motor drive and high-precision encoder",
        "subsystem_type": "mechanical",
        "parent_system_id": "system_001",
        "metadata": {
            "confidence_score": 0.90,
            "validation_status": "pending_review",
            "source_document": "sample_service_manual.txt"
        }
    })
    
    entities.append({
        "id": "subsystem_003",
        "entity_type": "subsystem", 
        "label": "Patient Support System",
        "description": "Treatment couch with 6-degree-of-freedom positioning",
        "subsystem_type": "mechanical",
        "parent_system_id": "system_001",
        "metadata": {
            "confidence_score": 0.88,
            "validation_status": "pending_review",
            "source_document": "sample_service_manual.txt"
        }
    })
    
    # Components
    components_data = [
        ("component_001", "MLC Controller Unit", "MLC-CTRL-2000", "subsystem_001", "Controller"),
        ("component_002", "Leaf Drive Motor", "LDM-001-V3", "subsystem_001", "Motor"),
        ("component_003", "Position Encoder", "ENC-HD-500", "subsystem_001", "Sensor"),
        ("component_004", "Motor Driver Card", "MDC-24V-100", "subsystem_001", "Driver"),
        ("component_005", "Safety Interlock System", "SIS-MLC-200", "subsystem_001", "Safety"),
        ("component_006", "Gantry Drive Motor", "GDM-5KW-SR", "subsystem_002", "Motor"),
        ("component_007", "Gantry Position Encoder", "GPE-ABS-19BIT", "subsystem_002", "Sensor"),
        ("component_008", "Motor Controller", "MC-SERVO-5K", "subsystem_002", "Controller"),
        ("component_009", "Brake System", "BRK-ELEC-500", "subsystem_002", "Safety"),
        ("component_010", "Couch Drive Motor", "CDM-SERVO-2K", "subsystem_003", "Motor"),
        ("component_011", "Position Sensor", "PS-LINEAR-500", "subsystem_003", "Sensor"),
        ("component_012", "Couch Controller", "CC-6DOF-MAIN", "subsystem_003", "Controller"),
        ("component_013", "Load Cell Assembly", "LC-2000KG", "subsystem_003", "Sensor")
    ]
    
    for comp_id, label, part_num, parent_id, comp_type in components_data:
        entities.append({
            "id": comp_id,
            "entity_type": "component",
            "label": label,
            "description": f"{comp_type} component for medical device system",
            "component_type": comp_type,
            "part_number": part_num,
            "manufacturer": "Varian Medical Systems",
            "parent_subsystem_id": parent_id,
            "metadata": {
                "confidence_score": 0.85,
                "validation_status": "not_validated",
                "source_document": "sample_service_manual.txt"
            }
        })
    
    # Spare Parts
    spare_parts_data = [
        ("spare_001", "Air Filter", "FILT-AIR-MLC", "component_001"),
        ("spare_002", "Leaf Guide Rail", "LGR-TUNG-120", "component_002"),
        ("spare_003", "Drive Belt", "BELT-COUCH-XL", "component_010"),
        ("spare_004", "Safety Interlock Module", "SIM-MLC-001", "component_005")
    ]
    
    for spare_id, label, part_num, parent_id in spare_parts_data:
        entities.append({
            "id": spare_id,
            "entity_type": "spare_part",
            "label": label,
            "description": f"Replacement part for {parent_id}",
            "part_number": part_num,
            "manufacturer": "Varian Medical Systems",
            "parent_component_id": parent_id,
            "metadata": {
                "confidence_score": 0.80,
                "validation_status": "not_validated",
                "source_document": "sample_service_manual.txt"
            }
        })
    
    # Relationships
    relationships_data = [
        ("has_subsystem", "system_001", "subsystem_001", "System contains MLC subsystem"),
        ("has_subsystem", "system_001", "subsystem_002", "System contains gantry subsystem"),
        ("has_subsystem", "system_001", "subsystem_003", "System contains patient support subsystem"),
        ("has_component", "subsystem_001", "component_001", "MLC subsystem contains controller"),
        ("has_component", "subsystem_001", "component_002", "MLC subsystem contains drive motor"),
        ("has_component", "subsystem_001", "component_003", "MLC subsystem contains encoder"),
        ("has_component", "subsystem_002", "component_006", "Gantry subsystem contains drive motor"),
        ("has_component", "subsystem_002", "component_007", "Gantry subsystem contains encoder"),
        ("has_component", "subsystem_003", "component_010", "Couch subsystem contains drive motor"),
        ("has_spare_part", "component_001", "spare_001", "Controller uses air filter"),
        ("has_spare_part", "component_002", "spare_002", "Motor uses guide rail"),
        ("connected_to", "component_002", "component_003", "Motor connected to encoder"),
        ("controlled_by", "component_002", "component_004", "Motor controlled by driver card")
    ]
    
    for rel_type, source_id, target_id, description in relationships_data:
        relationships.append({
            "relationship_type": rel_type,
            "source_entity_id": source_id,
            "target_entity_id": target_id,
            "description": description
        })
    
    # Create extraction results
    extraction_data = {
        "entities": entities,
        "relationships": relationships,
        "extraction_metadata": {
            "source_file": "sample_service_manual.txt",
            "extraction_method": "simulated",
            "timestamp": datetime.now().isoformat(),
            "total_entities": len(entities),
            "total_relationships": len(relationships)
        }
    }
    
    # Save extraction results
    os.makedirs("data/sample_extraction_results", exist_ok=True)
    results_file = "data/sample_extraction_results/sample_entities.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(extraction_data, f, indent=2)
    
    print(f"✅ Simulated extraction completed:")
    print(f"   - Entities: {len(entities)}")
    print(f"   - Relationships: {len(relationships)}")
    print(f"   - Results saved to: {results_file}")
    
    return extraction_data, results_file

def test_import_api(extraction_data):
    """Test the import API with extracted data"""
    print("\n🔄 Step 3: Testing import API...")
    
    # Check if dashboard is running
    try:
        response = requests.get("http://localhost:9000/api/expert-review/dashboard/overview", timeout=5)
        if response.status_code != 200:
            print("❌ Dashboard is not running on port 9000")
            return False
    except:
        print("❌ Dashboard is not running. Please start with: python launch_dashboard.py")
        return False
    
    print("✅ Dashboard is running")
    
    # Test validation first
    print("\n📋 Testing validation...")
    validation_payload = {
        "data": {
            "entities": extraction_data["entities"],
            "relationships": extraction_data["relationships"]
        },
        "expert_id": "test_expert",
        "import_mode": "merge",
        "validate_only": True
    }
    
    try:
        response = requests.post(
            "http://localhost:9000/api/expert-review/import-entities-json",
            json=validation_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Validation successful: {result['success']}")
            
            stats = result.get('stats', {})
            print(f"   - Entities processed: {stats.get('entities_processed', 0)}")
            print(f"   - Entities valid: {stats.get('entities_imported', 0)}")
            print(f"   - Relationships processed: {stats.get('relationships_processed', 0)}")
            
            if stats.get('errors'):
                print("   - Errors found:")
                for error in stats['errors'][:5]:  # Show first 5 errors
                    print(f"     • {error}")
            
            if not result['success']:
                print("❌ Validation failed")
                return False
                
        else:
            print(f"❌ Validation request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Validation request error: {e}")
        return False
    
    # Test actual import
    print("\n📥 Testing actual import...")
    import_payload = {
        "data": {
            "entities": extraction_data["entities"],
            "relationships": extraction_data["relationships"]
        },
        "expert_id": "test_expert",
        "import_mode": "replace",  # Replace existing data
        "validate_only": False
    }
    
    try:
        response = requests.post(
            "http://localhost:9000/api/expert-review/import-entities-json",
            json=import_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Import successful: {result['success']}")
            
            stats = result.get('stats', {})
            print(f"   - Entities imported: {stats.get('entities_imported', 0)}")
            print(f"   - Relationships imported: {stats.get('relationships_imported', 0)}")
            
            if stats.get('errors'):
                print("   - Import errors:")
                for error in stats['errors'][:3]:
                    print(f"     • {error}")
            
            return result['success']
            
        else:
            print(f"❌ Import request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Import request error: {e}")
        return False

def test_dashboard_ui():
    """Test dashboard UI after import"""
    print("\n🖥️ Step 4: Verifying dashboard data...")
    
    try:
        # Check overview
        response = requests.get("http://localhost:9000/api/expert-review/dashboard/overview", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard overview:")
            print(f"   - Total entities: {data.get('total_entities', 0)}")
            print(f"   - Systems: {data.get('entity_counts', {}).get('systems', 0)}")
            print(f"   - Subsystems: {data.get('entity_counts', {}).get('subsystems', 0)}")
            print(f"   - Components: {data.get('entity_counts', {}).get('components', 0)}")
            print(f"   - Spare parts: {data.get('entity_counts', {}).get('spare_parts', 0)}")
            print(f"   - Relationships: {data.get('total_relationships', 0)}")
            
            return True
        else:
            print(f"❌ Failed to get dashboard overview: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Dashboard check error: {e}")
        return False

def create_import_file_for_ui_test(extraction_data):
    """Create a JSON file for UI testing"""
    print("\n📁 Step 5: Creating import file for UI testing...")
    
    # Create a smaller subset for UI testing
    ui_test_data = {
        "entities": extraction_data["entities"][:10],  # First 10 entities
        "relationships": extraction_data["relationships"][:8]  # First 8 relationships
    }
    
    ui_test_file = "sample_import_for_ui_test.json"
    with open(ui_test_file, 'w', encoding='utf-8') as f:
        json.dump(ui_test_data, f, indent=2)
    
    print(f"✅ UI test file created: {ui_test_file}")
    print(f"   - Contains {len(ui_test_data['entities'])} entities")
    print(f"   - Contains {len(ui_test_data['relationships'])} relationships")
    
    return ui_test_file

def main():
    """Main test workflow"""
    print("🧪 Complete Import Functionality Test with Sample PDF")
    print("=" * 60)
    
    try:
        # Step 1: Create sample content
        text_file, html_file = create_sample_content()
        
        # Step 2: Simulate extraction
        extraction_data, results_file = simulate_pdf_extraction()
        
        # Step 3: Test import API
        import_success = test_import_api(extraction_data)
        
        if import_success:
            # Step 4: Verify dashboard
            dashboard_success = test_dashboard_ui()
            
            if dashboard_success:
                # Step 5: Create UI test file
                ui_test_file = create_import_file_for_ui_test(extraction_data)
                
                print(f"\n🎉 All tests completed successfully!")
                print(f"\n📋 Next Steps - Test the UI:")
                print(f"   1. Open http://localhost:9000 in your browser")
                print(f"   2. Click 'Import Data' button")
                print(f"   3. Upload '{ui_test_file}'")
                print(f"   4. Test validation and import process")
                
                print(f"\n📄 Files created for testing:")
                print(f"   - Sample content: {text_file}")
                print(f"   - HTML version: {html_file}")
                print(f"   - Extraction results: {results_file}")
                print(f"   - UI test file: {ui_test_file}")
                
                return True
            else:
                print("❌ Dashboard verification failed")
                return False
        else:
            print("❌ Import API test failed")
            return False
            
    except Exception as e:
        print(f"❌ Test workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)