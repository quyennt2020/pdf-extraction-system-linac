"""
Medical entity data models for the extraction system
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
from datetime import datetime


class EntityType(Enum):
    """Types of medical device entities"""
    ERROR_CODE = "error_code"
    COMPONENT = "component"
    PROCEDURE = "procedure"
    SAFETY_PROTOCOL = "safety_protocol"
    TECHNICAL_SPECIFICATION = "technical_specification"
    # Enhanced ontology types
    MECHATRONIC_SYSTEM = "mechatronic_system"
    SUBSYSTEM = "subsystem"
    SPARE_PART = "spare_part"
    FUNCTION = "function"
    CONTROL_UNIT = "control_unit"


class ErrorCodeCategory(Enum):
    """Categories for error codes"""
    MECHANICAL = "Mechanical"
    ELECTRICAL = "Electrical"
    SOFTWARE = "Software"
    SAFETY = "Safety"
    SYSTEM = "System"


class ErrorCodeSeverity(Enum):
    """Severity levels for error codes"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ComponentType(Enum):
    """Types of medical device components"""
    SENSOR = "Sensor"
    ACTUATOR = "Actuator"
    CONTROLLER = "Controller"
    DISPLAY = "Display"
    MOTOR = "Motor"
    DETECTOR = "Detector"
    MONITOR = "Monitor"
    CHAMBER = "Chamber"
    COLLIMATOR = "Collimator"
    ASSEMBLY = "Assembly"


class ProcedureType(Enum):
    """Types of procedures"""
    CALIBRATION = "Calibration"
    DIAGNOSIS = "Diagnosis"
    REPAIR = "Repair"
    SAFETY_CHECK = "Safety_Check"
    MAINTENANCE = "Maintenance"
    TESTING = "Testing"


class SafetyLevel(Enum):
    """Safety levels for procedures"""
    LEVEL_1 = "Level_1"  # Basic safety
    LEVEL_2 = "Level_2"  # Moderate safety requirements
    LEVEL_3 = "Level_3"  # High safety requirements


class SafetyProtocolType(Enum):
    """Types of safety protocols"""
    WARNING = "WARNING"
    CAUTION = "CAUTION"
    DANGER = "DANGER"
    NOTE = "NOTE"


@dataclass
class Entity:
    """Base entity class"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: EntityType = EntityType.COMPONENT
    confidence: float = 0.8
    source_page: int = 0
    source_text: str = ""
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    reviewed: bool = False
    approved: bool = False
    reviewer_id: Optional[str] = None
    review_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            'id': self.id,
            'entity_type': self.entity_type.value,
            'confidence': self.confidence,
            'source_page': self.source_page,
            'source_text': self.source_text,
            'extraction_timestamp': self.extraction_timestamp.isoformat(),
            'reviewed': self.reviewed,
            'approved': self.approved,
            'reviewer_id': self.reviewer_id,
            'review_notes': self.review_notes
        }


@dataclass
class ErrorCode(Entity):
    """Error code entity"""
    code: str = ""
    software_release: str = "unknown"
    message: str = "unknown"
    description: str = "unknown"
    response: str = "unknown"
    category: ErrorCodeCategory = ErrorCodeCategory.SYSTEM
    severity: ErrorCodeSeverity = ErrorCodeSeverity.MEDIUM
    related_components: List[str] = field(default_factory=list)
    related_procedures: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.entity_type = EntityType.ERROR_CODE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with error code specific fields"""
        base_dict = super().to_dict()
        base_dict.update({
            'code': self.code,
            'software_release': self.software_release,
            'message': self.message,
            'description': self.description,
            'response': self.response,
            'category': self.category.value,
            'severity': self.severity.value,
            'related_components': self.related_components,
            'related_procedures': self.related_procedures
        })
        return base_dict


@dataclass  
class Component(Entity):
    """Component entity"""
    name: str = ""
    component_type: ComponentType = ComponentType.ASSEMBLY
    function: str = "unknown"
    parent_system: str = "unknown"
    specifications: str = "unknown"
    part_number: str = "unknown"
    manufacturer: str = "unknown"
    related_error_codes: List[str] = field(default_factory=list)
    related_procedures: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.entity_type = EntityType.COMPONENT
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with component specific fields"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'component_type': self.component_type.value,
            'function': self.function,
            'parent_system': self.parent_system,
            'specifications': self.specifications,
            'part_number': self.part_number,
            'manufacturer': self.manufacturer,
            'related_error_codes': self.related_error_codes,
            'related_procedures': self.related_procedures
        })
        return base_dict


@dataclass
class Procedure(Entity):
    """Procedure entity"""
    name: str = ""
    procedure_type: ProcedureType = ProcedureType.MAINTENANCE
    description: str = "unknown"
    steps: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    safety_level: SafetyLevel = SafetyLevel.LEVEL_2
    estimated_time: str = "unknown"
    frequency: str = "unknown"
    related_components: List[str] = field(default_factory=list)
    related_error_codes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.entity_type = EntityType.PROCEDURE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with procedure specific fields"""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'procedure_type': self.procedure_type.value,
            'description': self.description,
            'steps': self.steps,
            'prerequisites': self.prerequisites,
            'tools_required': self.tools_required,
            'safety_level': self.safety_level.value,
            'estimated_time': self.estimated_time,
            'frequency': self.frequency,
            'related_components': self.related_components,
            'related_error_codes': self.related_error_codes
        })
        return base_dict


@dataclass
class SafetyProtocol(Entity):
    """Safety protocol entity"""
    protocol_type: SafetyProtocolType = SafetyProtocolType.NOTE
    title: str = "unknown"
    description: str = "unknown"
    applicable_procedures: List[str] = field(default_factory=list)
    compliance_standard: str = "unknown"
    risk_level: str = "unknown"
    mitigation_steps: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.entity_type = EntityType.SAFETY_PROTOCOL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with safety protocol specific fields"""
        base_dict = super().to_dict()
        base_dict.update({
            'protocol_type': self.protocol_type.value,
            'title': self.title,
            'description': self.description,
            'applicable_procedures': self.applicable_procedures,
            'compliance_standard': self.compliance_standard,
            'risk_level': self.risk_level,
            'mitigation_steps': self.mitigation_steps
        })
        return base_dict


@dataclass
class TechnicalSpecification(Entity):
    """Technical specification entity"""
    parameter: str = ""
    value: str = "unknown"
    unit: str = "unknown"
    tolerance: str = "unknown"
    measurement_method: str = "unknown"
    minimum_value: Optional[float] = None
    maximum_value: Optional[float] = None
    nominal_value: Optional[float] = None
    related_components: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.entity_type = EntityType.TECHNICAL_SPECIFICATION
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with technical specification fields"""
        base_dict = super().to_dict()
        base_dict.update({
            'parameter': self.parameter,
            'value': self.value,
            'unit': self.unit,
            'tolerance': self.tolerance,
            'measurement_method': self.measurement_method,
            'minimum_value': self.minimum_value,
            'maximum_value': self.maximum_value,
            'nominal_value': self.nominal_value,
            'related_components': self.related_components
        })
        return base_dict


@dataclass
class Relationship:
    """Relationship between entities"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_entity_id: str = ""
    target_entity_id: str = ""
    relationship_type: str = ""  # causes, applies_to, part_of, prerequisite_for, etc.
    description: str = ""
    confidence: float = 0.8
    bidirectional: bool = False
    extraction_timestamp: datetime = field(default_factory=datetime.now)
    reviewed: bool = False
    approved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary"""
        return {
            'id': self.id,
            'source_entity_id': self.source_entity_id,
            'target_entity_id': self.target_entity_id,
            'relationship_type': self.relationship_type,
            'description': self.description,
            'confidence': self.confidence,
            'bidirectional': self.bidirectional,
            'extraction_timestamp': self.extraction_timestamp.isoformat(),
            'reviewed': self.reviewed,
            'approved': self.approved
        }


# Factory functions for creating entities

def create_error_code(
    code: str,
    software_release: str = "unknown",
    message: str = "unknown",
    description: str = "unknown",
    response: str = "unknown",
    category: str = "System",
    severity: str = "Medium",
    confidence: float = 0.8,
    source_page: int = 0
) -> ErrorCode:
    """Factory function to create ErrorCode entity"""
    
    # Convert string enums to enum objects
    try:
        category_enum = ErrorCodeCategory(category)
    except ValueError:
        category_enum = ErrorCodeCategory.SYSTEM
    
    try:
        severity_enum = ErrorCodeSeverity(severity)
    except ValueError:
        severity_enum = ErrorCodeSeverity.MEDIUM
    
    return ErrorCode(
        code=code,
        software_release=software_release,
        message=message,
        description=description,
        response=response,
        category=category_enum,
        severity=severity_enum,
        confidence=confidence,
        source_page=source_page
    )


def create_component(
    name: str,
    component_type: str = "Assembly",
    function: str = "unknown",
    parent_system: str = "unknown",
    specifications: str = "unknown",
    confidence: float = 0.8,
    source_page: int = 0
) -> Component:
    """Factory function to create Component entity"""
    
    # Convert string enum to enum object
    try:
        type_enum = ComponentType(component_type)
    except ValueError:
        type_enum = ComponentType.ASSEMBLY
    
    return Component(
        name=name,
        component_type=type_enum,
        function=function,
        parent_system=parent_system,
        specifications=specifications,
        confidence=confidence,
        source_page=source_page
    )


def create_procedure(
    name: str,
    procedure_type: str = "Maintenance",
    description: str = "unknown",
    steps: List[str] = None,
    prerequisites: List[str] = None,
    safety_level: str = "Level_2",
    confidence: float = 0.8,
    source_page: int = 0
) -> Procedure:
    """Factory function to create Procedure entity"""
    
    if steps is None:
        steps = []
    if prerequisites is None:
        prerequisites = []
    
    # Convert string enums to enum objects
    try:
        type_enum = ProcedureType(procedure_type)
    except ValueError:
        type_enum = ProcedureType.MAINTENANCE
    
    try:
        safety_enum = SafetyLevel(safety_level)
    except ValueError:
        safety_enum = SafetyLevel.LEVEL_2
    
    return Procedure(
        name=name,
        procedure_type=type_enum,
        description=description,
        steps=steps,
        prerequisites=prerequisites,
        safety_level=safety_enum,
        confidence=confidence,
        source_page=source_page
    )


def create_safety_protocol(
    protocol_type: str = "NOTE",
    title: str = "unknown",
    description: str = "unknown",
    applicable_procedures: List[str] = None,
    compliance_standard: str = "unknown",
    confidence: float = 0.8,
    source_page: int = 0
) -> SafetyProtocol:
    """Factory function to create SafetyProtocol entity"""
    
    if applicable_procedures is None:
        applicable_procedures = []
    
    # Convert string enum to enum object
    try:
        type_enum = SafetyProtocolType(protocol_type)
    except ValueError:
        type_enum = SafetyProtocolType.NOTE
    
    return SafetyProtocol(
        protocol_type=type_enum,
        title=title,
        description=description,
        applicable_procedures=applicable_procedures,
        compliance_standard=compliance_standard,
        confidence=confidence,
        source_page=source_page
    )


def create_technical_specification(
    parameter: str,
    value: str = "unknown",
    unit: str = "unknown",
    tolerance: str = "unknown",
    measurement_method: str = "unknown",
    confidence: float = 0.8,
    source_page: int = 0
) -> TechnicalSpecification:
    """Factory function to create TechnicalSpecification entity"""
    
    return TechnicalSpecification(
        parameter=parameter,
        value=value,
        unit=unit,
        tolerance=tolerance,
        measurement_method=measurement_method,
        confidence=confidence,
        source_page=source_page
    )


def create_relationship(
    source_entity_id: str,
    target_entity_id: str,
    relationship_type: str,
    description: str = "",
    confidence: float = 0.8,
    bidirectional: bool = False
) -> Relationship:
    """Factory function to create Relationship"""
    
    return Relationship(
        source_entity_id=source_entity_id,
        target_entity_id=target_entity_id,
        relationship_type=relationship_type,
        description=description,
        confidence=confidence,
        bidirectional=bidirectional
    )


# Utility functions

def entity_from_dict(entity_dict: Dict[str, Any]) -> Entity:
    """Create entity object from dictionary"""
    
    entity_type = entity_dict.get('entity_type', 'component')
    
    if entity_type == 'error_code':
        return ErrorCode(
            id=entity_dict.get('id', str(uuid.uuid4())),
            code=entity_dict.get('code', ''),
            software_release=entity_dict.get('software_release', 'unknown'),
            message=entity_dict.get('message', 'unknown'),
            description=entity_dict.get('description', 'unknown'),
            response=entity_dict.get('response', 'unknown'),
            category=ErrorCodeCategory(entity_dict.get('category', 'System')),
            severity=ErrorCodeSeverity(entity_dict.get('severity', 'Medium')),
            confidence=entity_dict.get('confidence', 0.8),
            source_page=entity_dict.get('source_page', 0)
        )
    
    elif entity_type == 'component':
        return Component(
            id=entity_dict.get('id', str(uuid.uuid4())),
            name=entity_dict.get('name', ''),
            component_type=ComponentType(entity_dict.get('component_type', 'Assembly')),
            function=entity_dict.get('function', 'unknown'),
            parent_system=entity_dict.get('parent_system', 'unknown'),
            specifications=entity_dict.get('specifications', 'unknown'),
            confidence=entity_dict.get('confidence', 0.8),
            source_page=entity_dict.get('source_page', 0)
        )
    
    elif entity_type == 'procedure':
        return Procedure(
            id=entity_dict.get('id', str(uuid.uuid4())),
            name=entity_dict.get('name', ''),
            procedure_type=ProcedureType(entity_dict.get('procedure_type', 'Maintenance')),
            description=entity_dict.get('description', 'unknown'),
            steps=entity_dict.get('steps', []),
            prerequisites=entity_dict.get('prerequisites', []),
            safety_level=SafetyLevel(entity_dict.get('safety_level', 'Level_2')),
            confidence=entity_dict.get('confidence', 0.8),
            source_page=entity_dict.get('source_page', 0)
        )
    
    elif entity_type == 'safety_protocol':
        return SafetyProtocol(
            id=entity_dict.get('id', str(uuid.uuid4())),
            protocol_type=SafetyProtocolType(entity_dict.get('protocol_type', 'NOTE')),
            title=entity_dict.get('title', 'unknown'),
            description=entity_dict.get('description', 'unknown'),
            applicable_procedures=entity_dict.get('applicable_procedures', []),
            compliance_standard=entity_dict.get('compliance_standard', 'unknown'),
            confidence=entity_dict.get('confidence', 0.8),
            source_page=entity_dict.get('source_page', 0)
        )
    
    elif entity_type == 'technical_specification':
        return TechnicalSpecification(
            id=entity_dict.get('id', str(uuid.uuid4())),
            parameter=entity_dict.get('parameter', ''),
            value=entity_dict.get('value', 'unknown'),
            unit=entity_dict.get('unit', 'unknown'),
            tolerance=entity_dict.get('tolerance', 'unknown'),
            measurement_method=entity_dict.get('measurement_method', 'unknown'),
            confidence=entity_dict.get('confidence', 0.8),
            source_page=entity_dict.get('source_page', 0)
        )
    
    else:
        # Default to base Entity
        return Entity(
            id=entity_dict.get('id', str(uuid.uuid4())),
            entity_type=EntityType(entity_type),
            confidence=entity_dict.get('confidence', 0.8),
            source_page=entity_dict.get('source_page', 0)
        )


def validate_entity(entity: Entity) -> List[str]:
    """Validate entity and return list of validation errors"""
    
    errors = []
    
    # Basic validation
    if not entity.id:
        errors.append("Entity ID is required")
    
    if entity.confidence < 0.0 or entity.confidence > 1.0:
        errors.append("Confidence must be between 0.0 and 1.0")
    
    if entity.source_page < 0:
        errors.append("Source page must be non-negative")
    
    # Entity-specific validation
    if isinstance(entity, ErrorCode):
        if not entity.code:
            errors.append("Error code is required")
        elif not entity.code.isdigit() or len(entity.code) != 4:
            errors.append("Error code must be a 4-digit number")
    
    elif isinstance(entity, Component):
        if not entity.name:
            errors.append("Component name is required")
    
    elif isinstance(entity, Procedure):
        if not entity.name:
            errors.append("Procedure name is required")
    
    elif isinstance(entity, TechnicalSpecification):
        if not entity.parameter:
            errors.append("Parameter name is required")
    
    return errors


def get_entity_summary(entities: List[Entity]) -> Dict[str, Any]:
    """Get summary statistics for a list of entities"""
    
    summary = {
        'total_entities': len(entities),
        'by_type': {},
        'by_confidence': {
            'high': 0,      # > 0.8
            'medium': 0,    # 0.6 - 0.8
            'low': 0        # < 0.6
        },
        'reviewed_count': 0,
        'approved_count': 0,
        'average_confidence': 0.0
    }
    
    if not entities:
        return summary
    
    # Count by type
    for entity in entities:
        entity_type = entity.entity_type.value
        summary['by_type'][entity_type] = summary['by_type'].get(entity_type, 0) + 1
        
        # Count by confidence level
        if entity.confidence > 0.8:
            summary['by_confidence']['high'] += 1
        elif entity.confidence >= 0.6:
            summary['by_confidence']['medium'] += 1
        else:
            summary['by_confidence']['low'] += 1
        
        # Count reviewed/approved
        if entity.reviewed:
            summary['reviewed_count'] += 1
        if entity.approved:
            summary['approved_count'] += 1
    
    # Calculate average confidence
    total_confidence = sum(entity.confidence for entity in entities)
    summary['average_confidence'] = total_confidence / len(entities)
    
    return summary


if __name__ == "__main__":
    # Test the models
    
    # Create sample entities
    error_code = create_error_code(
        code="7002",
        software_release="R6.0x, R6.1x",
        message="MOVEMENT",
        description="Leaf movement error",
        response="Check motor drive",
        category="Mechanical",
        severity="High"
    )
    
    component = create_component(
        name="Leaf Motor Assembly",
        component_type="Motor",
        function="Control leaf positions",
        parent_system="MLC System"
    )
    
    procedure = create_procedure(
        name="Calibration Check",
        procedure_type="Calibration",
        description="Check system calibration",
        steps=["Check files", "Verify calibration"],
        safety_level="Level_2"
    )
    
    # Test validation
    errors = validate_entity(error_code)
    print(f"Error code validation: {len(errors)} errors")
    
    # Test conversion to dict
    error_dict = error_code.to_dict()
    print(f"Error code dict keys: {list(error_dict.keys())}")
    
    # Test summary
    entities = [error_code, component, procedure]
    summary = get_entity_summary(entities)
    print(f"Entity summary: {summary}")
    
    print("✅ Medical entity models test completed successfully!")
