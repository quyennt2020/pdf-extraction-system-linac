"""
Entity Validation Workflow
Handles entity-by-entity review with confidence indicators and audit trails
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from backend.models.ontology_models import (
    OWLClass, ValidationStatus, OntologyMetadata,
    MechatronicSystem, Subsystem, Component, SparePart
)

class ValidationAction(Enum):
    """Types of validation actions"""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_REVISION = "request_revision"
    UPDATE_CONFIDENCE = "update_confidence"
    EDIT_PROPERTIES = "edit_properties"
    ADD_COMMENT = "add_comment"

class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class ValidationIssue:
    """Represents a validation issue found in an entity"""
    issue_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: str = ""
    issue_type: str = ""  # missing_field, invalid_format, low_confidence, etc.
    severity: ValidationSeverity = ValidationSeverity.MEDIUM
    message: str = ""
    field_name: Optional[str] = None
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False
    created_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ValidationResult:
    """Result of entity validation"""
    entity_id: str
    is_valid: bool
    confidence_score: float
    issues: List[ValidationIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ExpertReview:
    """Expert review record with audit trail"""
    review_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: str = ""
    expert_id: str = ""
    action: ValidationAction = ValidationAction.ADD_COMMENT
    previous_status: ValidationStatus = ValidationStatus.NOT_VALIDATED
    new_status: ValidationStatus = ValidationStatus.NOT_VALIDATED
    comment: str = ""
    confidence_override: Optional[float] = None
    field_changes: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None

class EntityValidator:
    """Handles entity validation workflow and expert reviews"""
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.expert_reviews: List[ExpertReview] = []
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules for different entity types"""
        return {
            "system": {
                "required_fields": ["label", "system_type", "manufacturer"],
                "min_confidence": 0.7,
                "label_min_length": 3,
                "description_min_length": 10
            },
            "subsystem": {
                "required_fields": ["label", "subsystem_type", "parent_system_id"],
                "min_confidence": 0.6,
                "label_min_length": 3,
                "description_min_length": 10
            },
            "component": {
                "required_fields": ["label", "component_type", "parent_subsystem_id"],
                "min_confidence": 0.6,
                "label_min_length": 2,
                "part_number_format": r"^[A-Z0-9\-]+$"
            },
            "spare_part": {
                "required_fields": ["label", "parent_component_id", "part_number"],
                "min_confidence": 0.5,
                "label_min_length": 2,
                "part_number_format": r"^[A-Z0-9\-]+$"
            }
        }
    
    def validate_entity(self, entity: OWLClass, entity_type: str) -> ValidationResult:
        """Perform comprehensive validation of an entity"""
        
        issues = []
        recommendations = []
        
        # Get validation rules for entity type
        rules = self.validation_rules.get(entity_type, {})
        
        # Check required fields
        required_fields = rules.get("required_fields", [])
        for field in required_fields:
            if not hasattr(entity, field) or not getattr(entity, field):
                issues.append(ValidationIssue(
                    entity_id=entity.id,
                    issue_type="missing_required_field",
                    severity=ValidationSeverity.HIGH,
                    message=f"Required field '{field}' is missing or empty",
                    field_name=field,
                    suggested_fix=f"Please provide a value for {field}",
                    auto_fixable=False
                ))
        
        # Check confidence score
        min_confidence = rules.get("min_confidence", 0.5)
        if entity.metadata.confidence_score < min_confidence:
            issues.append(ValidationIssue(
                entity_id=entity.id,
                issue_type="low_confidence",
                severity=ValidationSeverity.MEDIUM,
                message=f"Confidence score {entity.metadata.confidence_score:.2f} is below threshold {min_confidence}",
                suggested_fix="Review and verify entity information",
                auto_fixable=False
            ))
        
        # Check label length
        min_label_length = rules.get("label_min_length", 2)
        if len(entity.label) < min_label_length:
            issues.append(ValidationIssue(
                entity_id=entity.id,
                issue_type="invalid_label_length",
                severity=ValidationSeverity.MEDIUM,
                message=f"Label is too short (minimum {min_label_length} characters)",
                field_name="label",
                suggested_fix="Provide a more descriptive label",
                auto_fixable=False
            ))
        
        # Check description length
        min_desc_length = rules.get("description_min_length", 0)
        if min_desc_length > 0 and len(entity.description) < min_desc_length:
            issues.append(ValidationIssue(
                entity_id=entity.id,
                issue_type="insufficient_description",
                severity=ValidationSeverity.LOW,
                message=f"Description is too short (minimum {min_desc_length} characters)",
                field_name="description",
                suggested_fix="Provide a more detailed description",
                auto_fixable=False
            ))
        
        # Entity-specific validations
        if entity_type == "component" and hasattr(entity, 'part_number'):
            part_number_format = rules.get("part_number_format")
            if part_number_format and entity.part_number:
                import re
                if not re.match(part_number_format, entity.part_number):
                    issues.append(ValidationIssue(
                        entity_id=entity.id,
                        issue_type="invalid_part_number_format",
                        severity=ValidationSeverity.MEDIUM,
                        message="Part number format is invalid",
                        field_name="part_number",
                        suggested_fix="Use format: letters, numbers, and hyphens only",
                        auto_fixable=False
                    ))
        
        # Generate recommendations
        if entity.metadata.validation_status == ValidationStatus.NOT_VALIDATED:
            recommendations.append("This entity has not been reviewed by an expert")
        
        if len(issues) == 0:
            recommendations.append("Entity passes all validation checks")
        elif len([i for i in issues if i.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]]) == 0:
            recommendations.append("Entity has minor issues that should be addressed")
        else:
            recommendations.append("Entity has critical issues that must be resolved")
        
        # Calculate overall validity
        critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
        is_valid = len(critical_issues) == 0
        
        return ValidationResult(
            entity_id=entity.id,
            is_valid=is_valid,
            confidence_score=entity.metadata.confidence_score,
            issues=issues,
            recommendations=recommendations
        )
    
    def submit_expert_review(
        self,
        entity_id: str,
        expert_id: str,
        action: ValidationAction,
        comment: str,
        new_status: Optional[ValidationStatus] = None,
        confidence_override: Optional[float] = None,
        field_changes: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> ExpertReview:
        """Submit an expert review for an entity"""
        
        # Create review record
        review = ExpertReview(
            entity_id=entity_id,
            expert_id=expert_id,
            action=action,
            comment=comment,
            confidence_override=confidence_override,
            field_changes=field_changes or {},
            session_id=session_id
        )
        
        # Set status based on action if not explicitly provided
        if new_status:
            review.new_status = new_status
        else:
            status_mapping = {
                ValidationAction.APPROVE: ValidationStatus.EXPERT_APPROVED,
                ValidationAction.REJECT: ValidationStatus.EXPERT_REJECTED,
                ValidationAction.REQUEST_REVISION: ValidationStatus.NEEDS_REVISION,
                ValidationAction.UPDATE_CONFIDENCE: ValidationStatus.PENDING_REVIEW,
                ValidationAction.EDIT_PROPERTIES: ValidationStatus.PENDING_REVIEW,
                ValidationAction.ADD_COMMENT: ValidationStatus.PENDING_REVIEW
            }
            review.new_status = status_mapping.get(action, ValidationStatus.PENDING_REVIEW)
        
        # Store review
        self.expert_reviews.append(review)
        
        return review
    
    def get_entity_review_history(self, entity_id: str) -> List[ExpertReview]:
        """Get review history for an entity"""
        return [review for review in self.expert_reviews if review.entity_id == entity_id]
    
    def get_expert_review_summary(self, expert_id: str) -> Dict[str, Any]:
        """Get summary of reviews by an expert"""
        expert_reviews = [r for r in self.expert_reviews if r.expert_id == expert_id]
        
        action_counts = {}
        for action in ValidationAction:
            action_counts[action.value] = len([r for r in expert_reviews if r.action == action])
        
        return {
            "expert_id": expert_id,
            "total_reviews": len(expert_reviews),
            "action_breakdown": action_counts,
            "entities_reviewed": len(set(r.entity_id for r in expert_reviews)),
            "last_review": max([r.timestamp for r in expert_reviews]) if expert_reviews else None
        }
    
    def get_validation_queue(
        self,
        priority_order: List[ValidationStatus] = None,
        confidence_threshold: float = 0.8
    ) -> List[Tuple[str, float, ValidationStatus]]:
        """Get prioritized queue of entities needing validation"""
        
        if priority_order is None:
            priority_order = [
                ValidationStatus.NOT_VALIDATED,
                ValidationStatus.NEEDS_REVISION,
                ValidationStatus.PENDING_REVIEW
            ]
        
        # This would typically query the database
        # For now, return empty list as placeholder
        return []
    
    def auto_fix_issues(self, entity: OWLClass, issues: List[ValidationIssue]) -> Dict[str, Any]:
        """Automatically fix issues that can be auto-fixed"""
        
        fixes_applied = {}
        
        for issue in issues:
            if not issue.auto_fixable:
                continue
            
            if issue.issue_type == "normalize_part_number":
                # Example auto-fix: normalize part number format
                if hasattr(entity, 'part_number') and entity.part_number:
                    original = entity.part_number
                    normalized = entity.part_number.upper().replace(' ', '-')
                    entity.part_number = normalized
                    fixes_applied[issue.field_name] = {
                        "original": original,
                        "fixed": normalized,
                        "issue_id": issue.issue_id
                    }
        
        return fixes_applied
    
    def generate_validation_report(
        self,
        entities: List[Tuple[OWLClass, str]],
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        results = []
        summary = {
            "total_entities": len(entities),
            "valid_entities": 0,
            "entities_with_issues": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
            "average_confidence": 0.0
        }
        
        total_confidence = 0.0
        
        for entity, entity_type in entities:
            result = self.validate_entity(entity, entity_type)
            results.append(result)
            
            if result.is_valid:
                summary["valid_entities"] += 1
            else:
                summary["entities_with_issues"] += 1
            
            # Count issues by severity
            for issue in result.issues:
                if issue.severity == ValidationSeverity.CRITICAL:
                    summary["critical_issues"] += 1
                elif issue.severity == ValidationSeverity.HIGH:
                    summary["high_issues"] += 1
                elif issue.severity == ValidationSeverity.MEDIUM:
                    summary["medium_issues"] += 1
                elif issue.severity == ValidationSeverity.LOW:
                    summary["low_issues"] += 1
            
            total_confidence += result.confidence_score
        
        if len(entities) > 0:
            summary["average_confidence"] = total_confidence / len(entities)
        
        report = {
            "summary": summary,
            "validation_results": [result.__dict__ for result in results],
            "generated_timestamp": datetime.now().isoformat()
        }
        
        if include_recommendations:
            report["recommendations"] = self._generate_global_recommendations(results)
        
        return report
    
    def _generate_global_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """Generate global recommendations based on validation results"""
        
        recommendations = []
        
        total_entities = len(results)
        entities_with_issues = len([r for r in results if not r.is_valid])
        
        if entities_with_issues > total_entities * 0.5:
            recommendations.append(
                "More than 50% of entities have validation issues. "
                "Consider reviewing extraction and processing procedures."
            )
        
        low_confidence_entities = len([r for r in results if r.confidence_score < 0.6])
        if low_confidence_entities > total_entities * 0.3:
            recommendations.append(
                "Many entities have low confidence scores. "
                "Consider improving AI extraction models or adding more training data."
            )
        
        critical_issues = sum(len([i for i in r.issues if i.severity == ValidationSeverity.CRITICAL]) 
                            for r in results)
        if critical_issues > 0:
            recommendations.append(
                f"Found {critical_issues} critical issues that must be addressed before approval."
            )
        
        return recommendations


# Factory function for creating validator
def create_entity_validator() -> EntityValidator:
    """Create and configure entity validator"""
    return EntityValidator()


if __name__ == "__main__":
    # Test the entity validator
    from backend.models.ontology_models import create_component, ValidationStatus
    
    validator = create_entity_validator()
    
    # Create test component with issues
    test_component = create_component(
        label="X",  # Too short
        component_type="Motor",
        parent_subsystem_id="subsystem_123",
        part_number="invalid part number",  # Invalid format
        description=""  # Too short
    )
    test_component.metadata.confidence_score = 0.4  # Low confidence
    
    # Validate entity
    result = validator.validate_entity(test_component, "component")
    
    print(f"Validation Result for {test_component.id}:")
    print(f"  Valid: {result.is_valid}")
    print(f"  Confidence: {result.confidence_score}")
    print(f"  Issues: {len(result.issues)}")
    
    for issue in result.issues:
        print(f"    - {issue.severity.value.upper()}: {issue.message}")
    
    print(f"  Recommendations:")
    for rec in result.recommendations:
        print(f"    - {rec}")
    
    # Test expert review
    review = validator.submit_expert_review(
        entity_id=test_component.id,
        expert_id="expert_001",
        action=ValidationAction.REQUEST_REVISION,
        comment="Component needs better description and valid part number format"
    )
    
    print(f"\nExpert Review Submitted:")
    print(f"  Review ID: {review.review_id}")
    print(f"  Action: {review.action.value}")
    print(f"  New Status: {review.new_status.value}")
    
    print("\n✅ Entity validator test completed!")