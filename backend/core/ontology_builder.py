"""
OWL Ontology Builder for Medical Device Troubleshooting System
Constructs and manages OWL ontologies from extracted entities and relationships
"""

import json
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import asdict
import logging

from ..models.ontology_models import (
    MechatronicSystem, Subsystem, Component, SparePart,
    OntologyRelationship, RelationshipType, SystemType, SubsystemType,
    ValidationStatus, OntologyMetadata, TechnicalSpecification,
    validate_hierarchy_consistency, validate_relationship_consistency,
    get_ontology_statistics
)
from ..models.entity import Entity, Relationship


logger = logging.getLogger(__name__)


class OWLOntology:
    """OWL Ontology representation with JSON-LD serialization"""
    
    def __init__(self, ontology_id: str, label: str, description: str = ""):
        self.ontology_id = ontology_id
        self.label = label
        self.description = description
        self.created_timestamp = datetime.now()
        self.version = "1.0"
        
        # Ontology entities
        self.systems: List[MechatronicSystem] = []
        self.subsystems: List[Subsystem] = []
        self.components: List[Component] = []
        self.spare_parts: List[SparePart] = []
        self.relationships: List[OntologyRelationship] = []
        
        # Namespaces
        self.namespaces = {
            "@context": {
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "mdo": "http://medical-device-ontology.org/",
                "linac": "http://medical-device-ontology.org/linac#"
            }
        }
    
    def add_system(self, system: MechatronicSystem) -> None:
        """Add a mechatronic system to the ontology"""
        self.systems.append(system)
        logger.info(f"Added system: {system.label} ({system.id})")
    
    def add_subsystem(self, subsystem: Subsystem) -> None:
        """Add a subsystem to the ontology"""
        self.subsystems.append(subsystem)
        logger.info(f"Added subsystem: {subsystem.label} ({subsystem.id})")
    
    def add_component(self, component: Component) -> None:
        """Add a component to the ontology"""
        self.components.append(component)
        logger.info(f"Added component: {component.label} ({component.id})")
    
    def add_spare_part(self, spare_part: SparePart) -> None:
        """Add a spare part to the ontology"""
        self.spare_parts.append(spare_part)
        logger.info(f"Added spare part: {spare_part.label} ({spare_part.id})")
    
    def add_relationship(self, relationship: OntologyRelationship) -> None:
        """Add a relationship to the ontology"""
        self.relationships.append(relationship)
        logger.info(f"Added relationship: {relationship.relationship_type.value}")
    
    def get_all_entity_ids(self) -> Set[str]:
        """Get all entity IDs in the ontology"""
        ids = set()
        ids.update(system.id for system in self.systems)
        ids.update(subsystem.id for subsystem in self.subsystems)
        ids.update(component.id for component in self.components)
        ids.update(spare_part.id for spare_part in self.spare_parts)
        return ids
    
    def validate_consistency(self) -> Dict[str, List[str]]:
        """Validate ontology consistency and return errors"""
        errors = {
            "hierarchy_errors": [],
            "relationship_errors": [],
            "general_errors": []
        }
        
        # Validate hierarchy consistency
        hierarchy_errors = validate_hierarchy_consistency(
            self.systems, self.subsystems, self.components, self.spare_parts
        )
        errors["hierarchy_errors"] = hierarchy_errors
        
        # Validate relationship consistency
        all_entity_ids = self.get_all_entity_ids()
        relationship_errors = validate_relationship_consistency(
            self.relationships, all_entity_ids
        )
        errors["relationship_errors"] = relationship_errors
        
        # Additional validation rules
        if not self.systems:
            errors["general_errors"].append("Ontology must contain at least one system")
        
        return errors
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get ontology statistics"""
        return get_ontology_statistics(
            self.systems, self.subsystems, self.components, 
            self.spare_parts, self.relationships
        )
    
    def to_json_ld(self) -> Dict[str, Any]:
        """Export ontology as JSON-LD"""
        json_ld = {
            **self.namespaces,
            "@type": "owl:Ontology",
            "@id": f"http://medical-device-ontology.org/{self.ontology_id}",
            "rdfs:label": self.label,
            "rdfs:comment": self.description,
            "owl:versionInfo": self.version,
            "created": self.created_timestamp.isoformat(),
            "@graph": []
        }
        
        # Add all entities to the graph
        for system in self.systems:
            json_ld["@graph"].append(system.to_owl_dict())
        
        for subsystem in self.subsystems:
            json_ld["@graph"].append(subsystem.to_owl_dict())
        
        for component in self.components:
            json_ld["@graph"].append(component.to_owl_dict())
        
        for spare_part in self.spare_parts:
            json_ld["@graph"].append(spare_part.to_owl_dict())
        
        # Add relationships as object properties
        for relationship in self.relationships:
            json_ld["@graph"].append(relationship.to_owl_dict())
        
        return json_ld
    
    def export_to_file(self, file_path: str, format: str = "json-ld") -> None:
        """Export ontology to file"""
        if format == "json-ld":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_json_ld(), f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"Exported ontology to {file_path} in {format} format")


class OntologyBuilder:
    """Builder class for constructing medical device ontologies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_linac_ontology(
        self, 
        ontology_id: str,
        label: str = "LINAC Troubleshooting Ontology",
        description: str = "Ontology for LINAC medical device troubleshooting"
    ) -> OWLOntology:
        """Create a new LINAC ontology with basic structure"""
        
        ontology = OWLOntology(ontology_id, label, description)
        
        # Create basic LINAC system structure
        linac_system = MechatronicSystem(
            label="LINAC System",
            description="Linear Accelerator System for Radiation Therapy",
            system_type=SystemType.LINAC
        )
        ontology.add_system(linac_system)
        
        # Create standard LINAC subsystems
        subsystem_configs = [
            ("Beam Delivery System", SubsystemType.BEAM_DELIVERY, 
             "System responsible for generating and delivering therapeutic radiation beam"),
            ("Patient Positioning System", SubsystemType.PATIENT_POSITIONING,
             "System for precise patient positioning and immobilization"),
            ("Imaging System", SubsystemType.IMAGING,
             "On-board imaging system for patient setup verification"),
            ("Treatment Control System", SubsystemType.TREATMENT_CONTROL,
             "Central control system for treatment planning and execution"),
            ("Safety Interlock System", SubsystemType.SAFETY_INTERLOCK,
             "Safety systems and interlocks for radiation protection"),
            ("Cooling System", SubsystemType.COOLING,
             "Cooling systems for heat management"),
            ("Power Supply System", SubsystemType.POWER_SUPPLY,
             "Electrical power distribution and conditioning")
        ]
        
        for label, subsystem_type, description in subsystem_configs:
            subsystem = Subsystem(
                label=label,
                description=description,
                subsystem_type=subsystem_type,
                parent_system_id=linac_system.id
            )
            ontology.add_subsystem(subsystem)
            
            # Add relationship
            relationship = OntologyRelationship(
                relationship_type=RelationshipType.HAS_SUBSYSTEM,
                source_entity_id=linac_system.id,
                target_entity_id=subsystem.id,
                description=f"LINAC system contains {label.lower()}"
            )
            ontology.add_relationship(relationship)
        
        self.logger.info(f"Created LINAC ontology with {len(ontology.subsystems)} subsystems")
        return ontology
    
    def add_entities_from_extraction(
        self, 
        ontology: OWLOntology,
        extracted_entities: List[Entity],
        extracted_relationships: List[Relationship]
    ) -> None:
        """Add entities from AI extraction to ontology"""
        
        entity_mapping = {}  # Map old entity IDs to new ontology entity IDs
        
        for entity in extracted_entities:
            ontology_entity = self._convert_entity_to_ontology(entity, ontology)
            if ontology_entity:
                entity_mapping[entity.id] = ontology_entity.id
        
        # Convert relationships
        for relationship in extracted_relationships:
            if (relationship.source_entity_id in entity_mapping and 
                relationship.target_entity_id in entity_mapping):
                
                ontology_rel = self._convert_relationship_to_ontology(
                    relationship, entity_mapping
                )
                if ontology_rel:
                    ontology.add_relationship(ontology_rel)
        
        self.logger.info(f"Added {len(extracted_entities)} entities and {len(extracted_relationships)} relationships")
    
    def _convert_entity_to_ontology(
        self, 
        entity: Entity, 
        ontology: OWLOntology
    ) -> Optional[Any]:
        """Convert extracted entity to ontology entity"""
        
        # Create metadata from entity
        metadata = OntologyMetadata(
            source_page=entity.source_page,
            extraction_method="ai_extraction",
            confidence_score=entity.confidence,
            validation_status=ValidationStatus.PENDING_REVIEW if entity.reviewed else ValidationStatus.NOT_VALIDATED
        )
        
        # Determine entity type and create appropriate ontology entity
        if hasattr(entity, 'component_type') and entity.entity_type.value == 'component':
            # This is a component
            component = Component(
                label=getattr(entity, 'name', 'Unknown Component'),
                description=getattr(entity, 'function', ''),
                component_type=getattr(entity, 'component_type', '').value if hasattr(getattr(entity, 'component_type', ''), 'value') else str(getattr(entity, 'component_type', '')),
                part_number=getattr(entity, 'part_number', ''),
                manufacturer=getattr(entity, 'manufacturer', ''),
                metadata=metadata
            )
            
            # Try to find appropriate subsystem
            parent_subsystem = self._find_or_create_subsystem(
                getattr(entity, 'parent_system', 'Unknown'), ontology
            )
            if parent_subsystem:
                component.parent_subsystem_id = parent_subsystem.id
            
            ontology.add_component(component)
            return component
        
        return None
    
    def _find_or_create_subsystem(
        self, 
        system_name: str, 
        ontology: OWLOntology
    ) -> Optional[Subsystem]:
        """Find existing subsystem or create new one"""
        
        # Try to match with existing subsystems
        for subsystem in ontology.subsystems:
            if system_name.lower() in subsystem.label.lower():
                return subsystem
        
        # Create new generic subsystem if no match found
        if system_name and system_name != 'Unknown':
            # Find a system to attach to
            if ontology.systems:
                parent_system = ontology.systems[0]  # Use first system
                
                subsystem = Subsystem(
                    label=system_name,
                    description=f"Subsystem for {system_name}",
                    subsystem_type=SubsystemType.MECHANICAL,  # Default type
                    parent_system_id=parent_system.id
                )
                ontology.add_subsystem(subsystem)
                
                # Add relationship
                relationship = OntologyRelationship(
                    relationship_type=RelationshipType.HAS_SUBSYSTEM,
                    source_entity_id=parent_system.id,
                    target_entity_id=subsystem.id,
                    description=f"System contains {system_name}"
                )
                ontology.add_relationship(relationship)
                
                return subsystem
        
        return None
    
    def _convert_relationship_to_ontology(
        self, 
        relationship: Relationship,
        entity_mapping: Dict[str, str]
    ) -> Optional[OntologyRelationship]:
        """Convert extracted relationship to ontology relationship"""
        
        # Map relationship types
        relationship_type_mapping = {
            "causes": RelationshipType.CAUSES,
            "part_of": RelationshipType.PART_OF,
            "requires": RelationshipType.REQUIRES,
            "controls": RelationshipType.CONTROLS,
            "monitors": RelationshipType.MONITORS,
            "affects": RelationshipType.AFFECTS,
            "connected_to": RelationshipType.CONNECTED_TO
        }
        
        ontology_rel_type = relationship_type_mapping.get(
            relationship.relationship_type.lower(),
            RelationshipType.AFFECTS  # Default
        )
        
        metadata = OntologyMetadata(
            extraction_method="ai_extraction",
            confidence_score=relationship.confidence,
            validation_status=ValidationStatus.PENDING_REVIEW if relationship.reviewed else ValidationStatus.NOT_VALIDATED
        )
        
        return OntologyRelationship(
            relationship_type=ontology_rel_type,
            source_entity_id=entity_mapping[relationship.source_entity_id],
            target_entity_id=entity_mapping[relationship.target_entity_id],
            description=relationship.description,
            metadata=metadata
        )
    
    def add_subsystem_hierarchy(
        self, 
        ontology: OWLOntology,
        subsystem_data: List[Dict[str, Any]]
    ) -> None:
        """Add subsystem hierarchy from structured data"""
        
        for subsystem_info in subsystem_data:
            # Find parent system
            parent_system = None
            for system in ontology.systems:
                if system.id == subsystem_info.get('parent_system_id'):
                    parent_system = system
                    break
            
            if not parent_system and ontology.systems:
                parent_system = ontology.systems[0]  # Use first system as default
            
            if parent_system:
                subsystem = Subsystem(
                    label=subsystem_info['label'],
                    description=subsystem_info.get('description', ''),
                    subsystem_type=SubsystemType(subsystem_info.get('type', 'mechanical')),
                    parent_system_id=parent_system.id
                )
                ontology.add_subsystem(subsystem)
                
                # Add relationship
                relationship = OntologyRelationship(
                    relationship_type=RelationshipType.HAS_SUBSYSTEM,
                    source_entity_id=parent_system.id,
                    target_entity_id=subsystem.id,
                    description=f"System contains {subsystem.label}"
                )
                ontology.add_relationship(relationship)
    
    def validate_ontology_consistency(self, ontology: OWLOntology) -> Dict[str, Any]:
        """Validate ontology consistency and return detailed results"""
        
        validation_result = {
            "is_valid": True,
            "errors": ontology.validate_consistency(),
            "warnings": [],
            "statistics": ontology.get_statistics(),
            "validation_timestamp": datetime.now().isoformat()
        }
        
        # Check if there are any errors
        total_errors = sum(len(error_list) for error_list in validation_result["errors"].values())
        validation_result["is_valid"] = total_errors == 0
        
        # Add warnings for potential issues
        stats = validation_result["statistics"]
        if stats["entity_counts"]["systems"] == 0:
            validation_result["warnings"].append("No systems defined in ontology")
        
        if stats["entity_counts"]["subsystems"] == 0:
            validation_result["warnings"].append("No subsystems defined in ontology")
        
        if stats["total_relationships"] == 0:
            validation_result["warnings"].append("No relationships defined in ontology")
        
        # Check validation status distribution
        validation_counts = stats["validation_status"]
        pending_count = validation_counts.get("pending_review", 0)
        not_validated_count = validation_counts.get("not_validated", 0)
        
        if pending_count > 0:
            validation_result["warnings"].append(f"{pending_count} entities pending expert review")
        
        if not_validated_count > 0:
            validation_result["warnings"].append(f"{not_validated_count} entities not yet validated")
        
        return validation_result


# Utility functions for ontology management

def merge_ontologies(ontology1: OWLOntology, ontology2: OWLOntology) -> OWLOntology:
    """Merge two ontologies into a single ontology"""
    
    merged = OWLOntology(
        f"{ontology1.ontology_id}_merged_{ontology2.ontology_id}",
        f"Merged: {ontology1.label} + {ontology2.label}",
        f"Merged ontology from {ontology1.label} and {ontology2.label}"
    )
    
    # Add all entities from both ontologies
    merged.systems.extend(ontology1.systems)
    merged.systems.extend(ontology2.systems)
    
    merged.subsystems.extend(ontology1.subsystems)
    merged.subsystems.extend(ontology2.subsystems)
    
    merged.components.extend(ontology1.components)
    merged.components.extend(ontology2.components)
    
    merged.spare_parts.extend(ontology1.spare_parts)
    merged.spare_parts.extend(ontology2.spare_parts)
    
    merged.relationships.extend(ontology1.relationships)
    merged.relationships.extend(ontology2.relationships)
    
    return merged


def create_ontology_diff(ontology1: OWLOntology, ontology2: OWLOntology) -> Dict[str, Any]:
    """Create a diff between two ontologies"""
    
    # Get entity IDs from both ontologies
    ids1 = ontology1.get_all_entity_ids()
    ids2 = ontology2.get_all_entity_ids()
    
    diff = {
        "added_entities": list(ids2 - ids1),
        "removed_entities": list(ids1 - ids2),
        "common_entities": list(ids1 & ids2),
        "statistics_diff": {
            "ontology1": ontology1.get_statistics(),
            "ontology2": ontology2.get_statistics()
        }
    }
    
    return diff


if __name__ == "__main__":
    # Test the ontology builder
    
    builder = OntologyBuilder()
    
    # Create a LINAC ontology
    ontology = builder.create_linac_ontology("test_linac_001")
    
    # Validate consistency
    validation_result = builder.validate_ontology_consistency(ontology)
    print(f"Ontology validation: {'✅ Valid' if validation_result['is_valid'] else '❌ Invalid'}")
    print(f"Errors: {sum(len(errors) for errors in validation_result['errors'].values())}")
    print(f"Warnings: {len(validation_result['warnings'])}")
    
    # Get statistics
    stats = ontology.get_statistics()
    print(f"Statistics: {stats}")
    
    # Test export
    json_ld = ontology.to_json_ld()
    print(f"JSON-LD export successful: {len(json_ld['@graph'])} entities")
    
    print("✅ Ontology builder test completed successfully!")