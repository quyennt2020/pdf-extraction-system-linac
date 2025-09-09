"""
Test suite for Enhanced Entity Models and Ontology Foundation
Tests the hierarchical entity models, OWL ontology construction, and validation framework
"""

import pytest
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from models.ontology_models import (
    MechatronicSystem, Subsystem, Component, SparePart,
    OntologyRelationship, RelationshipType, SystemType, SubsystemType,
    ValidationStatus, create_mechatronic_system, create_subsystem,
    create_component, create_spare_part, create_ontology_relationship,
    validate_hierarchy_consistency, validate_relationship_consistency,
    get_ontology_statistics
)

from core.ontology_builder import OntologyBuilder, OWLOntology
from verification.ontology_validator import OntologyValidator, ValidationSeverity


class TestOntologyModels:
    """Test the ontology data models"""
    
    def test_mechatronic_system_creation(self):
        """Test creating a mechatronic system"""
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
        assert system.description == "Test linear accelerator"
        assert system.id is not None
        assert system.uri.startswith("http://medical-device-ontology.org/")
    
    def test_subsystem_creation(self):
        """Test creating a subsystem"""
        system = create_mechatronic_system("Parent System", SystemType.LINAC)
        
        subsystem = create_subsystem(
            label="Beam Delivery",
            subsystem_type=SubsystemType.BEAM_DELIVERY,
            parent_system_id=system.id,
            description="Beam delivery subsystem"
        )
        
        assert subsystem.label == "Beam Delivery"
        assert subsystem.subsystem_type == SubsystemType.BEAM_DELIVERY
        assert subsystem.parent_system_id == system.id
        assert subsystem.description == "Beam delivery subsystem"
    
    def test_component_creation(self):
        """Test creating a component"""
        system = create_mechatronic_system("Test System", SystemType.LINAC)
        subsystem = create_subsystem("Test Subsystem", SubsystemType.BEAM_DELIVERY, system.id)
        
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
        assert component.part_number == "MLC-120"
        assert component.manufacturer == "Varian"
    
    def test_spare_part_creation(self):
        """Test creating a spare part"""
        system = create_mechatronic_system("Test System", SystemType.LINAC)
        subsystem = create_subsystem("Test Subsystem", SubsystemType.BEAM_DELIVERY, system.id)
        component = create_component("Test Component", "Motor", subsystem.id)
        
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
        assert spare_part.manufacturer == "Varian"
        assert spare_part.supplier == "Varian Medical"
    
    def test_relationship_creation(self):
        """Test creating relationships"""
        system = create_mechatronic_system("Test System", SystemType.LINAC)
        subsystem = create_subsystem("Test Subsystem", SubsystemType.BEAM_DELIVERY, system.id)
        
        relationship = create_ontology_relationship(
            RelationshipType.HAS_SUBSYSTEM,
            system.id,
            subsystem.id,
            "System contains subsystem",
            confidence=0.95
        )
        
        assert relationship.relationship_type == RelationshipType.HAS_SUBSYSTEM
        assert relationship.source_entity_id == system.id
        assert relationship.target_entity_id == subsystem.id
        assert relationship.description == "System contains subsystem"
        assert relationship.metadata.confidence_score == 0.95
    
    def test_owl_serialization(self):
        """Test OWL serialization"""
        system = create_mechatronic_system(
            "Test LINAC",
            SystemType.LINAC,
            "TrueBeam",
            "Varian"
        )
        
        owl_dict = system.to_owl_dict()
        
        assert owl_dict["@type"] == "MechatronicSystem"
        assert owl_dict["@id"] == system.uri
        assert owl_dict["rdfs:label"] == "Test LINAC"
        assert owl_dict["systemType"] == "linac"
        assert owl_dict["manufacturer"] == "Varian"


class TestHierarchyValidation:
    """Test hierarchy validation functions"""
    
    def test_valid_hierarchy(self):
        """Test validation of valid hierarchy"""
        system = create_mechatronic_system("Test System", SystemType.LINAC)
        subsystem = create_subsystem("Test Subsystem", SubsystemType.BEAM_DELIVERY, system.id)
        component = create_component("Test Component", "Motor", subsystem.id)
        spare_part = create_spare_part("Test Part", component.id, "P001")
        
        errors = validate_hierarchy_consistency(
            [system], [subsystem], [component], [spare_part]
        )
        
        assert len(errors) == 0
    
    def test_invalid_hierarchy_missing_parent(self):
        """Test validation with missing parent references"""
        system = create_mechatronic_system("Test System", SystemType.LINAC)
        subsystem = create_subsystem("Test Subsystem", SubsystemType.BEAM_DELIVERY, "nonexistent_id")
        
        errors = validate_hierarchy_consistency([system], [subsystem], [], [])
        
        assert len(errors) == 1
        assert "non-existent system" in errors[0]
    
    def test_relationship_validation(self):
        """Test relationship validation"""
        system = create_mechatronic_system("Test System", SystemType.LINAC)
        subsystem = create_subsystem("Test Subsystem", SubsystemType.BEAM_DELIVERY, system.id)
        
        # Valid relationship
        valid_rel = create_ontology_relationship(
            RelationshipType.HAS_SUBSYSTEM, system.id, subsystem.id
        )
        
        # Invalid relationship with non-existent entity
        invalid_rel = create_ontology_relationship(
            RelationshipType.HAS_SUBSYSTEM, system.id, "nonexistent_id"
        )
        
        all_entity_ids = {system.id, subsystem.id}
        
        errors = validate_relationship_consistency([valid_rel, invalid_rel], all_entity_ids)
        
        assert len(errors) == 1
        assert "non-existent target entity" in errors[0]


class TestOntologyBuilder:
    """Test the ontology builder"""
    
    def test_create_linac_ontology(self):
        """Test creating a LINAC ontology"""
        builder = OntologyBuilder()
        ontology = builder.create_linac_ontology("test_linac")
        
        assert ontology.ontology_id == "test_linac"
        assert len(ontology.systems) == 1
        assert ontology.systems[0].system_type == SystemType.LINAC
        assert len(ontology.subsystems) >= 5  # Should have standard LINAC subsystems
        assert len(ontology.relationships) >= 5  # Should have system-subsystem relationships
    
    def test_ontology_validation(self):
        """Test ontology consistency validation"""
        builder = OntologyBuilder()
        ontology = builder.create_linac_ontology("test_validation")
        
        validation_result = builder.validate_ontology_consistency(ontology)
        
        assert validation_result["is_valid"] is True
        assert validation_result["errors"]["hierarchy_errors"] == []
        assert validation_result["errors"]["relationship_errors"] == []
        assert "statistics" in validation_result
    
    def test_ontology_statistics(self):
        """Test ontology statistics generation"""
        builder = OntologyBuilder()
        ontology = builder.create_linac_ontology("test_stats")
        
        stats = ontology.get_statistics()
        
        assert "total_entities" in stats
        assert "entity_counts" in stats
        assert "total_relationships" in stats
        assert stats["entity_counts"]["systems"] == 1
        assert stats["entity_counts"]["subsystems"] > 0
        assert stats["total_relationships"] > 0
    
    def test_json_ld_export(self):
        """Test JSON-LD export"""
        builder = OntologyBuilder()
        ontology = builder.create_linac_ontology("test_export")
        
        json_ld = ontology.to_json_ld()
        
        assert "@context" in json_ld
        assert "@type" in json_ld
        assert json_ld["@type"] == "owl:Ontology"
        assert "@graph" in json_ld
        assert len(json_ld["@graph"]) > 0
        
        # Check that all entities are in the graph
        expected_entities = (
            len(ontology.systems) + 
            len(ontology.subsystems) + 
            len(ontology.components) + 
            len(ontology.spare_parts) +
            len(ontology.relationships)
        )
        assert len(json_ld["@graph"]) == expected_entities


class TestOntologyValidator:
    """Test the ontology validation framework"""
    
    def test_validator_initialization(self):
        """Test validator initialization with default rules"""
        validator = OntologyValidator()
        
        assert len(validator.rules) > 0
        
        # Check that we have rules of different types
        rule_types = {rule.rule_type for rule in validator.rules}
        assert len(rule_types) > 1
    
    def test_valid_ontology_validation(self):
        """Test validation of a valid ontology"""
        builder = OntologyBuilder()
        ontology = builder.create_linac_ontology("test_valid")
        
        validator = OntologyValidator()
        result = validator.validate_ontology(ontology)
        
        assert "validation_timestamp" in result
        assert "is_valid" in result
        assert "validation_score" in result
        assert "total_issues" in result
        assert "issues_by_severity" in result
        assert "issues" in result
        
        # Should have minimal issues for a properly constructed ontology
        assert result["issues_by_severity"]["errors"] == 0
    
    def test_invalid_ontology_validation(self):
        """Test validation of an invalid ontology"""
        # Create an ontology with issues
        ontology = OWLOntology("invalid_test", "Invalid Test", "Test ontology with issues")
        
        # Add a subsystem without a parent system
        subsystem = create_subsystem(
            "Orphan Subsystem", 
            SubsystemType.BEAM_DELIVERY, 
            "nonexistent_parent"
        )
        ontology.add_subsystem(subsystem)
        
        validator = OntologyValidator()
        result = validator.validate_ontology(ontology)
        
        assert result["is_valid"] is False
        assert result["issues_by_severity"]["errors"] > 0
        assert result["validation_score"] < 100
    
    def test_validation_rule_filtering(self):
        """Test validation with rule filtering"""
        builder = OntologyBuilder()
        ontology = builder.create_linac_ontology("test_filtering")
        
        validator = OntologyValidator()
        
        # Test filtering by rule type
        from verification.ontology_validator import ValidationRuleType
        result = validator.validate_ontology(
            ontology, 
            rule_types=[ValidationRuleType.STRUCTURAL]
        )
        
        assert "validation_timestamp" in result
        assert result["rules_executed"] > 0
        
        # Test filtering by severity
        result = validator.validate_ontology(
            ontology,
            severity_filter=ValidationSeverity.ERROR
        )
        
        assert result["rules_executed"] > 0
    
    def test_linac_specific_validation(self):
        """Test LINAC-specific validation rules"""
        builder = OntologyBuilder()
        ontology = builder.create_linac_ontology("test_linac_validation")
        
        validator = OntologyValidator()
        result = validator.validate_ontology(ontology)
        
        # Should pass LINAC-specific validations since we created a proper LINAC ontology
        linac_issues = [
            issue for issue in result["issues"] 
            if issue["rule_id"].startswith("DOM001")
        ]
        
        # Should have minimal LINAC-specific issues
        assert len(linac_issues) <= 2  # Allow for minor completeness warnings


class TestIntegration:
    """Integration tests for the complete ontology foundation"""
    
    def test_end_to_end_ontology_creation(self):
        """Test complete ontology creation and validation workflow"""
        # Step 1: Create ontology
        builder = OntologyBuilder()
        ontology = builder.create_linac_ontology("integration_test")
        
        # Step 2: Add custom components
        beam_delivery = None
        for subsystem in ontology.subsystems:
            if subsystem.subsystem_type == SubsystemType.BEAM_DELIVERY:
                beam_delivery = subsystem
                break
        
        assert beam_delivery is not None
        
        # Add MLC component
        mlc = create_component(
            "Multi-Leaf Collimator",
            "Collimator",
            beam_delivery.id,
            "MLC-120",
            "Varian",
            "120-leaf multi-leaf collimator"
        )
        ontology.add_component(mlc)
        
        # Add spare part
        leaf_motor = create_spare_part(
            "Leaf Drive Motor",
            mlc.id,
            "LDM-001",
            "Varian",
            "Varian Medical",
            "Motor for leaf positioning"
        )
        ontology.add_spare_part(leaf_motor)
        
        # Add relationships
        subsystem_component_rel = create_ontology_relationship(
            RelationshipType.HAS_COMPONENT,
            beam_delivery.id,
            mlc.id,
            "Beam delivery subsystem contains MLC"
        )
        ontology.add_relationship(subsystem_component_rel)
        
        component_part_rel = create_ontology_relationship(
            RelationshipType.HAS_SPARE_PART,
            mlc.id,
            leaf_motor.id,
            "MLC has leaf drive motor as spare part"
        )
        ontology.add_relationship(component_part_rel)
        
        # Step 3: Validate ontology
        validator = OntologyValidator()
        validation_result = validator.validate_ontology(ontology)
        
        assert validation_result["is_valid"] is True
        assert validation_result["issues_by_severity"]["errors"] == 0
        
        # Step 4: Check statistics
        stats = ontology.get_statistics()
        assert stats["entity_counts"]["components"] >= 1
        assert stats["entity_counts"]["spare_parts"] >= 1
        assert stats["total_relationships"] >= 2
        
        # Step 5: Export to JSON-LD
        json_ld = ontology.to_json_ld()
        assert len(json_ld["@graph"]) > 10  # Should have many entities
        
        # Step 6: Verify specific entities in export
        entity_labels = [entity.get("rdfs:label", "") for entity in json_ld["@graph"]]
        assert "Multi-Leaf Collimator" in entity_labels
        assert "Leaf Drive Motor" in entity_labels
    
    def test_ontology_consistency_after_modifications(self):
        """Test that ontology remains consistent after modifications"""
        builder = OntologyBuilder()
        ontology = builder.create_linac_ontology("consistency_test")
        
        # Initial validation
        validator = OntologyValidator()
        initial_result = validator.validate_ontology(ontology)
        assert initial_result["is_valid"] is True
        
        # Add entities and relationships
        system = ontology.systems[0]
        
        # Add new subsystem
        new_subsystem = create_subsystem(
            "Custom Subsystem",
            SubsystemType.MECHANICAL,
            system.id,
            "Custom mechanical subsystem"
        )
        ontology.add_subsystem(new_subsystem)
        
        # Add relationship
        new_relationship = create_ontology_relationship(
            RelationshipType.HAS_SUBSYSTEM,
            system.id,
            new_subsystem.id,
            "System has custom subsystem"
        )
        ontology.add_relationship(new_relationship)
        
        # Validate after modifications
        modified_result = validator.validate_ontology(ontology)
        assert modified_result["is_valid"] is True
        assert modified_result["issues_by_severity"]["errors"] == 0
        
        # Check that statistics updated correctly
        stats = ontology.get_statistics()
        assert stats["entity_counts"]["subsystems"] > initial_result["ontology_statistics"]["entity_counts"]["subsystems"]


def run_all_tests():
    """Run all tests and report results"""
    test_classes = [
        TestOntologyModels,
        TestHierarchyValidation,
        TestOntologyBuilder,
        TestOntologyValidator,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n{'='*60}")
        print(f"Running {test_class.__name__}")
        print(f"{'='*60}")
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                print(f"  Running {test_method}...", end=" ")
                getattr(test_instance, test_method)()
                print("✅ PASSED")
                passed_tests += 1
            except Exception as e:
                print(f"❌ FAILED: {e}")
                failed_tests.append(f"{test_class.__name__}.{test_method}: {e}")
    
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print(f"\nFAILED TESTS:")
        for failure in failed_tests:
            print(f"  ❌ {failure}")
    
    return len(failed_tests) == 0


if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n🎉 All tests passed! Ontology foundation is working correctly.")
    else:
        print("\n💥 Some tests failed. Please review the failures above.")
    
    exit(0 if success else 1)