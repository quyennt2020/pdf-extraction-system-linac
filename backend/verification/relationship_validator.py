"""
Relationship Validator and Editor
Handles relationship validation, inference, and domain knowledge suggestions
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from backend.models.ontology_models import (
    OntologyRelationship, RelationshipType, ValidationStatus,
    MechatronicSystem, Subsystem, Component, SparePart
)

class RelationshipValidationError(Enum):
    """Types of relationship validation errors"""
    CIRCULAR_DEPENDENCY = "circular_dependency"
    INVALID_DOMAIN_RANGE = "invalid_domain_range"
    DUPLICATE_RELATIONSHIP = "duplicate_relationship"
    MISSING_INVERSE = "missing_inverse"
    CARDINALITY_VIOLATION = "cardinality_violation"
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"

class InferenceConfidence(Enum):
    """Confidence levels for relationship inference"""
    HIGH = "high"      # >0.9
    MEDIUM = "medium"  # 0.7-0.9
    LOW = "low"        # 0.5-0.7
    VERY_LOW = "very_low"  # <0.5

@dataclass
class RelationshipValidationIssue:
    """Represents a relationship validation issue"""
    issue_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    relationship_id: str = ""
    error_type: RelationshipValidationError = RelationshipValidationError.SEMANTIC_INCONSISTENCY
    severity: str = "medium"  # critical, high, medium, low
    message: str = ""
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False
    created_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RelationshipSuggestion:
    """Suggested relationship based on domain knowledge"""
    suggestion_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_entity_id: str = ""
    target_entity_id: str = ""
    relationship_type: RelationshipType = RelationshipType.PART_OF
    confidence: InferenceConfidence = InferenceConfidence.MEDIUM
    confidence_score: float = 0.0
    reasoning: str = ""
    domain_rule: str = ""
    evidence: List[str] = field(default_factory=list)
    created_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RelationshipValidationResult:
    """Result of relationship validation"""
    relationship_id: str
    is_valid: bool
    issues: List[RelationshipValidationIssue] = field(default_factory=list)
    suggestions: List[RelationshipSuggestion] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.now)

class RelationshipValidator:
    """Validates relationships and provides domain-based suggestions"""
    
    def __init__(self):
        self.domain_rules = self._initialize_domain_rules()
        self.relationship_constraints = self._initialize_constraints()
        self.inference_patterns = self._initialize_inference_patterns()
    
    def _initialize_domain_rules(self) -> Dict[str, Any]:
        """Initialize domain-specific relationship rules"""
        return {
            "medical_device_hierarchy": {
                "system_to_subsystem": {
                    "allowed_types": [RelationshipType.HAS_SUBSYSTEM],
                    "cardinality": "one_to_many",
                    "required": True
                },
                "subsystem_to_component": {
                    "allowed_types": [RelationshipType.HAS_COMPONENT],
                    "cardinality": "one_to_many",
                    "required": True
                },
                "component_to_spare_part": {
                    "allowed_types": [RelationshipType.HAS_SPARE_PART],
                    "cardinality": "one_to_many",
                    "required": False
                }
            },
            "functional_relationships": {
                "control_relationships": {
                    "allowed_types": [RelationshipType.CONTROLS, RelationshipType.CONTROLLED_BY],
                    "symmetric": False,
                    "transitive": False
                },
                "monitoring_relationships": {
                    "allowed_types": [RelationshipType.MONITORS, RelationshipType.MONITORED_BY],
                    "symmetric": False,
                    "transitive": False
                }
            },
            "causal_relationships": {
                "error_causation": {
                    "allowed_types": [RelationshipType.CAUSES, RelationshipType.CAUSED_BY],
                    "symmetric": False,
                    "transitive": True
                }
            }
        }
    
    def _initialize_constraints(self) -> Dict[RelationshipType, Dict[str, Any]]:
        """Initialize relationship type constraints"""
        return {
            RelationshipType.HAS_SUBSYSTEM: {
                "domain": ["system"],
                "range": ["subsystem"],
                "cardinality": "one_to_many",
                "inverse": RelationshipType.PART_OF
            },
            RelationshipType.HAS_COMPONENT: {
                "domain": ["subsystem"],
                "range": ["component"],
                "cardinality": "one_to_many",
                "inverse": RelationshipType.PART_OF
            },
            RelationshipType.HAS_SPARE_PART: {
                "domain": ["component"],
                "range": ["spare_part"],
                "cardinality": "one_to_many",
                "inverse": RelationshipType.PART_OF
            },
            RelationshipType.PART_OF: {
                "domain": ["subsystem", "component", "spare_part"],
                "range": ["system", "subsystem", "component"],
                "cardinality": "many_to_one",
                "inverse": None  # Multiple possible inverses
            },
            RelationshipType.CONTROLS: {
                "domain": ["component", "subsystem"],
                "range": ["component", "subsystem"],
                "cardinality": "many_to_many",
                "inverse": RelationshipType.CONTROLLED_BY
            },
            RelationshipType.MONITORS: {
                "domain": ["component"],
                "range": ["component", "subsystem"],
                "cardinality": "many_to_many",
                "inverse": RelationshipType.MONITORED_BY
            }
        }
    
    def _initialize_inference_patterns(self) -> List[Dict[str, Any]]:
        """Initialize patterns for relationship inference"""
        return [
            {
                "name": "hierarchical_transitivity",
                "pattern": "If A has_subsystem B and B has_component C, then A contains C",
                "confidence": 0.9,
                "rule": lambda entities, rels: self._infer_hierarchical_containment(entities, rels)
            },
            {
                "name": "control_inference",
                "pattern": "Components with 'motor' or 'actuator' in name likely control other components",
                "confidence": 0.7,
                "rule": lambda entities, rels: self._infer_control_relationships(entities, rels)
            },
            {
                "name": "monitoring_inference", 
                "pattern": "Components with 'sensor' in name likely monitor other components",
                "confidence": 0.8,
                "rule": lambda entities, rels: self._infer_monitoring_relationships(entities, rels)
            },
            {
                "name": "spare_part_inference",
                "pattern": "Components with similar part numbers likely share spare parts",
                "confidence": 0.6,
                "rule": lambda entities, rels: self._infer_spare_part_relationships(entities, rels)
            }
        ]
    
    def validate_relationship(
        self,
        relationship: OntologyRelationship,
        source_entity: Any,
        target_entity: Any,
        source_type: str,
        target_type: str,
        existing_relationships: List[OntologyRelationship] = None
    ) -> RelationshipValidationResult:
        """Validate a single relationship"""
        
        issues = []
        suggestions = []
        
        # Check domain and range constraints
        constraints = self.relationship_constraints.get(relationship.relationship_type)
        if constraints:
            # Validate domain (source entity type)
            if source_type not in constraints["domain"]:
                issues.append(RelationshipValidationIssue(
                    relationship_id=relationship.id,
                    error_type=RelationshipValidationError.INVALID_DOMAIN_RANGE,
                    severity="high",
                    message=f"Invalid source type '{source_type}' for relationship '{relationship.relationship_type.value}'. Expected: {constraints['domain']}",
                    suggested_fix=f"Change source entity type or use different relationship type"
                ))
            
            # Validate range (target entity type)
            if target_type not in constraints["range"]:
                issues.append(RelationshipValidationIssue(
                    relationship_id=relationship.id,
                    error_type=RelationshipValidationError.INVALID_DOMAIN_RANGE,
                    severity="high",
                    message=f"Invalid target type '{target_type}' for relationship '{relationship.relationship_type.value}'. Expected: {constraints['range']}",
                    suggested_fix=f"Change target entity type or use different relationship type"
                ))
        
        # Check for circular dependencies
        if existing_relationships:
            if self._has_circular_dependency(relationship, existing_relationships):
                issues.append(RelationshipValidationIssue(
                    relationship_id=relationship.id,
                    error_type=RelationshipValidationError.CIRCULAR_DEPENDENCY,
                    severity="critical",
                    message="Relationship creates circular dependency in hierarchy",
                    suggested_fix="Remove or modify relationship to break the cycle"
                ))
        
        # Check for duplicates
        if existing_relationships:
            duplicates = [r for r in existing_relationships 
                         if (r.source_entity_id == relationship.source_entity_id and 
                             r.target_entity_id == relationship.target_entity_id and
                             r.relationship_type == relationship.relationship_type and
                             r.id != relationship.id)]
            if duplicates:
                issues.append(RelationshipValidationIssue(
                    relationship_id=relationship.id,
                    error_type=RelationshipValidationError.DUPLICATE_RELATIONSHIP,
                    severity="medium",
                    message="Duplicate relationship already exists",
                    suggested_fix="Remove duplicate or modify relationship properties",
                    auto_fixable=True
                ))
        
        # Generate suggestions based on domain knowledge
        domain_suggestions = self._generate_domain_suggestions(
            source_entity, target_entity, source_type, target_type
        )
        suggestions.extend(domain_suggestions)
        
        is_valid = len([i for i in issues if i.severity in ["critical", "high"]]) == 0
        
        return RelationshipValidationResult(
            relationship_id=relationship.id,
            is_valid=is_valid,
            issues=issues,
            suggestions=suggestions
        )
    
    def infer_relationships(
        self,
        entities: Dict[str, Tuple[Any, str]],  # entity_id -> (entity, type)
        existing_relationships: List[OntologyRelationship]
    ) -> List[RelationshipSuggestion]:
        """Infer potential relationships based on domain knowledge"""
        
        suggestions = []
        
        # Apply each inference pattern
        for pattern in self.inference_patterns:
            try:
                pattern_suggestions = pattern["rule"](entities, existing_relationships)
                for suggestion in pattern_suggestions:
                    suggestion.confidence_score = pattern["confidence"]
                    suggestion.domain_rule = pattern["name"]
                    suggestion.reasoning = pattern["pattern"]
                suggestions.extend(pattern_suggestions)
            except Exception as e:
                print(f"Error applying inference pattern {pattern['name']}: {e}")
        
        # Sort by confidence score
        suggestions.sort(key=lambda s: s.confidence_score, reverse=True)
        
        return suggestions
    
    def _has_circular_dependency(
        self,
        new_relationship: OntologyRelationship,
        existing_relationships: List[OntologyRelationship]
    ) -> bool:
        """Check if adding this relationship would create a circular dependency"""
        
        # Only check for hierarchical relationships that could create cycles
        hierarchical_types = [
            RelationshipType.HAS_SUBSYSTEM,
            RelationshipType.HAS_COMPONENT,
            RelationshipType.HAS_SPARE_PART,
            RelationshipType.PART_OF
        ]
        
        if new_relationship.relationship_type not in hierarchical_types:
            return False
        
        # Build graph of hierarchical relationships
        graph = {}
        for rel in existing_relationships:
            if rel.relationship_type in hierarchical_types:
                if rel.source_entity_id not in graph:
                    graph[rel.source_entity_id] = []
                graph[rel.source_entity_id].append(rel.target_entity_id)
        
        # Add the new relationship
        if new_relationship.source_entity_id not in graph:
            graph[new_relationship.source_entity_id] = []
        graph[new_relationship.source_entity_id].append(new_relationship.target_entity_id)
        
        # Check for cycles using DFS
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for node in graph:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    return True
        
        return False
    
    def _generate_domain_suggestions(
        self,
        source_entity: Any,
        target_entity: Any,
        source_type: str,
        target_type: str
    ) -> List[RelationshipSuggestion]:
        """Generate relationship suggestions based on domain knowledge"""
        
        suggestions = []
        
        # Hierarchical relationship suggestions
        if source_type == "system" and target_type == "subsystem":
            suggestions.append(RelationshipSuggestion(
                source_entity_id=source_entity.id,
                target_entity_id=target_entity.id,
                relationship_type=RelationshipType.HAS_SUBSYSTEM,
                confidence=InferenceConfidence.HIGH,
                confidence_score=0.9,
                reasoning="Systems typically contain subsystems in medical device hierarchy",
                domain_rule="medical_device_hierarchy"
            ))
        
        elif source_type == "subsystem" and target_type == "component":
            suggestions.append(RelationshipSuggestion(
                source_entity_id=source_entity.id,
                target_entity_id=target_entity.id,
                relationship_type=RelationshipType.HAS_COMPONENT,
                confidence=InferenceConfidence.HIGH,
                confidence_score=0.9,
                reasoning="Subsystems typically contain components",
                domain_rule="medical_device_hierarchy"
            ))
        
        # Functional relationship suggestions based on naming patterns
        if hasattr(source_entity, 'label') and hasattr(target_entity, 'label'):
            source_label = source_entity.label.lower()
            target_label = target_entity.label.lower()
            
            # Control relationships
            if any(keyword in source_label for keyword in ['motor', 'actuator', 'controller']):
                if any(keyword in target_label for keyword in ['position', 'movement', 'rotation']):
                    suggestions.append(RelationshipSuggestion(
                        source_entity_id=source_entity.id,
                        target_entity_id=target_entity.id,
                        relationship_type=RelationshipType.CONTROLS,
                        confidence=InferenceConfidence.MEDIUM,
                        confidence_score=0.7,
                        reasoning="Motors and actuators typically control positioning systems",
                        domain_rule="control_inference"
                    ))
            
            # Monitoring relationships
            if any(keyword in source_label for keyword in ['sensor', 'detector', 'monitor']):
                suggestions.append(RelationshipSuggestion(
                    source_entity_id=source_entity.id,
                    target_entity_id=target_entity.id,
                    relationship_type=RelationshipType.MONITORS,
                    confidence=InferenceConfidence.MEDIUM,
                    confidence_score=0.8,
                    reasoning="Sensors and detectors typically monitor other components",
                    domain_rule="monitoring_inference"
                ))
        
        return suggestions
    
    def _infer_hierarchical_containment(
        self,
        entities: Dict[str, Tuple[Any, str]],
        relationships: List[OntologyRelationship]
    ) -> List[RelationshipSuggestion]:
        """Infer hierarchical containment relationships"""
        suggestions = []
        
        # Build hierarchy graph
        hierarchy = {}
        for rel in relationships:
            if rel.relationship_type in [RelationshipType.HAS_SUBSYSTEM, RelationshipType.HAS_COMPONENT]:
                if rel.source_entity_id not in hierarchy:
                    hierarchy[rel.source_entity_id] = []
                hierarchy[rel.source_entity_id].append(rel.target_entity_id)
        
        # Find transitive relationships
        for system_id, subsystems in hierarchy.items():
            for subsystem_id in subsystems:
                if subsystem_id in hierarchy:
                    for component_id in hierarchy[subsystem_id]:
                        # Suggest system contains component relationship
                        suggestions.append(RelationshipSuggestion(
                            source_entity_id=system_id,
                            target_entity_id=component_id,
                            relationship_type=RelationshipType.CONTAINS,
                            confidence=InferenceConfidence.HIGH,
                            confidence_score=0.9,
                            reasoning="Transitive containment: system contains subsystem contains component",
                            domain_rule="hierarchical_transitivity",
                            evidence=[f"System {system_id} has subsystem {subsystem_id}", 
                                    f"Subsystem {subsystem_id} has component {component_id}"]
                        ))
        
        return suggestions
    
    def _infer_control_relationships(
        self,
        entities: Dict[str, Tuple[Any, str]],
        relationships: List[OntologyRelationship]
    ) -> List[RelationshipSuggestion]:
        """Infer control relationships based on component types"""
        suggestions = []
        
        controllers = []
        controlled = []
        
        for entity_id, (entity, entity_type) in entities.items():
            if entity_type == "component" and hasattr(entity, 'label'):
                label = entity.label.lower()
                if any(keyword in label for keyword in ['motor', 'actuator', 'controller', 'drive']):
                    controllers.append(entity_id)
                elif any(keyword in label for keyword in ['position', 'movement', 'rotation', 'valve']):
                    controlled.append(entity_id)
        
        # Suggest control relationships
        for controller_id in controllers:
            for controlled_id in controlled:
                if controller_id != controlled_id:
                    suggestions.append(RelationshipSuggestion(
                        source_entity_id=controller_id,
                        target_entity_id=controlled_id,
                        relationship_type=RelationshipType.CONTROLS,
                        confidence=InferenceConfidence.MEDIUM,
                        confidence_score=0.7,
                        reasoning="Control components typically control positioning/movement components",
                        domain_rule="control_inference"
                    ))
        
        return suggestions
    
    def _infer_monitoring_relationships(
        self,
        entities: Dict[str, Tuple[Any, str]],
        relationships: List[OntologyRelationship]
    ) -> List[RelationshipSuggestion]:
        """Infer monitoring relationships based on component types"""
        suggestions = []
        
        monitors = []
        monitored = []
        
        for entity_id, (entity, entity_type) in entities.items():
            if entity_type == "component" and hasattr(entity, 'label'):
                label = entity.label.lower()
                if any(keyword in label for keyword in ['sensor', 'detector', 'monitor', 'encoder']):
                    monitors.append(entity_id)
                else:
                    monitored.append(entity_id)
        
        # Suggest monitoring relationships
        for monitor_id in monitors:
            for monitored_id in monitored:
                if monitor_id != monitored_id:
                    suggestions.append(RelationshipSuggestion(
                        source_entity_id=monitor_id,
                        target_entity_id=monitored_id,
                        relationship_type=RelationshipType.MONITORS,
                        confidence=InferenceConfidence.MEDIUM,
                        confidence_score=0.8,
                        reasoning="Sensors and detectors typically monitor other components",
                        domain_rule="monitoring_inference"
                    ))
        
        return suggestions
    
    def _infer_spare_part_relationships(
        self,
        entities: Dict[str, Tuple[Any, str]],
        relationships: List[OntologyRelationship]
    ) -> List[RelationshipSuggestion]:
        """Infer spare part relationships based on part number similarity"""
        suggestions = []
        
        components = [(eid, entity) for eid, (entity, etype) in entities.items() if etype == "component"]
        spare_parts = [(eid, entity) for eid, (entity, etype) in entities.items() if etype == "spare_part"]
        
        for comp_id, component in components:
            if hasattr(component, 'part_number') and component.part_number:
                comp_part_base = component.part_number.split('-')[0]  # Get base part number
                
                for spare_id, spare_part in spare_parts:
                    if hasattr(spare_part, 'part_number') and spare_part.part_number:
                        spare_part_base = spare_part.part_number.split('-')[0]
                        
                        # If base part numbers match, suggest relationship
                        if comp_part_base == spare_part_base:
                            suggestions.append(RelationshipSuggestion(
                                source_entity_id=comp_id,
                                target_entity_id=spare_id,
                                relationship_type=RelationshipType.HAS_SPARE_PART,
                                confidence=InferenceConfidence.MEDIUM,
                                confidence_score=0.6,
                                reasoning=f"Similar part numbers suggest spare part relationship: {component.part_number} -> {spare_part.part_number}",
                                domain_rule="spare_part_inference"
                            ))
        
        return suggestions


# Factory function
def create_relationship_validator() -> RelationshipValidator:
    """Create and configure relationship validator"""
    return RelationshipValidator()


if __name__ == "__main__":
    # Test the relationship validator
    from backend.models.ontology_models import (
        create_mechatronic_system, create_subsystem, create_component,
        create_ontology_relationship, SystemType, SubsystemType, RelationshipType
    )
    
    validator = create_relationship_validator()
    
    # Create test entities
    system = create_mechatronic_system("Test LINAC", SystemType.LINAC)
    subsystem = create_subsystem("Beam Delivery", SubsystemType.BEAM_DELIVERY, system.id)
    component = create_component("MLC Motor", "Motor", subsystem.id)
    
    # Create test relationship
    relationship = create_ontology_relationship(
        RelationshipType.HAS_COMPONENT,
        subsystem.id,
        component.id,
        "Subsystem contains component"
    )
    
    # Validate relationship
    result = validator.validate_relationship(
        relationship, subsystem, component, "subsystem", "component"
    )
    
    print(f"Relationship validation result:")
    print(f"  Valid: {result.is_valid}")
    print(f"  Issues: {len(result.issues)}")
    print(f"  Suggestions: {len(result.suggestions)}")
    
    for issue in result.issues:
        print(f"    Issue: {issue.message}")
    
    for suggestion in result.suggestions:
        print(f"    Suggestion: {suggestion.reasoning}")
    
    # Test inference
    entities = {
        system.id: (system, "system"),
        subsystem.id: (subsystem, "subsystem"),
        component.id: (component, "component")
    }
    
    suggestions = validator.infer_relationships(entities, [relationship])
    print(f"\nInferred relationships: {len(suggestions)}")
    
    for suggestion in suggestions:
        print(f"  {suggestion.relationship_type.value}: {suggestion.reasoning}")
    
    print("\n✅ Relationship validator test completed!")