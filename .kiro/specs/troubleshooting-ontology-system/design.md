# Design Document - Troubleshooting Ontology System

## Overview

Troubleshooting Ontology System được thiết kế để tạo ra một comprehensive knowledge base từ service manual và schematic diagrams của thiết bị y tế, đặc biệt tập trung vào hệ thống LINAC (Linear Accelerator). Hệ thống sử dụng AI-powered extraction kết hợp với expert validation để đảm bảo accuracy và completeness của ontology.

Hệ thống mở rộng từ codebase hiện tại và bổ sung khả năng xử lý schematic diagrams, tạo ra một unified knowledge graph có cấu trúc phân cấp từ System → Subsystem → Component → SparePart.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Troubleshooting Ontology System              │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Layer                                                 │
│  ├── Expert Review Dashboard                                    │
│  ├── Ontology Visualization                                     │
│  └── Schematic Annotation Interface                             │
├─────────────────────────────────────────────────────────────────┤
│  API Layer                                                      │
│  ├── Service Manual Processing API                              │
│  ├── Schematic Processing API                                   │
│  ├── Ontology Management API                                    │
│  └── Expert Review API                                          │
├─────────────────────────────────────────────────────────────────┤
│  Processing Layer                                               │
│  ├── Enhanced Medical Entity Extractor                          │
│  ├── Schematic Component Recognition Engine                      │
│  ├── Ontology Builder & Relationship Mapper                     │
│  └── Multi-Modal Data Integration Engine                        │
├─────────────────────────────────────────────────────────────────┤
│  AI & ML Layer                                                  │
│  ├── Gemini Flash (Service Manual Processing)                   │
│  ├── Computer Vision Models (Schematic Analysis)                │
│  ├── OCR Engine (Text Recognition)                              │
│  └── Relationship Inference Engine                              │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                     │
│  ├── Ontology Store (OWL/RDF)                                   │
│  ├── Knowledge Graph Database                                   │
│  ├── Document Repository                                        │
│  └── Expert Review Database                                     │
└─────────────────────────────────────────────────────────────────┘
```

### System Integration with Existing Codebase

```
Existing Medical Device System
├── backend/ai_extraction/          # ENHANCED
│   ├── gemini_client.py           # Extended for ontology concepts
│   ├── prompt_templates.py        # Added subsystem/component prompts
│   ├── entity_parser.py           # Enhanced for hierarchical entities
│   └── schematic_processor.py     # NEW - Schematic analysis
├── backend/core/
│   ├── pdf_processor.py           # Extended for schematics
│   ├── ontology_builder.py        # NEW - OWL ontology construction
│   └── relationship_mapper.py     # NEW - Entity relationship mapping
├── backend/models/
│   ├── entity.py                  # Extended with subsystem models
│   ├── ontology_models.py         # NEW - OWL/RDF models
│   └── schematic_models.py        # NEW - Schematic component models
└── backend/verification/
    ├── expert_review.py           # Enhanced for ontology validation
    └── ontology_validator.py      # NEW - Ontology consistency checker
```

## Components and Interfaces

### 1. Enhanced Medical Entity Extractor

**Purpose**: Mở rộng từ hệ thống hiện tại để trích xuất hierarchical entities và relationships

**Key Components**:
- `HierarchicalEntityExtractor`: Trích xuất System → Subsystem → Component hierarchy
- `RelationshipDetector`: Phát hiện relationships giữa entities
- `OntologyConceptMapper`: Map entities với medical device ontology concepts

**Interface**:
```python
class HierarchicalEntityExtractor:
    async def extract_hierarchical_entities(
        self, 
        content: str, 
        device_type: str = "linac"
    ) -> HierarchicalEntityResult
    
    def map_to_ontology_concepts(
        self, 
        entities: List[Entity]
    ) -> List[OntologyConcept]
    
    def detect_relationships(
        self, 
        entities: List[Entity]
    ) -> List[EntityRelationship]
```

### 2. Schematic Component Recognition Engine

**Purpose**: Phân tích schematic diagrams để trích xuất components, connections, và spatial relationships

**Key Components**:
- `SchematicImageProcessor`: Xử lý schematic images/PDFs
- `ComponentSymbolRecognizer`: Nhận diện electrical/mechanical symbols
- `ConnectionTracer`: Trace connections giữa components
- `TextExtractor`: OCR cho labels và part numbers

**Interface**:
```python
class SchematicProcessor:
    def process_schematic(
        self, 
        schematic_file: str
    ) -> SchematicAnalysisResult
    
    def recognize_components(
        self, 
        image: np.ndarray
    ) -> List[SchematicComponent]
    
    def trace_connections(
        self, 
        components: List[SchematicComponent]
    ) -> List[ComponentConnection]
    
    def extract_text_labels(
        self, 
        image: np.ndarray
    ) -> List[TextLabel]
```

### 3. Ontology Builder & Relationship Mapper

**Purpose**: Tạo và quản lý OWL ontology từ extracted entities và relationships

**Key Components**:
- `OWLOntologyBuilder`: Tạo OWL ontology structure
- `RelationshipMapper`: Map relationships giữa entities
- `HierarchyBuilder`: Xây dựng class hierarchy
- `InstanceCreator`: Tạo instances từ extracted data

**Interface**:
```python
class OntologyBuilder:
    def create_linac_ontology(
        self, 
        entities: List[Entity], 
        relationships: List[Relationship]
    ) -> OWLOntology
    
    def add_subsystem_hierarchy(
        self, 
        ontology: OWLOntology, 
        subsystems: List[Subsystem]
    ) -> None
    
    def validate_ontology_consistency(
        self, 
        ontology: OWLOntology
    ) -> ValidationResult
```

### 4. Expert Review Interface

**Purpose**: Interface cho experts review và validate extracted ontology

**Key Components**:
- `OntologyReviewDashboard`: Web interface cho ontology review
- `EntityValidationInterface`: Validate individual entities
- `RelationshipEditor`: Edit và approve relationships
- `ConflictResolver`: Resolve conflicts giữa multiple experts

**Interface**:
```python
class ExpertReviewManager:
    def create_review_session(
        self, 
        ontology: OWLOntology, 
        expert_id: str
    ) -> ReviewSession
    
    def submit_entity_feedback(
        self, 
        entity_id: str, 
        feedback: EntityFeedback
    ) -> None
    
    def resolve_conflicts(
        self, 
        conflicting_reviews: List[Review]
    ) -> ConflictResolution
```

## Data Models

### Ontology Structure

```python
# Core Ontology Classes
class MechatronicSystem(OWLClass):
    """Top-level system (e.g., LINAC_001)"""
    has_subsystem: List[Subsystem]
    has_function: List[SystemFunction]
    has_status: SystemStatus
    used_for: List[MedicalApplication]

class Subsystem(OWLClass):
    """Functional subsystem (e.g., BeamDeliverySystem)"""
    has_component: List[Component]
    has_control_unit: List[ControlUnit]
    part_of_system: MechatronicSystem
    has_function: List[SubsystemFunction]

class Component(OWLClass):
    """Individual component (e.g., MLC, ServoMotor)"""
    part_of_subsystem: Subsystem
    has_spare_part: List[SparePart]
    monitored_by: List[Sensor]
    controlled_by: List[Controller]
    has_specifications: TechnicalSpecification

class SparePart(OWLClass):
    """Replaceable parts"""
    part_number: str
    maintenance_cycle: str
    used_by: Component
    supplier: str
    lifecycle_status: str

# Relationships
class EntityRelationship(OWLObjectProperty):
    """Base class for all relationships"""
    source_entity: Entity
    target_entity: Entity
    relationship_type: RelationshipType
    confidence: float
    validated_by_expert: bool

# Specific Relationship Types
class CausalRelationship(EntityRelationship):
    """Error causes component failure"""
    pass

class PartOfRelationship(EntityRelationship):
    """Component is part of subsystem"""
    pass

class RequiresRelationship(EntityRelationship):
    """Procedure requires component"""
    pass
```

### Schematic Data Models

```python
class SchematicDocument:
    """Represents a schematic document"""
    document_id: str
    file_path: str
    pages: List[SchematicPage]
    document_type: str  # electrical, mechanical, hydraulic
    device_system: str  # linac, ct_scanner, etc.

class SchematicPage:
    """Single page of schematic"""
    page_number: int
    image_data: np.ndarray
    components: List[SchematicComponent]
    connections: List[ComponentConnection]
    text_labels: List[TextLabel]
    spatial_layout: SpatialLayout

class SchematicComponent:
    """Component identified in schematic"""
    component_id: str
    symbol_type: str  # resistor, motor, sensor, etc.
    bounding_box: BoundingBox
    part_number: Optional[str]
    component_value: Optional[str]  # resistance, voltage, etc.
    connections: List[ConnectionPoint]
    
class ComponentConnection:
    """Connection between components"""
    connection_id: str
    source_component: str
    target_component: str
    connection_type: str  # wire, pipe, mechanical
    signal_type: Optional[str]  # power, data, control
```

### Integration Models

```python
class IntegratedKnowledgeGraph:
    """Unified knowledge from manual + schematic"""
    ontology: OWLOntology
    schematic_data: List[SchematicDocument]
    entity_mappings: List[EntityMapping]
    validation_status: ValidationStatus

class EntityMapping:
    """Maps manual entities to schematic components"""
    manual_entity_id: str
    schematic_component_id: str
    mapping_confidence: float
    mapping_type: str  # exact_match, partial_match, inferred
    validated_by_expert: bool

class ValidationStatus:
    """Overall validation status"""
    total_entities: int
    validated_entities: int
    pending_review: int
    expert_approved: int
    confidence_distribution: Dict[str, int]
```

## Error Handling

### Error Categories

1. **Document Processing Errors**
   - PDF corruption or unreadable files
   - Schematic image quality issues
   - OCR failures

2. **AI Processing Errors**
   - Gemini API failures or rate limits
   - Computer vision model failures
   - Low confidence extractions

3. **Ontology Construction Errors**
   - Inconsistent relationships
   - Circular dependencies
   - Missing required properties

4. **Expert Review Errors**
   - Conflicting expert opinions
   - Incomplete reviews
   - System unavailability during review

### Error Handling Strategy

```python
class ErrorHandler:
    def handle_processing_error(
        self, 
        error: ProcessingError, 
        context: ProcessingContext
    ) -> ErrorResolution:
        """
        - Retry with different parameters
        - Fallback to alternative processing method
        - Queue for manual intervention
        - Log for analysis and improvement
        """
        
    def handle_validation_error(
        self, 
        error: ValidationError, 
        ontology: OWLOntology
    ) -> ValidationFix:
        """
        - Suggest automatic fixes
        - Flag for expert review
        - Provide conflict resolution options
        """
```

## Testing Strategy

### Unit Testing
- Individual component extraction accuracy
- Relationship detection precision/recall
- Ontology consistency validation
- Schematic component recognition accuracy

### Integration Testing
- End-to-end pipeline from PDF to OWL
- Multi-modal data integration
- Expert review workflow
- API endpoint functionality

### Performance Testing
- Large document processing (>100MB PDFs)
- Complex schematic analysis (>1000 components)
- Concurrent user sessions
- Database query performance

### Domain Testing
- Medical device terminology accuracy
- LINAC-specific entity recognition
- Safety protocol extraction
- Technical specification parsing

### Test Data Requirements
- Sample LINAC service manuals
- Schematic diagrams (electrical, mechanical)
- Expert-validated ground truth data
- Performance benchmark datasets

## Security and Compliance

### Data Security
- Encrypted storage for sensitive medical device information
- Access control for expert review interfaces
- Audit logging for all ontology modifications
- Secure API authentication and authorization

### Medical Device Compliance
- Alignment with IEC 60601 standards
- UMLS and SNOMED CT terminology mapping
- HL7 FHIR compatibility for healthcare integration
- FDA medical device software guidelines compliance

### Privacy Protection
- Anonymization of device-specific information
- Secure handling of proprietary technical data
- GDPR compliance for expert user data
- Data retention and deletion policies

## Deployment Architecture

### Development Environment
```yaml
Services:
  - api_server: FastAPI application
  - ontology_db: Apache Jena Fuseki (RDF store)
  - document_store: MinIO (S3-compatible)
  - cache_layer: Redis
  - task_queue: Celery with Redis broker
  - monitoring: Prometheus + Grafana
```

### Production Environment
```yaml
Infrastructure:
  - Container orchestration: Kubernetes
  - Load balancer: NGINX Ingress
  - Database: PostgreSQL + Apache Jena
  - File storage: AWS S3 or Azure Blob
  - Monitoring: ELK Stack + Prometheus
  - Backup: Automated daily snapshots
```

### Scalability Considerations
- Horizontal scaling for API services
- Distributed processing for large documents
- Caching strategies for frequently accessed ontologies
- Database sharding for large knowledge graphs
- CDN for static assets and documentation