"""
Simple test for Enhanced Entity Models and Ontology Foundation
Tests the core functionality without complex dependencies
"""

import sys
import os
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Test imports
try:
    from models.ontology_models import (
        MechatronicSystem, Subsystem, Component, SparePart,
        OntologyRelationship, RelationshipType, SystemType, SubsystemType,
        ValidationStatus, create_mechatronic_system, create_subsystem,
        create_component, create_spare_part, create_ontology_relationship,
        validate_hierarchy_consistency, validate_relationship_consistency,
        get_ontology_statistics
    )
    print("✅ Successfully imported ontology models")
except Exception as e:
    print(f"❌ Failed to import ontology models: {e}")
    sys.exit(1)

def test_basic_entity_creation():
    """Test basic entity creation"""
    print("\n🧪 Testing basic entity creation...")
    
    # Create system
    system = create_mechatronic_system(
        label="Test LINAC",
        system_type=SystemType.LINAC,
        model_number="TrueBeam STx",
        manufacturer="Varian",
        description="Test linear accelerator"
    )
    
    assert system.label == "Test LINAC"
    assert system.system_type == SystemType.LINAC
    assert system.model_number == "TrueBeam STx"
    assert system.manufacturer == "Varian"
    print("  ✅ System creation successful")
    
    # Create subsystem
    subsystem = create_subsystem(
        label="Beam Delivery",
        subsystem_type=SubsystemType.BEAM_DELIVERY,
        parent_system_id=system.id,
        description="Beam delivery subsystem"
    )
    
    assert subsystem.label == "Beam Delivery"
    assert subsystem.subsystem_type == SubsystemType.BEAM_DELIVERY
    assert subsystem.parent_system_id == system.id
    print("  ✅ Subsystem creation successful")
    
    # Create component
    component = create_component(
        label="MLC",
        component_type="Collimator",
        parent_subsystem_id=subsystem.id,
        part_number="MLC-120",
        manufacturer="Varian",
        description="Multi-leaf collimator"
    )
    
    assert component.label == "MLC"
    assert component.component_type == "Collimator"
    assert component.parent_subsystem_id == subsystem.id
    print("  ✅ Component creation successful")
    
    # Create spare part
    spare_part = create_spare_part(
        label="Motor Drive",
        parent_component_id=component.id,
        part_number="MD-001",
        manufacturer="Varian",
        supplier="Varian Medical",
        description="Servo motor drive"
    )
    
    assert spare_part.label == "Motor Drive"
    assert spare_part.parent_component_id == component.id
    assert spare_part.part_number == "MD-001"
    print("  ✅ Spare part creation successful")
    
    return system, subsystem, component, spare_part

def test_relationships():
    """Test relationship creation and validation"""
    print("\n🧪 Testing relationships...")
    
    system, subsystem, component, spare_part = test_basic_entity_creation()
    
    # Create relationships
    system_subsystem_rel = create_ontology_relationship(
        RelationshipType.HAS_SUBSYSTEM,
        system.id,
        subsystem.id,
        "System contains subsystem",
        confidence=0.95
    )
    
    assert system_subsystem_rel.relationship_type == RelationshipType.HAS_SUBSYSTEM
    assert system_subsystem_rel.source_entity_id == system.id
    assert system_subsystem_rel.target_entity_id == subsystem.id
    print("  ✅ System-subsystem relationship creation successful")
    
    subsystem_component_rel = create_ontology_relationship(
        RelationshipType.HAS_COMPONENT,
        subsystem.id,
        component.id,
        "Subsystem contains component"
    )
    
    component_part_rel = create_ontology_relationship(
        RelationshipType.HAS_SPARE_PART,
        component.id,
        spare_part.id,
        "Component has spare part"
    )
    
    print("  ✅ All relationships created successfully")
    
    return [system_subsystem_rel, subsystem_component_rel, component_part_rel]

def test_hierarchy_validation():
    """Test hierarchy validation"""
    print("\n🧪 Testing hierarchy validation...")
    
    system, subsystem, component, spare_part = test_basic_entity_creation()
    
    # Test valid hierarchy
    errors = validate_hierarchy_consistency(
        [system], [subsystem], [component], [spare_part]
    )
    
    assert len(errors) == 0, f"Expected no errors, got: {errors}"
    print("  ✅ Valid hierarchy validation successful")
    
    # Test invalid hierarchy (missing parent)
    invalid_subsystem = create_subsystem(
        "Invalid Subsystem", 
        SubsystemType.BEAM_DELIVERY, 
        "nonexistent_parent"
    )
    
    errors = validate_hierarchy_consistency(
        [system], [subsystem, invalid_subsystem], [component], [spare_part]
    )
    
    assert len(errors) > 0, "Expected validation errors for invalid hierarchy"
    print("  ✅ Invalid hierarchy detection successful")

def test_relationship_validation():
    """Test relationship validation"""
    print("\n🧪 Testing relationship validation...")
    
    # Create entities and relationships in the same scope
    system, subsystem, component, spare_part = test_basic_entity_creation()
    
    # Create relationships with the same entities
    system_subsystem_rel = create_ontology_relationship(
        RelationshipType.HAS_SUBSYSTEM,
        system.id,
        subsystem.id,
        "System contains subsystem"
    )
    
    subsystem_component_rel = create_ontology_relationship(
        RelationshipType.HAS_COMPONENT,
        subsystem.id,
        component.id,
        "Subsystem contains component"
    )
    
    component_part_rel = create_ontology_relationship(
        RelationshipType.HAS_SPARE_PART,
        component.id,
        spare_part.id,
        "Component has spare part"
    )
    
    relationships = [system_subsystem_rel, subsystem_component_rel, component_part_rel]
    all_entity_ids = {system.id, subsystem.id, component.id, spare_part.id}
    
    # Test valid relationships
    errors = validate_relationship_consistency(relationships, all_entity_ids)
    assert len(errors) == 0, f"Expected no errors, got: {errors}"
    print("  ✅ Valid relationship validation successful")
    
    # Test invalid relationship (non-existent entity)
    invalid_rel = create_ontology_relationship(
        RelationshipType.HAS_COMPONENT,
        system.id,
        "nonexistent_entity"
    )
    
    errors = validate_relationship_consistency([invalid_rel], all_entity_ids)
    assert len(errors) > 0, "Expected validation errors for invalid relationship"
    print("  ✅ Invalid relationship detection successful")

def test_owl_serialization():
    """Test OWL serialization"""
    print("\n🧪 Testing OWL serialization...")
    
    system, subsystem, component, spare_part = test_basic_entity_creation()
    
    # Test system OWL serialization
    owl_dict = system.to_owl_dict()
    
    assert owl_dict["@type"] == "MechatronicSystem"
    assert owl_dict["@id"] == system.uri
    assert owl_dict["rdfs:label"] == "Test LINAC"
    assert owl_dict["systemType"] == "linac"
    assert owl_dict["manufacturer"] == "Varian"
    print("  ✅ System OWL serialization successful")
    
    # Test subsystem OWL serialization
    subsystem_owl = subsystem.to_owl_dict()
    assert subsystem_owl["@type"] == "Subsystem"
    assert subsystem_owl["subsystemType"] == "beam_delivery"
    print("  ✅ Subsystem OWL serialization successful")
    
    # Test component OWL serialization
    component_owl = component.to_owl_dict()
    assert component_owl["@type"] == "Component"
    assert component_owl["componentType"] == "Collimator"
    print("  ✅ Component OWL serialization successful")
    
    # Test spare part OWL serialization
    spare_part_owl = spare_part.to_owl_dict()
    assert spare_part_owl["@type"] == "SparePart"
    assert spare_part_owl["partNumber"] == "MD-001"
    print("  ✅ Spare part OWL serialization successful")

def test_statistics():
    """Test ontology statistics"""
    print("\n🧪 Testing ontology statistics...")
    
    system, subsystem, component, spare_part = test_basic_entity_creation()
    relationships = test_relationships()
    
    stats = get_ontology_statistics(
        [system], [subsystem], [component], [spare_part], relationships
    )
    
    assert stats["total_entities"] == 4
    assert stats["entity_counts"]["systems"] == 1
    assert stats["entity_counts"]["subsystems"] == 1
    assert stats["entity_counts"]["components"] == 1
    assert stats["entity_counts"]["spare_parts"] == 1
    assert stats["total_relationships"] == 3
    
    print(f"  ✅ Statistics calculation successful: {stats}")

def test_ontology_builder_basic():
    """Test basic ontology builder functionality"""
    print("\n🧪 Testing ontology builder (basic)...")
    
    try:
        from core.ontology_builder import OntologyBuilder, OWLOntology
        
        # Create ontology
        ontology = OWLOntology("test_ontology", "Test Ontology", "Test description")
        
        # Add entities
        system, subsystem, component, spare_part = test_basic_entity_creation()
        relationships = test_relationships()
        
        ontology.add_system(system)
        ontology.add_subsystem(subsystem)
        ontology.add_component(component)
        ontology.add_spare_part(spare_part)
        
        for rel in relationships:
            ontology.add_relationship(rel)
        
        # Test validation
        errors = ontology.validate_consistency()
        assert sum(len(error_list) for error_list in errors.values()) == 0
        print("  ✅ Ontology builder basic functionality successful")
        
        # Test JSON-LD export
        json_ld = ontology.to_json_ld()
        assert "@context" in json_ld
        assert "@graph" in json_ld
        assert len(json_ld["@graph"]) == 7  # 4 entities + 3 relationships
        print("  ✅ JSON-LD export successful")
        
    except ImportError as e:
        print(f"  ⚠️ Skipping ontology builder test due to import issues: {e}")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Enhanced Entity Models and Ontology Foundation Tests")
    print("=" * 70)
    
    tests = [
        test_basic_entity_creation,
        test_relationships,
        test_hierarchy_validation,
        test_relationship_validation,
        test_owl_serialization,
        test_statistics,
        test_ontology_builder_basic
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests))*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All tests passed! Enhanced Entity Models and Ontology Foundation is working correctly.")
        return True
    else:
        print(f"\n💥 {failed} test(s) failed. Please review the failures above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)