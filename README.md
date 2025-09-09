# Medical Device Ontology Extraction System

## Mục Tiêu Chính
Xây dựng ontology từ service manual của thiết bị y tế với hệ thống **Human-in-the-Loop** để đảm bảo chất lượng và độ chính xác cao.

### 🎯 **Use Case Cụ Thể**
- **Target**: MLCi/MLCi2 Digital Linear Accelerator Service Manuals
- **AI Engine**: Google Gemini Flash cho entity extraction
- **Human Verification**: Chuyên gia y tế review và verify
- **Output**: Medical Device Ontology (OWL format)

### 🏥 **Domain Specific Features**

#### **1. Medical Device Entities**
```yaml
Error Codes:
  - Code: "7002"
  - Software Release: "R6.0x, R6.1x" 
  - Message: "MOVEMENT"
  - Description: "Actual direction of movement does not match expected"
  - Response: "Check drive to leaf motors"
  - Category: "Mechanical"
  - Severity: "High"

Components:
  - Name: "Leaf Motor"
  - Type: "Actuator"
  - Function: "Control leaf movement"
  - Parent System: "MLCi Control System"

Procedures:
  - Name: "Calibration Check"
  - Steps: ["Check calibration files", "Verify video line"]
  - Prerequisites: ["System powered", "Service mode"]
  - Safety Level: "Level 2"
```

#### **2. Human-in-the-Loop Workflow**
```
PDF Input → Gemini Flash → AI Extraction → Human Review → Verification → Ontology
    ↓           ↓             ↓             ↓            ↓           ↓
  Manual     Auto Extract   Entities    Expert Check   Approve    OWL Export
```

#### **3. Specialized Entity Types**
- **Error Codes**: Diagnostic information
- **Components**: Physical equipment parts  
- **Procedures**: Maintenance/troubleshooting steps
- **Specifications**: Technical parameters
- **Safety Protocols**: Warning and safety measures

## Kiến Trúc Hệ Thống

```
medical_device_ontology_system/
├── backend/
│   ├── ai_extraction/          # Gemini Flash integration
│   │   ├── gemini_client.py         # Google AI client
│   │   ├── prompt_templates.py      # Medical device prompts
│   │   └── entity_parser.py         # Parse AI responses
│   ├── core/
│   │   ├── pdf_processor.py         # PDF parsing
│   │   ├── medical_entity_extractor.py  # Medical-specific extraction
│   │   ├── ontology_builder.py      # OWL ontology construction
│   │   └── human_review_manager.py  # Human verification workflow
│   ├── models/
│   │   ├── medical_entities.py      # Medical entity models
│   │   ├── error_code.py           # Error code structure
│   │   ├── component.py            # Equipment component
│   │   └── procedure.py            # Procedure/workflow
│   └── verification/
│       ├── review_interface.py     # Human review UI
│       ├── confidence_scoring.py   # AI confidence analysis
│       └── expert_feedback.py     # Expert annotation system
├── frontend/
│   ├── review_dashboard/       # Expert review interface
│   ├── ontology_viewer/       # Ontology visualization
│   └── extraction_monitor/    # Real-time extraction progress
├── data/
│   ├── medical_manuals/       # Service manual PDFs
│   ├── extracted_entities/    # Raw AI extractions
│   ├── reviewed_data/         # Human-verified entities
│   ├── ontologies/           # Generated OWL files
│   └── knowledge_graphs/     # Visual graph representations
└── domain_knowledge/
    ├── medical_vocabularies/  # Medical terminology
    ├── device_taxonomies/     # Equipment classifications
    └── safety_standards/      # Medical device standards
```

## Công Nghệ Stack

### **AI & NLP**
- **Google Gemini Flash**: Primary entity extraction
- **spaCy**: Text preprocessing và NER backup
- **Transformers**: Domain-specific fine-tuning capabilities

### **Ontology & Knowledge Graph**
- **owlready2**: OWL ontology manipulation
- **rdflib**: RDF graph operations
- **SPARQL**: Ontology querying
- **Protégé compatibility**: Standard ontology format

### **Human Review Interface**
- **FastAPI**: Backend API
- **React/Vue**: Interactive review dashboard
- **D3.js**: Ontology visualization
- **Annotation tools**: Entity marking interface

### **Medical Domain Support**
- **UMLS integration**: Medical terminology mapping
- **IEC 60601**: Medical device safety standards
- **HL7 FHIR**: Healthcare data interoperability

## Workflow Chi Tiết

### **Phase 1: AI-Powered Extraction**
```python
# 1. PDF Processing
pages = pdf_processor.extract_pages(manual_pdf)

# 2. Gemini Flash Extraction
for page in pages:
    entities = gemini_client.extract_medical_entities(
        page_content=page,
        domain="medical_device",
        device_type="linear_accelerator"
    )
    
# 3. Entity Structuring
structured_entities = entity_parser.parse_gemini_response(entities)
```

### **Phase 2: Human Review**
```python  
# 1. Present to Expert
review_session = review_manager.create_session(extracted_entities)

# 2. Expert Annotations
expert_feedback = review_interface.collect_annotations(
    entities=structured_entities,
    expert_id="medical_engineer_001"
)

# 3. Quality Scoring
confidence_scores = confidence_scorer.evaluate_extractions(
    ai_entities=structured_entities,
    expert_feedback=expert_feedback
)
```

### **Phase 3: Ontology Construction**
```python
# 1. Build OWL Ontology
ontology = ontology_builder.create_medical_device_ontology(
    verified_entities=expert_verified_entities,
    domain_vocabulary=medical_vocabularies
)

# 2. Add Relationships
ontology_builder.add_relationships(
    error_codes_to_components=error_component_mappings,
    procedures_to_safety=safety_procedure_links
)

# 3. Export Standard Formats
ontology.save("mlci_device_ontology.owl")
knowledge_graph.export("mlci_knowledge_graph.rdf")
```

## Medical Device Entity Schema

```yaml
ErrorCode:
  properties:
    - code: String (required)
    - software_release: String
    - message: String
    - description: String  
    - response_action: String
    - category: Enum[Mechanical, Electrical, Software, Safety]
    - severity: Enum[Low, Medium, High, Critical]
    - related_components: List[Component]

Component:
  properties:
    - name: String (required)
    - type: Enum[Sensor, Actuator, Controller, Display]
    - function: String
    - parent_system: String
    - specifications: Dict
    - maintenance_procedures: List[Procedure]

Procedure:
  properties:
    - name: String (required)
    - type: Enum[Calibration, Diagnosis, Repair, Safety_Check]
    - steps: List[String]
    - prerequisites: List[String]
    - tools_required: List[String]
    - safety_level: Enum[Level_1, Level_2, Level_3]
    - estimated_time: Integer (minutes)

SafetyProtocol:
  properties:
    - name: String (required)
    - type: Enum[Warning, Caution, Danger]
    - description: String
    - applicable_procedures: List[Procedure]
    - compliance_standard: String (e.g., IEC 60601)
```

## Human Review Interface Features

### **1. Entity Verification Dashboard**
- ✅ **Approve** correct extractions
- ✏️ **Edit** incorrect information  
- ❌ **Reject** invalid entities
- 🔗 **Link** relationships between entities
- 📝 **Annotate** additional context

### **2. Confidence Visualization**
- 🟢 **High Confidence** (>90%): Auto-approve candidates
- 🟡 **Medium Confidence** (70-90%): Review recommended  
- 🔴 **Low Confidence** (<70%): Manual verification required

### **3. Domain Expert Tools**
- 📚 **Medical Dictionary** integration
- 🔍 **Similar Entity** suggestions
- 📋 **Checklist** for completeness verification
- 📊 **Progress Tracking** for large manuals

## API Endpoints

```
POST   /extract/gemini           # Gemini Flash extraction
GET    /entities/pending         # Entities awaiting review
PUT    /entities/{id}/verify     # Expert verification
POST   /ontology/build          # Generate OWL ontology
GET    /review/dashboard        # Human review interface
POST   /feedback/expert         # Expert annotation submission
```

## Validation & Quality Metrics

```python
Quality Metrics:
- extraction_accuracy: float      # AI vs Expert agreement
- ontology_completeness: float    # Coverage of manual content
- expert_confidence: float        # Human reviewer confidence
- relationship_consistency: float # Logical consistency
- domain_compliance: float        # Medical standard adherence

Success Criteria:
- >95% accuracy on error codes
- >90% accuracy on components  
- >85% accuracy on procedures
- 100% expert review completion
- Full OWL ontology generation
```

## Deployment & Integration

### **Production Environment**
```yaml
AI Service:
  - Google Cloud AI Platform
  - Gemini Flash API integration
  - Rate limiting & cost management

Review Platform:
  - Web-based expert interface
  - Multi-expert collaboration
  - Version control for ontologies

Output Integration:
  - Hospital CMMS systems
  - Technical documentation
  - Training material generation
  - Regulatory compliance reports
```

Bạn có muốn tôi bắt đầu implement từ **Gemini Flash integration** trước không? Đây sẽ là core component cho việc trích xuất entities từ medical device manual.
