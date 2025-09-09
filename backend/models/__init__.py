"""
Data models for the system
"""

from .entity import Entity, EntityType, Relationship
from .ontology_models import (
    MechatronicSystem, Subsystem, Component, SparePart,
    OntologyRelationship, RelationshipType, SystemType, SubsystemType,
    ValidationStatus, OntologyMetadata, TechnicalSpecification
)

__all__ = [
    'Entity', 'EntityType', 'Relationship',
    'MechatronicSystem', 'Subsystem', 'Component', 'SparePart',
    'OntologyRelationship', 'RelationshipType', 'SystemType', 'SubsystemType',
    'ValidationStatus', 'OntologyMetadata', 'TechnicalSpecification'
]
