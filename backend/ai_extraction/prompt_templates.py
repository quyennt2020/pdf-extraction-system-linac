"""
Specialized prompt templates for medical device entity extraction using Gemini Flash
"""

from typing import List, Dict, Any
import json


class MedicalDevicePrompts:
    """
    Prompt templates optimized for extracting entities from medical device service manuals
    """
    
    def __init__(self):
        """Initialize prompt templates"""
        
        # Medical device entity definitions - Enhanced for hierarchical ontology
        self.entity_definitions = {
            "error_codes": {
                "description": "Diagnostic codes indicating system faults or warnings",
                "fields": ["code", "software_release", "message", "description", "response", "category", "severity"],
                "examples": ["7002", "7001", "0000"]
            },
            "systems": {
                "description": "Top-level medical device systems (e.g., LINAC_001, CT_Scanner_A)",
                "fields": ["name", "type", "model", "manufacturer", "primary_function", "subsystems", "status"],
                "examples": ["LINAC System", "Beam Delivery System", "Patient Positioning System"]
            },
            "subsystems": {
                "description": "Functional subsystems within medical devices",
                "fields": ["name", "type", "parent_system", "components", "function", "control_method", "interfaces"],
                "examples": ["Beam Delivery System", "Patient Positioning System", "MLC Control System"]
            },
            "components": {
                "description": "Individual components within subsystems",
                "fields": ["name", "type", "function", "parent_subsystem", "specifications", "spare_parts", "maintenance_cycle"],
                "examples": ["Leaf Motor", "MLC Controller", "Beam Monitor", "Servo Motor"]
            },
            "spare_parts": {
                "description": "Replaceable parts for components",
                "fields": ["part_number", "name", "component", "supplier", "lifecycle_status", "maintenance_cycle", "specifications"],
                "examples": ["Motor Assembly P/N 12345", "Sensor Board P/N 67890"]
            },
            "relationships": {
                "description": "Relationships between entities (causal, spatial, functional, temporal)",
                "fields": ["source_entity", "target_entity", "relationship_type", "description", "confidence"],
                "examples": ["Motor controls Leaf", "Error causes Component failure", "Subsystem part_of System"]
            },
            "procedures": {
                "description": "Maintenance, calibration, and troubleshooting procedures",
                "fields": ["name", "type", "steps", "prerequisites", "tools_required", "safety_level", "estimated_time"],
                "examples": ["Calibration Check", "Motor Alignment", "Safety Interlock Test"]
            },
            "safety_protocols": {
                "description": "Safety warnings, cautions, and danger notices",
                "fields": ["type", "title", "description", "applicable_procedures", "compliance_standard"],
                "examples": ["WARNING", "CAUTION", "DANGER"]
            },
            "technical_specifications": {
                "description": "Technical parameters, limits, and measurements",
                "fields": ["parameter", "value", "unit", "tolerance", "measurement_method"],
                "examples": ["Voltage: 220V ±5%", "Temperature: 20-25°C"]
            }
        }
        
        # Device-specific vocabularies with hierarchical structure
        self.device_vocabularies = {
            "linear_accelerator": [
                "MLC", "MLCi", "MLCi2", "leaf", "collimator", "gantry", "couch", 
                "beam", "monitor", "chamber", "detector", "dose", "treatment",
                "radiation", "linac", "electron", "photon", "energy", "field"
            ],
            "ct_scanner": [
                "gantry", "detector", "tube", "collimator", "table", "patient",
                "scan", "reconstruction", "slice", "helical", "axial", "contrast"
            ],
            "mri_scanner": [
                "magnet", "coil", "gradient", "RF", "sequence", "bore", "table",
                "shimming", "quench", "cryogen", "helium", "field"
            ]
        }
        
        # LINAC subsystem hierarchy for specialized extraction
        self.linac_subsystems = {
            "BeamDeliverySystem": {
                "description": "Controls and delivers therapeutic radiation beam",
                "components": ["Electron Gun", "Accelerating Waveguide", "Bending Magnet", "Target", "Flattening Filter", "Primary Collimator"],
                "functions": ["beam_generation", "beam_shaping", "dose_delivery"]
            },
            "PatientPositioningSystem": {
                "description": "Positions and immobilizes patient for treatment",
                "components": ["Treatment Couch", "Couch Drive Motors", "Position Sensors", "Immobilization Devices"],
                "functions": ["patient_positioning", "position_verification", "motion_monitoring"]
            },
            "MLCSystem": {
                "description": "Multi-Leaf Collimator for beam shaping",
                "components": ["Leaf Motors", "Leaf Position Sensors", "MLC Controller", "Leaf Assemblies"],
                "functions": ["beam_shaping", "field_modulation", "dose_conformity"]
            },
            "GantrySystem": {
                "description": "Rotates treatment head around patient",
                "components": ["Gantry Drive Motor", "Gantry Position Sensors", "Slip Ring Assembly", "Counterweight"],
                "functions": ["angular_positioning", "rotation_control", "mechanical_stability"]
            },
            "ImagingSystem": {
                "description": "Provides imaging for treatment verification",
                "components": ["kV Imaging System", "MV Portal Imaging", "CBCT System", "Image Detectors"],
                "functions": ["patient_verification", "treatment_monitoring", "quality_assurance"]
            },
            "SafetySystem": {
                "description": "Ensures safe operation and radiation protection",
                "components": ["Safety Interlocks", "Radiation Monitors", "Emergency Stops", "Access Control"],
                "functions": ["radiation_safety", "personnel_protection", "system_monitoring"]
            },
            "ControlSystem": {
                "description": "Central control and coordination of all subsystems",
                "components": ["Main Controller", "User Interface", "Network Interface", "Data Storage"],
                "functions": ["system_coordination", "user_interface", "data_management"]
            }
        }
        
        # Relationship types for medical device ontology
        self.relationship_types = {
            "causal": ["causes", "triggers", "results_in", "leads_to", "prevents"],
            "spatial": ["part_of", "contains", "adjacent_to", "connected_to", "located_in"],
            "functional": ["controls", "monitors", "regulates", "operates", "interfaces_with"],
            "temporal": ["precedes", "follows", "concurrent_with", "during", "after"],
            "dependency": ["requires", "depends_on", "enables", "supports", "affects"]
        }
    
    def build_extraction_prompt(
        self,
        page_content: str,
        device_type: str = "linear_accelerator",
        manual_type: str = "service_manual",
        extraction_focus: List[str] = None
    ) -> str:
        """
        Build comprehensive extraction prompt for medical device content
        """
        
        if not extraction_focus:
            extraction_focus = ["error_codes", "components", "procedures", "safety_protocols"]
        
        # Build main prompt
        prompt_parts = [
            self._get_system_instruction(device_type, manual_type),
            self._get_entity_definitions(extraction_focus),
            self._get_extraction_guidelines(device_type),
            self._get_output_format_instruction(extraction_focus),
            self._get_examples_section(device_type, extraction_focus),
            f"\n**CONTENT TO ANALYZE:**\n{page_content}\n",
            self._get_final_instruction(extraction_focus)
        ]
        
        return "\n\n".join(prompt_parts)
    
    def _get_system_instruction(self, device_type: str, manual_type: str) -> str:
        """Get system instruction based on device and manual type"""
        
        device_name = device_type.replace('_', ' ').title()
        
        return f"""
You are an expert medical device engineer specializing in {device_name} systems. 
Your task is to extract structured information from {manual_type} content with high accuracy.

**EXPERTISE AREAS:**
- Medical device maintenance and troubleshooting
- Error code analysis and interpretation  
- Component identification and relationships
- Safety protocol compliance
- Technical specification extraction

**QUALITY REQUIREMENTS:**
- High accuracy (>95% for error codes)
- Complete entity extraction
- Proper medical terminology usage
- Safety-first approach
- Structured JSON output
        """.strip()
    
    def _get_entity_definitions(self, extraction_focus: List[str]) -> str:
        """Get entity definitions for focused extraction"""
        
        definitions = []
        
        for entity_type in extraction_focus:
            if entity_type in self.entity_definitions:
                entity_def = self.entity_definitions[entity_type]
                
                definitions.append(f"""
**{entity_type.upper().replace('_', ' ')}:**
- Description: {entity_def['description']}
- Required Fields: {', '.join(entity_def['fields'])}
- Examples: {', '.join(entity_def['examples'])}
                """.strip())
        
        header = "**ENTITY TYPES TO EXTRACT:**"
        
        return header + "\n\n" + "\n\n".join(definitions)
    
    def _get_extraction_guidelines(self, device_type: str) -> str:
        """Get device-specific extraction guidelines"""
        
        vocab = self.device_vocabularies.get(device_type, [])
        vocab_text = ", ".join(vocab[:15]) + ("..." if len(vocab) > 15 else "")
        
        return f"""
**EXTRACTION GUIDELINES:**

1. **Error Codes:**
   - Look for 4-digit numeric codes ONLY when preceded by "Error", "Code", or followed by error descriptions
   - EXCLUDE document numbers, part numbers, and figure references (e.g., "4513 370 2102", "Figure 3.1")
   - Extract associated software releases (e.g., R6.0x, R7.0x)
   - Capture error messages in UPPERCASE format
   - Include detailed descriptions and response actions
   - Categorize by type: Mechanical, Electrical, Software, Safety

2. **Components:**
   - Identify physical parts and subsystems
   - Map parent-child relationships
   - Note component functions and specifications
   - Key vocabulary: {vocab_text}

3. **Procedures:**
   - Extract step-by-step instructions
   - Identify prerequisites and required tools
   - Note safety levels and time estimates
   - Categorize: Calibration, Diagnosis, Repair, Safety Check

4. **Safety Protocols:**
   - Distinguish WARNING, CAUTION, DANGER levels
   - Extract complete safety descriptions
   - Link to applicable procedures
   - Note compliance standards (e.g., IEC 60601)

5. **Technical Specifications:**
   - Extract numerical values with units
   - Include tolerances and ranges
   - Note measurement methods
   - Identify critical parameters
        """.strip()
    
    def _get_output_format_instruction(self, extraction_focus: List[str]) -> str:
        """Get output format instructions"""
        
        # Build JSON schema
        schema = {"type": "object", "properties": {}}
        
        for entity_type in extraction_focus:
            schema["properties"][entity_type] = {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": self._get_entity_schema(entity_type)
                }
            }
        
        return f"""
**OUTPUT FORMAT:**
Provide your response as a valid JSON object with the following structure:

```json
{json.dumps(schema, indent=2)}
```

**FIELD REQUIREMENTS:**
- All entities must include a "confidence" field (0.0 to 1.0)
- Use "unknown" for missing information, never leave fields empty
- Preserve exact text for codes and technical terms
- Use consistent formatting for similar entities
        """.strip()
    
    def _get_entity_schema(self, entity_type: str) -> Dict[str, Any]:
        """Get JSON schema for specific entity type"""
        
        base_schema = {"confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}}
        
        if entity_type == "error_codes":
            base_schema.update({
                "code": {"type": "string"},
                "software_release": {"type": "string"},
                "message": {"type": "string"},
                "description": {"type": "string"},
                "response": {"type": "string"},
                "category": {"type": "string", "enum": ["Mechanical", "Electrical", "Software", "Safety", "System"]},
                "severity": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]}
            })
        elif entity_type == "components":
            base_schema.update({
                "name": {"type": "string"},
                "type": {"type": "string"},
                "function": {"type": "string"},
                "parent_system": {"type": "string"},
                "specifications": {"type": "string"}
            })
        elif entity_type == "procedures":
            base_schema.update({
                "name": {"type": "string"},
                "type": {"type": "string", "enum": ["Calibration", "Diagnosis", "Repair", "Safety_Check", "Maintenance"]},
                "description": {"type": "string"},
                "steps": {"type": "array", "items": {"type": "string"}},
                "prerequisites": {"type": "array", "items": {"type": "string"}},
                "safety_level": {"type": "string", "enum": ["Level_1", "Level_2", "Level_3"]},
                "estimated_time": {"type": "string"}
            })
        elif entity_type == "safety_protocols":
            base_schema.update({
                "type": {"type": "string", "enum": ["WARNING", "CAUTION", "DANGER", "NOTE"]},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "applicable_procedures": {"type": "array", "items": {"type": "string"}},
                "compliance_standard": {"type": "string"}
            })
        elif entity_type == "technical_specifications":
            base_schema.update({
                "parameter": {"type": "string"},
                "value": {"type": "string"},
                "unit": {"type": "string"},
                "tolerance": {"type": "string"},
                "measurement_method": {"type": "string"}
            })
        
        return base_schema
    
    def _get_examples_section(self, device_type: str, extraction_focus: List[str]) -> str:
        """Get example extractions for the device type"""
        
        examples = []
        
        if "error_codes" in extraction_focus:
            examples.append("""
**ERROR CODE EXAMPLE:**
Input: "Error Code 7002: MOVEMENT The actual direction of movement of a leaf does not match the expected direction. Check the drive to the leaf motors."

Output:
```json
{
  "error_codes": [{
    "code": "7002",
    "software_release": "unknown",
    "message": "MOVEMENT",
    "description": "The actual direction of movement of a leaf does not match the expected direction",
    "response": "Check the drive to the leaf motors and the leaves for free movement",
    "category": "Mechanical",
    "severity": "High",
    "confidence": 0.95
  }]
}
```

**WHAT NOT TO EXTRACT AS ERROR CODES:**
- Document numbers: "4513 370 2102 03" 
- Figure references: "Figure 3.1 (4513 332 6702)"
- Part numbers: "P/N 12345-67"
- Page numbers: "Page 3-5"
            """.strip())
        
        if "components" in extraction_focus:
            examples.append("""
**COMPONENT EXAMPLE:**
Input: "The leaf motor assembly consists of stepper motors that control individual leaf positions in the MLC system."

Output:
```json
{
  "components": [{
    "name": "Leaf Motor Assembly",
    "type": "Actuator",
    "function": "Control individual leaf positions",
    "parent_system": "MLC System",
    "specifications": "Stepper motors",
    "confidence": 0.90
  }]
}
```
            """.strip())
        
        if "procedures" in extraction_focus:
            examples.append("""
**PROCEDURE EXAMPLE:**
Input: "Calibration Check: 1. Check calibration files are present 2. Verify video line calibration 3. Confirm correct spacing"

Output:
```json
{
  "procedures": [{
    "name": "Calibration Check",
    "type": "Calibration",
    "description": "Verify system calibration status",
    "steps": [
      "Check calibration files are present",
      "Verify video line calibration", 
      "Confirm correct spacing"
    ],
    "prerequisites": ["System powered", "Service mode access"],
    "safety_level": "Level_2",
    "estimated_time": "15 minutes",
    "confidence": 0.88
  }]
}
```
            """.strip())
        
        if not examples:
            return ""
        
        header = "**EXTRACTION EXAMPLES:**"
        return header + "\n\n" + "\n\n".join(examples)
    
    def _get_final_instruction(self, extraction_focus: List[str]) -> str:
        """Get final extraction instruction"""
        
        entities_list = ", ".join([e.replace('_', ' ') for e in extraction_focus])
        
        return f"""
**FINAL INSTRUCTIONS:**

1. Analyze the provided content thoroughly for {entities_list}
2. Extract ALL relevant entities with high confidence (>0.7)
3. Provide confidence scores based on text clarity and completeness  
4. Use medical device terminology consistently
5. Ensure JSON output is valid and complete
6. If no entities found for a category, return empty array []
7. **HIERARCHICAL EXTRACTION**: Identify System→Subsystem→Component→SparePart relationships
8. **RELATIONSHIP DETECTION**: Extract causal, spatial, functional, and temporal relationships
9. **LINAC SPECIALIZATION**: Use LINAC subsystem knowledge for accurate classification

**BEGIN EXTRACTION NOW:**
        """.strip()
    
    def build_hierarchical_extraction_prompt(
        self,
        page_content: str,
        device_type: str = "linear_accelerator",
        focus_subsystem: str = None
    ) -> str:
        """
        Build specialized prompt for hierarchical ontology extraction
        
        Args:
            page_content: Text content to analyze
            device_type: Type of medical device
            focus_subsystem: Specific subsystem to focus on (optional)
        """
        
        prompt_parts = [
            self._get_hierarchical_system_instruction(device_type, focus_subsystem),
            self._get_hierarchical_entity_definitions(),
            self._get_linac_subsystem_guidelines() if device_type == "linear_accelerator" else "",
            self._get_relationship_extraction_guidelines(),
            self._get_hierarchical_output_format(),
            self._get_hierarchical_examples(device_type),
            f"\n**CONTENT TO ANALYZE:**\n{page_content}\n",
            self._get_hierarchical_final_instruction()
        ]
        
        return "\n\n".join([part for part in prompt_parts if part])
    
    def _get_hierarchical_system_instruction(self, device_type: str, focus_subsystem: str = None) -> str:
        """Get system instruction for hierarchical extraction"""
        
        device_name = device_type.replace('_', ' ').title()
        focus_text = f" with special focus on {focus_subsystem}" if focus_subsystem else ""
        
        return f"""
You are an expert medical device ontology engineer specializing in {device_name} systems{focus_text}.
Your task is to extract hierarchical entities and relationships to build a comprehensive medical device ontology.

**ONTOLOGY STRUCTURE:**
System (Top Level) → Subsystem → Component → SparePart

**EXTRACTION PRIORITIES:**
1. **Hierarchical Classification**: Identify where each entity fits in the System→Subsystem→Component→SparePart hierarchy
2. **Relationship Mapping**: Extract causal, spatial, functional, and temporal relationships between entities
3. **LINAC Specialization**: Use domain knowledge of LINAC subsystems for accurate classification
4. **Medical Device Standards**: Align with IEC 60601 and medical device terminology

**QUALITY REQUIREMENTS:**
- Hierarchical accuracy >95%
- Relationship confidence >80%
- Complete entity extraction
- Proper medical terminology
- Structured ontology output
        """.strip()
    
    def _get_hierarchical_entity_definitions(self) -> str:
        """Get entity definitions for hierarchical extraction"""
        
        return """
**HIERARCHICAL ENTITY TYPES:**

**SYSTEMS (Top Level):**
- Complete medical devices or major functional units
- Examples: "LINAC System", "Treatment Planning System", "Patient Monitoring System"
- Fields: name, type, model, manufacturer, primary_function, subsystems, status

**SUBSYSTEMS (Level 2):**
- Functional units within systems
- Examples: "Beam Delivery System", "MLC System", "Patient Positioning System"
- Fields: name, type, parent_system, components, function, control_method, interfaces

**COMPONENTS (Level 3):**
- Individual parts within subsystems
- Examples: "Leaf Motor", "Position Sensor", "Drive Controller"
- Fields: name, type, function, parent_subsystem, specifications, spare_parts, maintenance_cycle

**SPARE PARTS (Level 4):**
- Replaceable parts for components
- Examples: "Motor Assembly P/N 12345", "Sensor Board P/N 67890"
- Fields: part_number, name, component, supplier, lifecycle_status, maintenance_cycle

**RELATIONSHIPS:**
- Connections between entities at any level
- Types: causal, spatial, functional, temporal, dependency
- Fields: source_entity, target_entity, relationship_type, description, confidence
        """.strip()
    
    def _get_linac_subsystem_guidelines(self) -> str:
        """Get LINAC-specific subsystem extraction guidelines"""
        
        subsystem_descriptions = []
        for subsystem, info in self.linac_subsystems.items():
            components_text = ", ".join(info["components"][:3]) + ("..." if len(info["components"]) > 3 else "")
            subsystem_descriptions.append(f"- **{subsystem}**: {info['description']} (Components: {components_text})")
        
        return f"""
**LINAC SUBSYSTEM CLASSIFICATION:**

{chr(10).join(subsystem_descriptions)}

**CLASSIFICATION RULES:**
1. **BeamDeliverySystem**: Components related to radiation beam generation and delivery
2. **PatientPositioningSystem**: Components for patient setup and positioning
3. **MLCSystem**: Multi-leaf collimator components for beam shaping
4. **GantrySystem**: Components for gantry rotation and positioning
5. **ImagingSystem**: Components for patient imaging and verification
6. **SafetySystem**: Components for radiation safety and interlocks
7. **ControlSystem**: Components for system control and user interface

**COMPONENT IDENTIFICATION:**
- Look for motor, sensor, controller, actuator keywords
- Identify part numbers and model numbers
- Extract technical specifications and parameters
- Note maintenance cycles and replacement schedules
        """.strip()
    
    def _get_relationship_extraction_guidelines(self) -> str:
        """Get guidelines for relationship extraction"""
        
        return """
**RELATIONSHIP EXTRACTION GUIDELINES:**

**CAUSAL RELATIONSHIPS:**
- Error codes → Component failures
- Component malfunctions → System errors
- Maintenance actions → Problem resolution
- Keywords: "causes", "triggers", "results in", "leads to"

**SPATIAL RELATIONSHIPS:**
- Component → Subsystem membership
- Subsystem → System membership  
- Physical connections and locations
- Keywords: "part of", "contains", "located in", "connected to"

**FUNCTIONAL RELATIONSHIPS:**
- Control relationships between components
- Monitoring and feedback loops
- Operational dependencies
- Keywords: "controls", "monitors", "regulates", "operates"

**TEMPORAL RELATIONSHIPS:**
- Sequence of operations
- Maintenance schedules
- Error occurrence patterns
- Keywords: "before", "after", "during", "follows"

**DEPENDENCY RELATIONSHIPS:**
- Component dependencies
- System requirements
- Operational prerequisites
- Keywords: "requires", "depends on", "enables", "supports"

**EXTRACTION RULES:**
1. Extract explicit relationships mentioned in text
2. Infer logical relationships from context
3. Assign confidence scores (0.8+ for explicit, 0.6+ for inferred)
4. Validate relationships against domain knowledge
        """.strip()
    
    def _get_hierarchical_output_format(self) -> str:
        """Get output format for hierarchical extraction"""
        
        return """
**HIERARCHICAL OUTPUT FORMAT:**

```json
{
  "systems": [
    {
      "name": "string",
      "type": "string", 
      "model": "string",
      "manufacturer": "string",
      "primary_function": "string",
      "subsystems": ["array of subsystem names"],
      "status": "string",
      "confidence": 0.0-1.0
    }
  ],
  "subsystems": [
    {
      "name": "string",
      "type": "string",
      "parent_system": "string",
      "components": ["array of component names"],
      "function": "string", 
      "control_method": "string",
      "interfaces": ["array of interface types"],
      "confidence": 0.0-1.0
    }
  ],
  "components": [
    {
      "name": "string",
      "type": "string",
      "function": "string",
      "parent_subsystem": "string", 
      "specifications": "string",
      "spare_parts": ["array of part numbers"],
      "maintenance_cycle": "string",
      "confidence": 0.0-1.0
    }
  ],
  "spare_parts": [
    {
      "part_number": "string",
      "name": "string",
      "component": "string",
      "supplier": "string",
      "lifecycle_status": "string",
      "maintenance_cycle": "string",
      "specifications": "string",
      "confidence": 0.0-1.0
    }
  ],
  "relationships": [
    {
      "source_entity": "string",
      "target_entity": "string", 
      "relationship_type": "causal|spatial|functional|temporal|dependency",
      "description": "string",
      "confidence": 0.0-1.0
    }
  ],
  "error_codes": [...],
  "procedures": [...],
  "safety_protocols": [...]
}
```
        """.strip()
    
    def _get_hierarchical_examples(self, device_type: str) -> str:
        """Get examples for hierarchical extraction"""
        
        if device_type == "linear_accelerator":
            return """
**HIERARCHICAL EXTRACTION EXAMPLES:**

**Example 1 - System Level:**
Input: "The Varian TrueBeam LINAC system consists of multiple subsystems including beam delivery, patient positioning, and multi-leaf collimator systems."

Output:
```json
{
  "systems": [{
    "name": "Varian TrueBeam LINAC",
    "type": "Linear Accelerator",
    "manufacturer": "Varian Medical Systems",
    "primary_function": "Radiation therapy delivery",
    "subsystems": ["Beam Delivery System", "Patient Positioning System", "MLC System"],
    "confidence": 0.95
  }]
}
```

**Example 2 - Subsystem Level:**
Input: "The MLC system controls individual leaf positions using stepper motors and position feedback sensors."

Output:
```json
{
  "subsystems": [{
    "name": "MLC System", 
    "type": "Beam Shaping System",
    "parent_system": "LINAC System",
    "components": ["Leaf Motors", "Position Sensors"],
    "function": "Beam shaping and modulation",
    "control_method": "Stepper motor control",
    "confidence": 0.90
  }]
}
```

**Example 3 - Component Level:**
Input: "Each leaf motor assembly (P/N 12345-67) consists of a stepper motor, encoder, and drive electronics."

Output:
```json
{
  "components": [{
    "name": "Leaf Motor Assembly",
    "type": "Actuator",
    "function": "Individual leaf positioning",
    "parent_subsystem": "MLC System",
    "specifications": "Stepper motor with encoder",
    "spare_parts": ["P/N 12345-67"],
    "confidence": 0.92
  }]
}
```

**Example 4 - Relationships:**
Input: "Error 7002 indicates leaf motor movement failure, requiring motor assembly replacement."

Output:
```json
{
  "relationships": [
    {
      "source_entity": "Error 7002",
      "target_entity": "Leaf Motor Assembly",
      "relationship_type": "causal",
      "description": "Error indicates motor failure",
      "confidence": 0.88
    },
    {
      "source_entity": "Motor Assembly Replacement",
      "target_entity": "Error 7002",
      "relationship_type": "causal", 
      "description": "Replacement resolves error",
      "confidence": 0.85
    }
  ]
}
```
            """.strip()
        
        return ""
    
    def _get_hierarchical_final_instruction(self) -> str:
        """Get final instruction for hierarchical extraction"""
        
        return """
**HIERARCHICAL EXTRACTION INSTRUCTIONS:**

1. **ANALYZE HIERARCHY**: Identify System→Subsystem→Component→SparePart structure
2. **EXTRACT ENTITIES**: Extract all entities at appropriate hierarchy levels
3. **MAP RELATIONSHIPS**: Identify causal, spatial, functional, temporal, and dependency relationships
4. **ASSIGN CONFIDENCE**: Provide confidence scores based on text clarity and domain knowledge
5. **VALIDATE STRUCTURE**: Ensure hierarchical consistency and medical device terminology
6. **COMPLETE OUTPUT**: Provide comprehensive JSON with all entity types and relationships

**QUALITY CHECKLIST:**
- ✓ Hierarchical structure maintained
- ✓ LINAC subsystems correctly classified  
- ✓ Relationships properly typed and described
- ✓ Confidence scores realistic (0.7-1.0 range)
- ✓ Medical device terminology used consistently
- ✓ JSON format valid and complete

**BEGIN HIERARCHICAL EXTRACTION:**
        """.strip()


# Utility functions for prompt management

def get_device_specific_vocabulary(device_type: str) -> List[str]:
    """Get vocabulary specific to device type"""
    
    prompt_builder = MedicalDevicePrompts()
    return prompt_builder.device_vocabularies.get(device_type, [])


def validate_extraction_focus(focus_list: List[str]) -> List[str]:
    """Validate and clean extraction focus list"""
    
    valid_entities = [
        "error_codes", "components", "procedures", 
        "safety_protocols", "technical_specifications",
        "systems", "subsystems", "spare_parts", "relationships"
    ]
    
    return [entity for entity in focus_list if entity in valid_entities]


def build_relationship_detection_prompt(
    entities: List[Dict[str, Any]], 
    context_text: str,
    device_type: str = "linear_accelerator"
) -> str:
    """
    Build specialized prompt for relationship detection between entities
    
    Args:
        entities: List of already extracted entities
        context_text: Original text context
        device_type: Type of medical device
    """
    
    prompt_builder = MedicalDevicePrompts()
    
    entity_list = []
    for entity in entities:
        entity_name = entity.get('name', entity.get('code', 'Unknown'))
        entity_type = entity.get('type', 'Unknown')
        entity_list.append(f"- {entity_name} ({entity_type})")
    
    entities_text = "\n".join(entity_list)
    
    return f"""
You are an expert medical device ontology engineer specializing in relationship detection.
Your task is to identify relationships between extracted entities based on the provided context.

**EXTRACTED ENTITIES:**
{entities_text}

**RELATIONSHIP TYPES TO DETECT:**

**CAUSAL RELATIONSHIPS:**
- Error codes → Component failures
- Component malfunctions → System errors  
- Maintenance actions → Problem resolution
- Keywords: causes, triggers, results_in, leads_to, prevents

**SPATIAL RELATIONSHIPS:**
- Component → Subsystem membership (part_of)
- Subsystem → System membership (part_of)
- Physical connections (connected_to, adjacent_to)
- Location relationships (located_in, contains)

**FUNCTIONAL RELATIONSHIPS:**
- Control relationships (controls, regulates)
- Monitoring relationships (monitors, measures)
- Operational relationships (operates, interfaces_with)
- Support relationships (supports, enables)

**TEMPORAL RELATIONSHIPS:**
- Sequence relationships (precedes, follows)
- Concurrent relationships (concurrent_with, during)
- Timing relationships (before, after)

**DEPENDENCY RELATIONSHIPS:**
- Requirement relationships (requires, depends_on)
- Enablement relationships (enables, supports)
- Impact relationships (affects, influences)

**CONTEXT TEXT:**
{context_text}

**OUTPUT FORMAT:**
```json
{{
  "relationships": [
    {{
      "source_entity": "Entity name from list above",
      "target_entity": "Entity name from list above", 
      "relationship_type": "causal|spatial|functional|temporal|dependency",
      "description": "Clear description of the relationship",
      "confidence": 0.0-1.0,
      "evidence_text": "Text snippet supporting this relationship"
    }}
  ]
}}
```

**INSTRUCTIONS:**
1. Analyze the context text for explicit and implicit relationships
2. Only create relationships between entities in the provided list
3. Assign confidence scores: 0.9+ for explicit, 0.7+ for strong inference, 0.5+ for weak inference
4. Provide evidence text that supports each relationship
5. Focus on medically and technically meaningful relationships
6. Ensure relationship directions are correct (source → target)

**BEGIN RELATIONSHIP DETECTION:**
    """.strip()


def build_linac_subsystem_prompt(
    page_content: str,
    target_subsystem: str
) -> str:
    """
    Build specialized prompt for specific LINAC subsystem extraction
    
    Args:
        page_content: Text content to analyze
        target_subsystem: Specific LINAC subsystem to focus on
    """
    
    prompt_builder = MedicalDevicePrompts()
    
    if target_subsystem not in prompt_builder.linac_subsystems:
        raise ValueError(f"Unknown LINAC subsystem: {target_subsystem}")
    
    subsystem_info = prompt_builder.linac_subsystems[target_subsystem]
    components_text = ", ".join(subsystem_info["components"])
    functions_text = ", ".join(subsystem_info["functions"])
    
    return f"""
You are an expert LINAC engineer specializing in the {target_subsystem}.
Your task is to extract detailed information about this specific subsystem from the provided content.

**TARGET SUBSYSTEM: {target_subsystem}**
- Description: {subsystem_info["description"]}
- Key Components: {components_text}
- Primary Functions: {functions_text}

**EXTRACTION FOCUS:**
1. **Components**: All components belonging to {target_subsystem}
2. **Specifications**: Technical parameters and specifications
3. **Error Codes**: Errors specific to this subsystem
4. **Procedures**: Maintenance and troubleshooting procedures
5. **Relationships**: How components interact within this subsystem

**CONTENT TO ANALYZE:**
{page_content}

**OUTPUT FORMAT:**
```json
{{
  "subsystem": {{
    "name": "{target_subsystem}",
    "components": [
      {{
        "name": "string",
        "type": "string", 
        "function": "string",
        "specifications": "string",
        "confidence": 0.0-1.0
      }}
    ],
    "error_codes": [
      {{
        "code": "string",
        "description": "string",
        "related_components": ["array"],
        "confidence": 0.0-1.0
      }}
    ],
    "procedures": [
      {{
        "name": "string",
        "type": "string",
        "related_components": ["array"],
        "confidence": 0.0-1.0
      }}
    ],
    "relationships": [
      {{
        "source_entity": "string",
        "target_entity": "string",
        "relationship_type": "string", 
        "description": "string",
        "confidence": 0.0-1.0
      }}
    ]
  }}
}}
```

**SPECIALIZED INSTRUCTIONS FOR {target_subsystem}:**
- Focus on components and functions specific to this subsystem
- Extract technical specifications relevant to subsystem operation
- Identify error codes that affect this subsystem
- Note maintenance procedures specific to subsystem components
- Map relationships between components within the subsystem

**BEGIN SUBSYSTEM EXTRACTION:**
    """.strip()
