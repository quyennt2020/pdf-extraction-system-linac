"""
Ontology Validation Framework for Medical Device Troubleshooting System
Provides comprehensive validation and consistency checking for OWL ontologies
"""

from typing import List, Dict, Any, Optional, Set, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import re
import logging
from datetime import datetime

from ..models.ontology_models import (
    MechatronicSystem, Subsystem, Component, SparePart,
    OntologyRelationship, RelationshipType, ValidationStatus,
    SystemType, SubsystemType
)
from ..core.ontology_builder import OWLOntology


logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationRuleType(Enum):
    """Types of validation rules"""
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    CONSISTENCY = "consistency"
    COMPLETENESS = "completeness"
    DOMAIN_SPECIFIC = "domain_specific"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in the ontology"""
    rule_id: str
    severity: ValidationSeverity
    message: str
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    relationship_id: Optional[str] = None
    suggested_fix: Optional[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}


@dataclass
class ValidationRule:
    """Defines a validation rule for ontology checking"""
    rule_id: str
    name: str
    description: str
    rule_type: ValidationRuleType
    severity: ValidationSeverity
    validator_function: Callable[[OWLOntology], List[ValidationIssue]]
    
    def validate(self, ontology: OWLOntology) -> List[ValidationIssue]:
        """Execute the validation rule"""
        try:
            return self.validator_function(ontology)
        except Exception as e:
            logger.error(f"Error executing validation rule {self.rule_id}: {e}")
            return [ValidationIssue(
                rule_id=self.rule_id,
                severity=ValidationSeverity.ERROR,
                message=f"Validation rule execution failed: {e}"
            )]


class OntologyValidator:
    """Main validator class for ontology validation"""
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
        self.logger = logging.getLogger(__name__)
        self._register_default_rules()
    
    def _register_default_rules(self):
        """Register default validation rules"""
        
        # Structural validation rules
        self.add_rule(ValidationRule(
            rule_id="STR001",
            name="System Existence",
            description="Ontology must contain at least one system",
            rule_type=ValidationRuleType.STRUCTURAL,
            severity=ValidationSeverity.ERROR,
            validator_function=self._validate_system_existence
        ))
        
        self.add_rule(ValidationRule(
            rule_id="STR002",
            name="Hierarchy Integrity",
            description="All child entities must reference valid parent entities",
            rule_type=ValidationRuleType.STRUCTURAL,
            severity=ValidationSeverity.ERROR,
            validator_function=self._validate_hierarchy_integrity
        ))
        
        self.add_rule(ValidationRule(
            rule_id="STR003",
            name="Relationship Validity",
            description="All relationships must reference existing entities",
            rule_type=ValidationRuleType.STRUCTURAL,
            severity=ValidationSeverity.ERROR,
            validator_function=self._validate_relationship_validity
        ))
        
        # Semantic validation rules
        self.add_rule(ValidationRule(
            rule_id="SEM001",
            name="Entity Naming Convention",
            description="Entity names should follow naming conventions",
            rule_type=ValidationRuleType.SEMANTIC,
            severity=ValidationSeverity.WARNING,
            validator_function=self._validate_naming_conventions
        ))
        
        self.add_rule(ValidationRule(
            rule_id="SEM002",
            name="Required Properties",
            description="Entities must have required properties filled",
            rule_type=ValidationRuleType.SEMANTIC,
            severity=ValidationSeverity.WARNING,
            validator_function=self._validate_required_properties
        ))
        
        # Consistency validation rules
        self.add_rule(ValidationRule(
            rule_id="CON001",
            name="Circular Dependencies",
            description="No circular dependencies in hierarchy",
            rule_type=ValidationRuleType.CONSISTENCY,
            severity=ValidationSeverity.ERROR,
            validator_function=self._validate_no_circular_dependencies
        ))
        
        self.add_rule(ValidationRule(
            rule_id="CON002",
            name="Relationship Consistency",
            description="Relationships should be logically consistent",
            rule_type=ValidationRuleType.CONSISTENCY,
            severity=ValidationSeverity.WARNING,
            validator_function=self._validate_relationship_consistency
        ))
        
        # Completeness validation rules
        self.add_rule(ValidationRule(
            rule_id="COM001",
            name="Subsystem Coverage",
            description="Systems should have appropriate subsystems",
            rule_type=ValidationRuleType.COMPLETENESS,
            severity=ValidationSeverity.INFO,
            validator_function=self._validate_subsystem_coverage
        ))
        
        # Domain-specific validation rules
        self.add_rule(ValidationRule(
            rule_id="DOM001",
            name="LINAC Subsystem Completeness",
            description="LINAC systems should have standard subsystems",
            rule_type=ValidationRuleType.DOMAIN_SPECIFIC,
            severity=ValidationSeverity.WARNING,
            validator_function=self._validate_linac_subsystems
        ))
        
        self.add_rule(ValidationRule(
            rule_id="DOM002",
            name="Medical Device Standards",
            description="Entities should comply with medical device standards",
            rule_type=ValidationRuleType.DOMAIN_SPECIFIC,
            severity=ValidationSeverity.INFO,
            validator_function=self._validate_medical_device_standards
        ))
    
    def add_rule(self, rule: ValidationRule):
        """Add a validation rule"""
        self.rules.append(rule)
        self.logger.debug(f"Added validation rule: {rule.rule_id} - {rule.name}")
    
    def remove_rule(self, rule_id: str):
        """Remove a validation rule by ID"""
        self.rules = [rule for rule in self.rules if rule.rule_id != rule_id]
        self.logger.debug(f"Removed validation rule: {rule_id}")
    
    def validate_ontology(
        self, 
        ontology: OWLOntology,
        rule_types: Optional[List[ValidationRuleType]] = None,
        severity_filter: Optional[ValidationSeverity] = None
    ) -> Dict[str, Any]:
        """Validate ontology against all applicable rules"""
        
        start_time = datetime.now()
        all_issues = []
        
        # Filter rules if specified
        rules_to_run = self.rules
        if rule_types:
            rules_to_run = [rule for rule in rules_to_run if rule.rule_type in rule_types]
        if severity_filter:
            rules_to_run = [rule for rule in rules_to_run if rule.severity == severity_filter]
        
        # Execute validation rules
        for rule in rules_to_run:
            self.logger.debug(f"Executing validation rule: {rule.rule_id}")
            issues = rule.validate(ontology)
            all_issues.extend(issues)
        
        # Categorize issues
        issues_by_severity = {
            ValidationSeverity.ERROR: [],
            ValidationSeverity.WARNING: [],
            ValidationSeverity.INFO: []
        }
        
        for issue in all_issues:
            issues_by_severity[issue.severity].append(issue)
        
        # Calculate validation score (0-100)
        total_issues = len(all_issues)
        error_count = len(issues_by_severity[ValidationSeverity.ERROR])
        warning_count = len(issues_by_severity[ValidationSeverity.WARNING])
        
        # Score calculation: errors are heavily penalized, warnings less so
        max_score = 100
        error_penalty = 10  # Each error reduces score by 10
        warning_penalty = 2  # Each warning reduces score by 2
        
        score = max_score - (error_count * error_penalty) - (warning_count * warning_penalty)
        score = max(0, score)  # Ensure score doesn't go below 0
        
        validation_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "validation_timestamp": start_time.isoformat(),
            "validation_duration_seconds": validation_time,
            "is_valid": error_count == 0,
            "validation_score": score,
            "total_issues": total_issues,
            "issues_by_severity": {
                "errors": len(issues_by_severity[ValidationSeverity.ERROR]),
                "warnings": len(issues_by_severity[ValidationSeverity.WARNING]),
                "info": len(issues_by_severity[ValidationSeverity.INFO])
            },
            "issues": [self._issue_to_dict(issue) for issue in all_issues],
            "rules_executed": len(rules_to_run),
            "ontology_statistics": ontology.get_statistics()
        }
    
    def _issue_to_dict(self, issue: ValidationIssue) -> Dict[str, Any]:
        """Convert validation issue to dictionary"""
        return {
            "rule_id": issue.rule_id,
            "severity": issue.severity.value,
            "message": issue.message,
            "entity_id": issue.entity_id,
            "entity_type": issue.entity_type,
            "relationship_id": issue.relationship_id,
            "suggested_fix": issue.suggested_fix,
            "context": issue.context
        }
    
    # Validation rule implementations
    
    def _validate_system_existence(self, ontology: OWLOntology) -> List[ValidationIssue]:
        """Validate that ontology contains at least one system"""
        issues = []
        
        if not ontology.systems:
            issues.append(ValidationIssue(
                rule_id="STR001",
                severity=ValidationSeverity.ERROR,
                message="Ontology must contain at least one mechatronic system",
                suggested_fix="Add a MechatronicSystem entity to the ontology"
            ))
        
        return issues
    
    def _validate_hierarchy_integrity(self, ontology: OWLOntology) -> List[ValidationIssue]:
        """Validate hierarchy integrity"""
        issues = []
        
        # Get all entity IDs
        system_ids = {sys.id for sys in ontology.systems}
        subsystem_ids = {sub.id for sub in ontology.subsystems}
        component_ids = {comp.id for comp in ontology.components}
        
        # Check subsystem parent references
        for subsystem in ontology.subsystems:
            if subsystem.parent_system_id and subsystem.parent_system_id not in system_ids:
                issues.append(ValidationIssue(
                    rule_id="STR002",
                    severity=ValidationSeverity.ERROR,
                    message=f"Subsystem '{subsystem.label}' references non-existent parent system",
                    entity_id=subsystem.id,
                    entity_type="Subsystem",
                    suggested_fix="Update parent_system_id to reference an existing system or create the referenced system"
                ))
        
        # Check component parent references
        for component in ontology.components:
            if component.parent_subsystem_id and component.parent_subsystem_id not in subsystem_ids:
                issues.append(ValidationIssue(
                    rule_id="STR002",
                    severity=ValidationSeverity.ERROR,
                    message=f"Component '{component.label}' references non-existent parent subsystem",
                    entity_id=component.id,
                    entity_type="Component",
                    suggested_fix="Update parent_subsystem_id to reference an existing subsystem or create the referenced subsystem"
                ))
        
        # Check spare part parent references
        for spare_part in ontology.spare_parts:
            if spare_part.parent_component_id and spare_part.parent_component_id not in component_ids:
                issues.append(ValidationIssue(
                    rule_id="STR002",
                    severity=ValidationSeverity.ERROR,
                    message=f"Spare part '{spare_part.label}' references non-existent parent component",
                    entity_id=spare_part.id,
                    entity_type="SparePart",
                    suggested_fix="Update parent_component_id to reference an existing component or create the referenced component"
                ))
        
        return issues
    
    def _validate_relationship_validity(self, ontology: OWLOntology) -> List[ValidationIssue]:
        """Validate that all relationships reference existing entities"""
        issues = []
        
        all_entity_ids = ontology.get_all_entity_ids()
        
        for relationship in ontology.relationships:
            if relationship.source_entity_id not in all_entity_ids:
                issues.append(ValidationIssue(
                    rule_id="STR003",
                    severity=ValidationSeverity.ERROR,
                    message=f"Relationship references non-existent source entity: {relationship.source_entity_id}",
                    relationship_id=relationship.id,
                    suggested_fix="Update source_entity_id to reference an existing entity or remove the relationship"
                ))
            
            if relationship.target_entity_id not in all_entity_ids:
                issues.append(ValidationIssue(
                    rule_id="STR003",
                    severity=ValidationSeverity.ERROR,
                    message=f"Relationship references non-existent target entity: {relationship.target_entity_id}",
                    relationship_id=relationship.id,
                    suggested_fix="Update target_entity_id to reference an existing entity or remove the relationship"
                ))
        
        return issues
    
    def _validate_naming_conventions(self, ontology: OWLOntology) -> List[ValidationIssue]:
        """Validate entity naming conventions"""
        issues = []
        
        # Check for empty or generic names
        all_entities = ontology.systems + ontology.subsystems + ontology.components + ontology.spare_parts
        
        for entity in all_entities:
            if not entity.label or entity.label.strip() == "":
                issues.append(ValidationIssue(
                    rule_id="SEM001",
                    severity=ValidationSeverity.WARNING,
                    message=f"Entity has empty label",
                    entity_id=entity.id,
                    entity_type=entity.__class__.__name__,
                    suggested_fix="Provide a descriptive label for the entity"
                ))
            
            elif entity.label.lower() in ["unknown", "unnamed", "untitled", "default"]:
                issues.append(ValidationIssue(
                    rule_id="SEM001",
                    severity=ValidationSeverity.WARNING,
                    message=f"Entity has generic label: '{entity.label}'",
                    entity_id=entity.id,
                    entity_type=entity.__class__.__name__,
                    suggested_fix="Provide a more specific and descriptive label"
                ))
        
        return issues
    
    def _validate_required_properties(self, ontology: OWLOntology) -> List[ValidationIssue]:
        """Validate that entities have required properties"""
        issues = []
        
        # Check systems
        for system in ontology.systems:
            if not system.manufacturer:
                issues.append(ValidationIssue(
                    rule_id="SEM002",
                    severity=ValidationSeverity.WARNING,
                    message=f"System '{system.label}' missing manufacturer information",
                    entity_id=system.id,
                    entity_type="MechatronicSystem",
                    suggested_fix="Add manufacturer information to the system"
                ))
        
        # Check components
        for component in ontology.components:
            if not component.component_type:
                issues.append(ValidationIssue(
                    rule_id="SEM002",
                    severity=ValidationSeverity.WARNING,
                    message=f"Component '{component.label}' missing component type",
                    entity_id=component.id,
                    entity_type="Component",
                    suggested_fix="Specify the component type"
                ))
        
        # Check spare parts
        for spare_part in ontology.spare_parts:
            if not spare_part.part_number:
                issues.append(ValidationIssue(
                    rule_id="SEM002",
                    severity=ValidationSeverity.WARNING,
                    message=f"Spare part '{spare_part.label}' missing part number",
                    entity_id=spare_part.id,
                    entity_type="SparePart",
                    suggested_fix="Add part number for the spare part"
                ))
        
        return issues
    
    def _validate_no_circular_dependencies(self, ontology: OWLOntology) -> List[ValidationIssue]:
        """Validate no circular dependencies in hierarchy"""
        issues = []
        
        # Build hierarchy graph
        hierarchy_graph = {}
        
        # Add system -> subsystem relationships
        for subsystem in ontology.subsystems:
            if subsystem.parent_system_id:
                if subsystem.parent_system_id not in hierarchy_graph:
                    hierarchy_graph[subsystem.parent_system_id] = []
                hierarchy_graph[subsystem.parent_system_id].append(subsystem.id)
        
        # Add subsystem -> component relationships
        for component in ontology.components:
            if component.parent_subsystem_id:
                if component.parent_subsystem_id not in hierarchy_graph:
                    hierarchy_graph[component.parent_subsystem_id] = []
                hierarchy_graph[component.parent_subsystem_id].append(component.id)
        
        # Add component -> spare part relationships
        for spare_part in ontology.spare_parts:
            if spare_part.parent_component_id:
                if spare_part.parent_component_id not in hierarchy_graph:
                    hierarchy_graph[spare_part.parent_component_id] = []
                hierarchy_graph[spare_part.parent_component_id].append(spare_part.id)
        
        # Check for cycles using DFS
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in hierarchy_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for node in hierarchy_graph:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    issues.append(ValidationIssue(
                        rule_id="CON001",
                        severity=ValidationSeverity.ERROR,
                        message=f"Circular dependency detected in hierarchy starting from entity: {node}",
                        entity_id=node,
                        suggested_fix="Remove circular references in the hierarchy"
                    ))
        
        return issues
    
    def _validate_relationship_consistency(self, ontology: OWLOntology) -> List[ValidationIssue]:
        """Validate relationship consistency"""
        issues = []
        
        # Check for conflicting relationships
        relationship_pairs = {}
        
        for rel in ontology.relationships:
            pair_key = (rel.source_entity_id, rel.target_entity_id)
            if pair_key not in relationship_pairs:
                relationship_pairs[pair_key] = []
            relationship_pairs[pair_key].append(rel)
        
        # Look for conflicting relationship types
        conflicting_types = [
            (RelationshipType.CONTROLS, RelationshipType.CONTROLLED_BY),
            (RelationshipType.MONITORS, RelationshipType.MONITORED_BY),
            (RelationshipType.CAUSES, RelationshipType.CAUSED_BY)
        ]
        
        for pair, relationships in relationship_pairs.items():
            if len(relationships) > 1:
                rel_types = [rel.relationship_type for rel in relationships]
                
                for type1, type2 in conflicting_types:
                    if type1 in rel_types and type2 in rel_types:
                        issues.append(ValidationIssue(
                            rule_id="CON002",
                            severity=ValidationSeverity.WARNING,
                            message=f"Conflicting relationship types between entities {pair[0]} and {pair[1]}",
                            context={"relationship_types": [t.value for t in rel_types]},
                            suggested_fix="Review and resolve conflicting relationship types"
                        ))
        
        return issues
    
    def _validate_subsystem_coverage(self, ontology: OWLOntology) -> List[ValidationIssue]:
        """Validate that systems have appropriate subsystem coverage"""
        issues = []
        
        for system in ontology.systems:
            # Count subsystems for this system
            subsystem_count = sum(1 for sub in ontology.subsystems if sub.parent_system_id == system.id)
            
            if subsystem_count == 0:
                issues.append(ValidationIssue(
                    rule_id="COM001",
                    severity=ValidationSeverity.INFO,
                    message=f"System '{system.label}' has no subsystems defined",
                    entity_id=system.id,
                    entity_type="MechatronicSystem",
                    suggested_fix="Consider adding subsystems to provide better system organization"
                ))
            elif subsystem_count < 3:
                issues.append(ValidationIssue(
                    rule_id="COM001",
                    severity=ValidationSeverity.INFO,
                    message=f"System '{system.label}' has only {subsystem_count} subsystem(s)",
                    entity_id=system.id,
                    entity_type="MechatronicSystem",
                    context={"subsystem_count": subsystem_count},
                    suggested_fix="Consider if additional subsystems would improve system organization"
                ))
        
        return issues
    
    def _validate_linac_subsystems(self, ontology: OWLOntology) -> List[ValidationIssue]:
        """Validate LINAC-specific subsystem requirements"""
        issues = []
        
        # Expected LINAC subsystems
        expected_linac_subsystems = [
            SubsystemType.BEAM_DELIVERY,
            SubsystemType.PATIENT_POSITIONING,
            SubsystemType.TREATMENT_CONTROL,
            SubsystemType.SAFETY_INTERLOCK
        ]
        
        for system in ontology.systems:
            if system.system_type == SystemType.LINAC:
                # Get subsystems for this LINAC
                system_subsystems = [
                    sub for sub in ontology.subsystems 
                    if sub.parent_system_id == system.id
                ]
                
                existing_types = {sub.subsystem_type for sub in system_subsystems}
                
                for expected_type in expected_linac_subsystems:
                    if expected_type not in existing_types:
                        issues.append(ValidationIssue(
                            rule_id="DOM001",
                            severity=ValidationSeverity.WARNING,
                            message=f"LINAC system '{system.label}' missing expected subsystem: {expected_type.value}",
                            entity_id=system.id,
                            entity_type="MechatronicSystem",
                            context={"missing_subsystem_type": expected_type.value},
                            suggested_fix=f"Consider adding a {expected_type.value} subsystem"
                        ))
        
        return issues
    
    def _validate_medical_device_standards(self, ontology: OWLOntology) -> List[ValidationIssue]:
        """Validate compliance with medical device standards"""
        issues = []
        
        # Check for IEC 60601 compliance indicators
        all_entities = ontology.systems + ontology.subsystems + ontology.components + ontology.spare_parts
        
        safety_related_keywords = ["safety", "interlock", "emergency", "alarm", "monitor"]
        
        for entity in all_entities:
            entity_text = f"{entity.label} {entity.description}".lower()
            
            # Check if safety-related entity has appropriate validation status
            if any(keyword in entity_text for keyword in safety_related_keywords):
                if entity.metadata.validation_status == ValidationStatus.NOT_VALIDATED:
                    issues.append(ValidationIssue(
                        rule_id="DOM002",
                        severity=ValidationSeverity.INFO,
                        message=f"Safety-related entity '{entity.label}' should be validated by expert",
                        entity_id=entity.id,
                        entity_type=entity.__class__.__name__,
                        suggested_fix="Ensure safety-related entities are reviewed and validated by qualified experts"
                    ))
        
        return issues


# Utility functions for validation

def create_validation_report(validation_result: Dict[str, Any]) -> str:
    """Create a human-readable validation report"""
    
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("ONTOLOGY VALIDATION REPORT")
    report_lines.append("=" * 60)
    report_lines.append(f"Validation Time: {validation_result['validation_timestamp']}")
    report_lines.append(f"Duration: {validation_result['validation_duration_seconds']:.2f} seconds")
    report_lines.append(f"Overall Status: {'✅ VALID' if validation_result['is_valid'] else '❌ INVALID'}")
    report_lines.append(f"Validation Score: {validation_result['validation_score']}/100")
    report_lines.append("")
    
    # Summary
    issues_summary = validation_result['issues_by_severity']
    report_lines.append("ISSUE SUMMARY:")
    report_lines.append(f"  Errors: {issues_summary['errors']}")
    report_lines.append(f"  Warnings: {issues_summary['warnings']}")
    report_lines.append(f"  Info: {issues_summary['info']}")
    report_lines.append(f"  Total Issues: {validation_result['total_issues']}")
    report_lines.append("")
    
    # Ontology statistics
    stats = validation_result['ontology_statistics']
    report_lines.append("ONTOLOGY STATISTICS:")
    report_lines.append(f"  Total Entities: {stats['total_entities']}")
    report_lines.append(f"  Systems: {stats['entity_counts']['systems']}")
    report_lines.append(f"  Subsystems: {stats['entity_counts']['subsystems']}")
    report_lines.append(f"  Components: {stats['entity_counts']['components']}")
    report_lines.append(f"  Spare Parts: {stats['entity_counts']['spare_parts']}")
    report_lines.append(f"  Relationships: {stats['total_relationships']}")
    report_lines.append("")
    
    # Detailed issues
    if validation_result['issues']:
        report_lines.append("DETAILED ISSUES:")
        report_lines.append("-" * 40)
        
        for issue in validation_result['issues']:
            severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}
            icon = severity_icon.get(issue['severity'], "•")
            
            report_lines.append(f"{icon} [{issue['rule_id']}] {issue['message']}")
            if issue['entity_id']:
                report_lines.append(f"    Entity: {issue['entity_type']} ({issue['entity_id']})")
            if issue['suggested_fix']:
                report_lines.append(f"    Suggested Fix: {issue['suggested_fix']}")
            report_lines.append("")
    
    return "\n".join(report_lines)


if __name__ == "__main__":
    # Test the validation framework
    from ..core.ontology_builder import OntologyBuilder
    
    # Create a test ontology
    builder = OntologyBuilder()
    ontology = builder.create_linac_ontology("test_validation")
    
    # Create validator and run validation
    validator = OntologyValidator()
    result = validator.validate_ontology(ontology)
    
    print(f"Validation completed: {'✅ Valid' if result['is_valid'] else '❌ Invalid'}")
    print(f"Score: {result['validation_score']}/100")
    print(f"Issues: {result['total_issues']}")
    
    # Generate report
    report = create_validation_report(result)
    print("\n" + report)
    
    print("✅ Ontology validator test completed successfully!")