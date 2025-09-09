"""
OWL Ontology data models for the troubleshooting ontology system
Extends existing entity models with hierarchical structure and OWL support
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Union
from enum import Enum
import uuid
from datetime import datetime
from abc import ABC, abstractmethod

# Import existing models
from .entity import Entity, EntityType, Relationship


class OntologyEntityType(Enum):
    """Extended entity types for ontology hierarchy"""
    MECHATRONIC_SYSTEM = "mechatronic_system"
    SUBSYSTEM = "subsystem"
    COMPONENT = "component"
    SPARE_PART = "spare_part"
    FUNCTION = "function"
    CONTROL_UNIT = "control_unit"
    SENSOR = "sensor"
    CONTROLLER = "controller"


class SystemType(Enum):
    """Types of medical device systems"""
    LINAC = "linac"
    CT_SCANNER = "ct_scanner"
    MRI = "mri"
    ULTRASOUND = "ultrasound"
    XRAY = "xray"
    GENERIC = "generic"


class SubsystemType(Enum):
    """Types of subsystems for LINAC and other medical devices"""
    # LINAC Subsystems
    BEAM_DELIVERY = "beam_delivery"
    PATIENT_POSITIONING = "patient_positioning"
    IMAGING = "imaging"
    TREATMENT_CONTROL = "treatment_control"
    SAFETY_INTERLOCK = "safety_interlock"
    COOLING = "cooling"
    POWER_SUPPLY = "power_supply"
    
    # Generic Subsystems
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    SOFTWARE = "software"
    HYDRAULIC = "hydraulic"
    PNEUMATIC = "pneumatic"


class RelationshipType(Enum):
    """Types of relationships in the ontology"""
    # Hierarchical relationships
    HAS_SUBSYSTEM = "has_subsystem"
    HAS_COMPONENT = "has_component"
    HAS_SPARE_PART = "has_spare_part"
    PART_OF = "part_of"
    
    # Functional relationships
    CONTROLS = "controls"
    CONTROLLED_BY = "controlled_by"
    MONITORS = "monitors"
    MONITORED_BY = "monitored_by"
    REQUIRES = "requires"
    PROVIDES = "provides"
    
    # Causal relationships
    CAUSES = "causes"
    CAUSED_BY = "caused_by"
    AFFECTS = "affects"
    AFFECTED_BY = "affected_by"
    
    # Spatial relationships
    CONNECTED_TO = "connected_to"
    ADJACENT_TO = "adjacent_to"
    CONTAINS = "contains"
    CONTAINED_IN = "contained_in"
    
    # Temporal relationships
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    CONCURRENT_WITH = "concurrent_with"


class ValidationStatus(Enum):
    """Validation status for ontology elements"""
    NOT_VALIDATED = "not_validated"
    PENDING_REVIEW = "pending_review"
    EXPERT_APPROVED = "expert_approved"
    EXPERT_REJECTED = "expert_rejected"
    NEEDS_REVISION = "needs_revision"
    CONFLICTING_REVIEWS = "conflicting_reviews"


@dataclass
class OntologyMetadata:
    """Metadata for ontology elements"""
    created_timestamp: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    extraction_method: str = "manual"  # manual, ai_extraction, schematic_analysis
    confidence_score: float = 1.0
    validation_status: ValidationStatus = ValidationStatus.NOT_VALIDATED
    expert_reviews: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)


@dataclass
class TechnicalSpecification:
    """Technical specification for components"""
    parameter_name: str
    value: Union[str, float, int]
    unit: Optional[str] = None
    tolerance: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    measurement_method: Optional[str] = None
    compliance_standard: Optional[str] = None


@dataclass
class OWLClass(ABC):
    """Base class for OWL ontology classes"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    uri: str = ""
    label: str = ""
    description: str = ""
    image_url: Optional[str] = None  # URL or path to entity image
    metadata: OntologyMetadata = field(default_factory=OntologyMetadata)
    
    def __post_init__(self):
        if not self.uri:
            self.uri = f"http://medical-device-ontology.org/{self.__class__.__name__}#{self.id}"
    
    @abstractmethod
    def to_owl_dict(self) -> Dict[str, Any]:
        """Convert to OWL representation"""
        pass
    
    def get_namespace(self) -> str:
        """Get the namespace for this class"""
        return "http://medical-device-ontology.org/"


@dataclass
class MechatronicSystem(OWLClass):
    """Top-level medical device system (e.g., LINAC_001)"""
    system_type: SystemType = SystemType.GENERIC
    model_number: str = ""
    manufacturer: str = ""
    serial_number: str = ""
    installation_date: Optional[datetime] = None
    software_version: str = ""
    hardware_version: str = ""
    
    # Relationships
    subsystems: List[str] = field(default_factory=list)  # IDs of subsystems
    functions: List[str] = field(default_factory=list)   # System functions
    applications: List[str] = field(default_factory=list)  # Medical applications
    
    # Technical specifications
    specifications: Dict[str, TechnicalSpecification] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization"""
        return {
            "id": self.id,
            "uri": self.uri,
            "label": self.label,
            "description": self.description,
            "image_url": self.image_url,
            "system_type": self.system_type.value,
            "model_number": self.model_number,
            "manufacturer": self.manufacturer,
            "serial_number": self.serial_number,
            "installation_date": self.installation_date.isoformat() if self.installation_date else None,
            "software_version": self.software_version,
            "hardware_version": self.hardware_version,
            "subsystems": self.subsystems,
            "functions": self.functions,
            "applications": self.applications,
            "specifications": {k: {
                "parameter_name": v.parameter_name,
                "value": v.value,
                "unit": v.unit,
                "tolerance": v.tolerance,
                "min_value": v.min_value,
                "max_value": v.max_value,
                "measurement_method": v.measurement_method,
                "compliance_standard": v.compliance_standard
            } for k, v in self.specifications.items()},
            "metadata": {
                "created_timestamp": self.metadata.created_timestamp.isoformat(),
                "last_modified": self.metadata.last_modified.isoformat(),
                "version": self.metadata.version,
                "source_document": self.metadata.source_document,
                "source_page": self.metadata.source_page,
                "extraction_method": self.metadata.extraction_method,
                "confidence_score": self.metadata.confidence_score,
                "validation_status": self.metadata.validation_status.value,
                "expert_reviews": self.metadata.expert_reviews,
                "tags": list(self.metadata.tags)
            }
        }
    
    def to_owl_dict(self) -> Dict[str, Any]:
        """Convert to OWL representation"""
        return {
            "@type": "MechatronicSystem",
            "@id": self.uri,
            "rdfs:label": self.label,
            "rdfs:comment": self.description,
            "systemType": self.system_type.value,
            "modelNumber": self.model_number,
            "manufacturer": self.manufacturer,
            "serialNumber": self.serial_number,
            "softwareVersion": self.software_version,
            "hardwareVersion": self.hardware_version,
            "hasSubsystem": [{"@id": f"#{subsystem_id}"} for subsystem_id in self.subsystems],
            "hasFunction": [{"@id": f"#{func_id}"} for func_id in self.functions],
            "usedFor": [{"@id": f"#{app_id}"} for app_id in self.applications]
        }


@dataclass
class Subsystem(OWLClass):
    """Functional subsystem (e.g., BeamDeliverySystem)"""
    subsystem_type: SubsystemType = SubsystemType.MECHANICAL
    parent_system_id: str = ""
    
    # Relationships
    components: List[str] = field(default_factory=list)  # Component IDs
    control_units: List[str] = field(default_factory=list)  # Control unit IDs
    functions: List[str] = field(default_factory=list)  # Subsystem functions
    
    # Technical specifications
    specifications: Dict[str, TechnicalSpecification] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization"""
        return {
            "id": self.id,
            "uri": self.uri,
            "label": self.label,
            "description": self.description,
            "image_url": self.image_url,
            "subsystem_type": self.subsystem_type.value,
            "parent_system_id": self.parent_system_id,
            "components": self.components,
            "control_units": self.control_units,
            "functions": self.functions,
            "specifications": {k: {
                "parameter_name": v.parameter_name,
                "value": v.value,
                "unit": v.unit,
                "tolerance": v.tolerance,
                "min_value": v.min_value,
                "max_value": v.max_value,
                "measurement_method": v.measurement_method,
                "compliance_standard": v.compliance_standard
            } for k, v in self.specifications.items()},
            "metadata": {
                "created_timestamp": self.metadata.created_timestamp.isoformat(),
                "last_modified": self.metadata.last_modified.isoformat(),
                "version": self.metadata.version,
                "source_document": self.metadata.source_document,
                "source_page": self.metadata.source_page,
                "extraction_method": self.metadata.extraction_method,
                "confidence_score": self.metadata.confidence_score,
                "validation_status": self.metadata.validation_status.value,
                "expert_reviews": self.metadata.expert_reviews,
                "tags": list(self.metadata.tags)
            }
        }
    
    def to_owl_dict(self) -> Dict[str, Any]:
        """Convert to OWL representation"""
        return {
            "@type": "Subsystem",
            "@id": self.uri,
            "rdfs:label": self.label,
            "rdfs:comment": self.description,
            "subsystemType": self.subsystem_type.value,
            "partOfSystem": {"@id": f"#{self.parent_system_id}"},
            "hasComponent": [{"@id": f"#{comp_id}"} for comp_id in self.components],
            "hasControlUnit": [{"@id": f"#{ctrl_id}"} for ctrl_id in self.control_units],
            "hasFunction": [{"@id": f"#{func_id}"} for func_id in self.functions]
        }


@dataclass
class Component(OWLClass):
    """Individual component (e.g., MLC, ServoMotor)"""
    component_type: str = ""  # More flexible than enum for diverse components
    parent_subsystem_id: str = ""
    part_number: str = ""
    manufacturer: str = ""
    model: str = ""
    
    # Relationships
    spare_parts: List[str] = field(default_factory=list)  # Spare part IDs
    sensors: List[str] = field(default_factory=list)      # Monitoring sensors
    controllers: List[str] = field(default_factory=list)  # Control units
    
    # Technical specifications
    specifications: Dict[str, TechnicalSpecification] = field(default_factory=dict)
    
    # Operational data
    lifecycle_status: str = "active"  # active, deprecated, obsolete
    maintenance_schedule: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization"""
        return {
            "id": self.id,
            "uri": self.uri,
            "label": self.label,
            "description": self.description,
            "image_url": self.image_url,
            "component_type": self.component_type,
            "parent_subsystem_id": self.parent_subsystem_id,
            "part_number": self.part_number,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "spare_parts": self.spare_parts,
            "sensors": self.sensors,
            "controllers": self.controllers,
            "specifications": {k: {
                "parameter_name": v.parameter_name,
                "value": v.value,
                "unit": v.unit,
                "tolerance": v.tolerance,
                "min_value": v.min_value,
                "max_value": v.max_value,
                "measurement_method": v.measurement_method,
                "compliance_standard": v.compliance_standard
            } for k, v in self.specifications.items()},
            "lifecycle_status": self.lifecycle_status,
            "maintenance_schedule": self.maintenance_schedule,
            "metadata": {
                "created_timestamp": self.metadata.created_timestamp.isoformat(),
                "last_modified": self.metadata.last_modified.isoformat(),
                "version": self.metadata.version,
                "source_document": self.metadata.source_document,
                "source_page": self.metadata.source_page,
                "extraction_method": self.metadata.extraction_method,
                "confidence_score": self.metadata.confidence_score,
                "validation_status": self.metadata.validation_status.value,
                "expert_reviews": self.metadata.expert_reviews,
                "tags": list(self.metadata.tags)
            }
        }
    
    def to_owl_dict(self) -> Dict[str, Any]:
        """Convert to OWL representation"""
        return {
            "@type": "Component",
            "@id": self.uri,
            "rdfs:label": self.label,
            "rdfs:comment": self.description,
            "componentType": self.component_type,
            "partOfSubsystem": {"@id": f"#{self.parent_subsystem_id}"},
            "partNumber": self.part_number,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "hasSparePart": [{"@id": f"#{part_id}"} for part_id in self.spare_parts],
            "monitoredBy": [{"@id": f"#{sensor_id}"} for sensor_id in self.sensors],
            "controlledBy": [{"@id": f"#{ctrl_id}"} for ctrl_id in self.controllers],
            "lifecycleStatus": self.lifecycle_status
        }


@dataclass
class SparePart(OWLClass):
    """Replaceable parts and consumables"""
    parent_component_id: str = ""
    part_number: str = ""
    manufacturer: str = ""
    supplier: str = ""
    
    # Lifecycle information
    maintenance_cycle: Optional[str] = None  # e.g., "6 months", "1000 hours"
    replacement_frequency: Optional[str] = None
    lifecycle_status: str = "available"  # available, discontinued, obsolete
    
    # Inventory information
    stock_level: Optional[int] = None
    reorder_point: Optional[int] = None
    lead_time: Optional[str] = None
    
    # Technical specifications
    specifications: Dict[str, TechnicalSpecification] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization"""
        return {
            "id": self.id,
            "uri": self.uri,
            "label": self.label,
            "description": self.description,
            "image_url": self.image_url,
            "parent_component_id": self.parent_component_id,
            "part_number": self.part_number,
            "manufacturer": self.manufacturer,
            "supplier": self.supplier,
            "maintenance_cycle": self.maintenance_cycle,
            "replacement_frequency": self.replacement_frequency,
            "lifecycle_status": self.lifecycle_status,
            "stock_level": self.stock_level,
            "reorder_point": self.reorder_point,
            "lead_time": self.lead_time,
            "specifications": {k: {
                "parameter_name": v.parameter_name,
                "value": v.value,
                "unit": v.unit,
                "tolerance": v.tolerance,
                "min_value": v.min_value,
                "max_value": v.max_value,
                "measurement_method": v.measurement_method,
                "compliance_standard": v.compliance_standard
            } for k, v in self.specifications.items()},
            "metadata": {
                "created_timestamp": self.metadata.created_timestamp.isoformat(),
                "last_modified": self.metadata.last_modified.isoformat(),
                "version": self.metadata.version,
                "source_document": self.metadata.source_document,
                "source_page": self.metadata.source_page,
                "extraction_method": self.metadata.extraction_method,
                "confidence_score": self.metadata.confidence_score,
                "validation_status": self.metadata.validation_status.value,
                "expert_reviews": self.metadata.expert_reviews,
                "tags": list(self.metadata.tags)
            }
        }
    
    def to_owl_dict(self) -> Dict[str, Any]:
        """Convert to OWL representation"""
        return {
            "@type": "SparePart",
            "@id": self.uri,
            "rdfs:label": self.label,
            "rdfs:comment": self.description,
            "usedByComponent": {"@id": f"#{self.parent_component_id}"},
            "partNumber": self.part_number,
            "manufacturer": self.manufacturer,
            "supplier": self.supplier,
            "maintenanceCycle": self.maintenance_cycle,
            "lifecycleStatus": self.lifecycle_status,
            "stockLevel": self.stock_level,
            "reorderPoint": self.reorder_point,
            "leadTime": self.lead_time
        }


@dataclass
class OntologyRelationship:
    """Enhanced relationship class for ontology"""
    relationship_type: RelationshipType
    source_entity_id: str
    target_entity_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Relationship properties
    label: str = ""
    description: str = ""
    inverse_relationship: Optional[RelationshipType] = None
    is_functional: bool = False  # True if relationship is functional (one-to-one)
    is_symmetric: bool = False   # True if relationship is symmetric
    is_transitive: bool = False  # True if relationship is transitive
    
    # Metadata
    metadata: OntologyMetadata = field(default_factory=OntologyMetadata)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization"""
        return {
            "id": self.id,
            "relationship_type": self.relationship_type.value,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "label": self.label,
            "description": self.description,
            "inverse_relationship": self.inverse_relationship.value if self.inverse_relationship else None,
            "is_functional": self.is_functional,
            "is_symmetric": self.is_symmetric,
            "is_transitive": self.is_transitive,
            "metadata": {
                "created_timestamp": self.metadata.created_timestamp.isoformat(),
                "last_modified": self.metadata.last_modified.isoformat(),
                "version": self.metadata.version,
                "source_document": self.metadata.source_document,
                "source_page": self.metadata.source_page,
                "extraction_method": self.metadata.extraction_method,
                "confidence_score": self.metadata.confidence_score,
                "validation_status": self.metadata.validation_status.value,
                "expert_reviews": self.metadata.expert_reviews,
                "tags": list(self.metadata.tags)
            }
        }
    
    def to_owl_dict(self) -> Dict[str, Any]:
        """Convert to OWL object property representation"""
        return {
            "@type": "ObjectProperty",
            "@id": f"#{self.relationship_type.value}",
            "rdfs:label": self.label or self.relationship_type.value.replace("_", " ").title(),
            "rdfs:comment": self.description,
            "rdfs:domain": {"@id": f"#{self.source_entity_id}"},
            "rdfs:range": {"@id": f"#{self.target_entity_id}"},
            "owl:inverseOf": {"@id": f"#{self.inverse_relationship.value}"} if self.inverse_relationship else None,
            "rdf:type": [
                {"@id": "owl:FunctionalProperty"} if self.is_functional else None,
                {"@id": "owl:SymmetricProperty"} if self.is_symmetric else None,
                {"@id": "owl:TransitiveProperty"} if self.is_transitive else None
            ]
        }


@dataclass
class OntologyValidationRule:
    """Validation rule for ontology consistency"""
    name: str
    description: str
    rule_type: str  # "cardinality", "domain_range", "consistency", "completeness"
    sparql_query: str  # SPARQL query to validate the rule
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    severity: str = "error"  # "error", "warning", "info"
    
    def validate(self, ontology_graph) -> List[Dict[str, Any]]:
        """Execute validation rule against ontology graph"""
        # This would be implemented with a SPARQL engine
        # For now, return empty list as placeholder
        return []


# Factory functions for creating ontology entities

def create_mechatronic_system(
    label: str,
    system_type: SystemType = SystemType.GENERIC,
    model_number: str = "",
    manufacturer: str = "",
    description: str = ""
) -> MechatronicSystem:
    """Factory function to create MechatronicSystem"""
    return MechatronicSystem(
        label=label,
        description=description,
        system_type=system_type,
        model_number=model_number,
        manufacturer=manufacturer
    )


def create_subsystem(
    label: str,
    subsystem_type: SubsystemType,
    parent_system_id: str,
    description: str = ""
) -> Subsystem:
    """Factory function to create Subsystem"""
    return Subsystem(
        label=label,
        description=description,
        subsystem_type=subsystem_type,
        parent_system_id=parent_system_id
    )


def create_component(
    label: str,
    component_type: str,
    parent_subsystem_id: str,
    part_number: str = "",
    manufacturer: str = "",
    description: str = ""
) -> Component:
    """Factory function to create Component"""
    return Component(
        label=label,
        description=description,
        component_type=component_type,
        parent_subsystem_id=parent_subsystem_id,
        part_number=part_number,
        manufacturer=manufacturer
    )


def create_spare_part(
    label: str,
    parent_component_id: str,
    part_number: str,
    manufacturer: str = "",
    supplier: str = "",
    description: str = ""
) -> SparePart:
    """Factory function to create SparePart"""
    return SparePart(
        label=label,
        description=description,
        parent_component_id=parent_component_id,
        part_number=part_number,
        manufacturer=manufacturer,
        supplier=supplier
    )


def create_ontology_relationship(
    relationship_type: RelationshipType,
    source_entity_id: str,
    target_entity_id: str,
    description: str = "",
    confidence: float = 1.0
) -> OntologyRelationship:
    """Factory function to create OntologyRelationship"""
    metadata = OntologyMetadata(confidence_score=confidence)
    
    return OntologyRelationship(
        relationship_type=relationship_type,
        source_entity_id=source_entity_id,
        target_entity_id=target_entity_id,
        description=description,
        metadata=metadata
    )


# Validation functions

def validate_hierarchy_consistency(
    systems: List[MechatronicSystem],
    subsystems: List[Subsystem],
    components: List[Component],
    spare_parts: List[SparePart]
) -> List[str]:
    """Validate the hierarchical consistency of the ontology"""
    errors = []
    
    # Create ID sets for efficient lookup
    system_ids = {sys.id for sys in systems}
    subsystem_ids = {sub.id for sub in subsystems}
    component_ids = {comp.id for comp in components}
    spare_part_ids = {part.id for part in spare_parts}
    
    # Validate subsystem references
    for subsystem in subsystems:
        if subsystem.parent_system_id and subsystem.parent_system_id not in system_ids:
            errors.append(f"Subsystem {subsystem.id} references non-existent system {subsystem.parent_system_id}")
    
    # Validate component references
    for component in components:
        if component.parent_subsystem_id and component.parent_subsystem_id not in subsystem_ids:
            errors.append(f"Component {component.id} references non-existent subsystem {component.parent_subsystem_id}")
    
    # Validate spare part references
    for spare_part in spare_parts:
        if spare_part.parent_component_id and spare_part.parent_component_id not in component_ids:
            errors.append(f"Spare part {spare_part.id} references non-existent component {spare_part.parent_component_id}")
    
    return errors


def validate_relationship_consistency(
    relationships: List[OntologyRelationship],
    all_entity_ids: Set[str]
) -> List[str]:
    """Validate relationship consistency"""
    errors = []
    
    for rel in relationships:
        # Check if source and target entities exist
        if rel.source_entity_id not in all_entity_ids:
            errors.append(f"Relationship {rel.id} references non-existent source entity {rel.source_entity_id}")
        
        if rel.target_entity_id not in all_entity_ids:
            errors.append(f"Relationship {rel.id} references non-existent target entity {rel.target_entity_id}")
        
        # Check for self-references (usually not allowed)
        if rel.source_entity_id == rel.target_entity_id:
            errors.append(f"Relationship {rel.id} has self-reference")
    
    return errors


# Utility functions

def get_ontology_statistics(
    systems: List[MechatronicSystem],
    subsystems: List[Subsystem],
    components: List[Component],
    spare_parts: List[SparePart],
    relationships: List[OntologyRelationship]
) -> Dict[str, Any]:
    """Get comprehensive statistics about the ontology"""
    
    total_entities = len(systems) + len(subsystems) + len(components) + len(spare_parts)
    
    # Count validation statuses
    all_entities = systems + subsystems + components + spare_parts
    validation_counts = {}
    for status in ValidationStatus:
        validation_counts[status.value] = sum(
            1 for entity in all_entities 
            if entity.metadata.validation_status == status
        )
    
    # Count relationship types
    relationship_counts = {}
    for rel_type in RelationshipType:
        relationship_counts[rel_type.value] = sum(
            1 for rel in relationships 
            if rel.relationship_type == rel_type
        )
    
    return {
        "total_entities": total_entities,
        "entity_counts": {
            "systems": len(systems),
            "subsystems": len(subsystems),
            "components": len(components),
            "spare_parts": len(spare_parts)
        },
        "total_relationships": len(relationships),
        "relationship_counts": relationship_counts,
        "validation_status": validation_counts,
        "average_confidence": sum(
            entity.metadata.confidence_score for entity in all_entities
        ) / total_entities if total_entities > 0 else 0.0
    }


if __name__ == "__main__":
    # Test the ontology models
    
    # Create a sample LINAC system hierarchy
    linac_system = create_mechatronic_system(
        label="LINAC_TrueBeam_001",
        system_type=SystemType.LINAC,
        model_number="TrueBeam STx",
        manufacturer="Varian Medical Systems",
        description="Linear Accelerator for radiation therapy"
    )
    
    beam_delivery = create_subsystem(
        label="Beam Delivery System",
        subsystem_type=SubsystemType.BEAM_DELIVERY,
        parent_system_id=linac_system.id,
        description="System responsible for beam generation and delivery"
    )
    
    mlc_component = create_component(
        label="Multi-Leaf Collimator",
        component_type="Collimator",
        parent_subsystem_id=beam_delivery.id,
        part_number="MLC-120",
        manufacturer="Varian",
        description="120-leaf multi-leaf collimator for beam shaping"
    )
    
    leaf_motor = create_spare_part(
        label="Leaf Drive Motor",
        parent_component_id=mlc_component.id,
        part_number="LDM-001",
        manufacturer="Varian",
        description="Servo motor for individual leaf positioning"
    )
    
    # Create relationships
    system_subsystem_rel = create_ontology_relationship(
        RelationshipType.HAS_SUBSYSTEM,
        linac_system.id,
        beam_delivery.id,
        "LINAC system contains beam delivery subsystem"
    )
    
    subsystem_component_rel = create_ontology_relationship(
        RelationshipType.HAS_COMPONENT,
        beam_delivery.id,
        mlc_component.id,
        "Beam delivery subsystem contains MLC component"
    )
    
    # Test validation
    systems = [linac_system]
    subsystems = [beam_delivery]
    components = [mlc_component]
    spare_parts = [leaf_motor]
    relationships = [system_subsystem_rel, subsystem_component_rel]
    
    hierarchy_errors = validate_hierarchy_consistency(systems, subsystems, components, spare_parts)
    print(f"Hierarchy validation errors: {len(hierarchy_errors)}")
    
    all_entity_ids = {linac_system.id, beam_delivery.id, mlc_component.id, leaf_motor.id}
    relationship_errors = validate_relationship_consistency(relationships, all_entity_ids)
    print(f"Relationship validation errors: {len(relationship_errors)}")
    
    # Test statistics
    stats = get_ontology_statistics(systems, subsystems, components, spare_parts, relationships)
    print(f"Ontology statistics: {stats}")
    
    # Test OWL conversion
    owl_dict = linac_system.to_owl_dict()
    print(f"OWL representation keys: {list(owl_dict.keys())}")
    
    print("✅ Ontology models test completed successfully!")