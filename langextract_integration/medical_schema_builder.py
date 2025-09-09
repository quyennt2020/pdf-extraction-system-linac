"""
Medical Schema Builder for LangExtract

Constructs few-shot examples and schemas specifically for medical device
entity extraction using LangExtract framework.
"""

import textwrap
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import langextract as lx


@dataclass
class MedicalEntityExample:
    """Medical entity example for few-shot learning"""
    text: str
    extractions: List[Dict[str, Any]]
    context_type: str = "service_manual"
    device_type: str = "linear_accelerator"


class MedicalSchemaBuilder:
    """Builds schemas and examples for medical device entity extraction"""
    
    def __init__(self, device_type: str = "linear_accelerator"):
        self.device_type = device_type
        self.examples = []
    
    def build_error_code_examples(self) -> List[lx.data.ExampleData]:
        """Build few-shot examples for error code extraction"""
        
        examples = [
            lx.data.ExampleData(
                text=textwrap.dedent("""
                Error Code 7002: MOVEMENT
                Software Release: R6.0x, R6.1x, R7.0x\\Integrity™ R1.1
                Description: The actual direction of movement of a leaf does not match the expected direction.  
                Response: Check the drive to the leaf motors and the leaves for free movement.
                Category: Mechanical
                Severity: High
                """).strip(),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="error_code",
                        extraction_text="7002",
                        attributes={
                            "message": "MOVEMENT",
                            "software_releases": ["R6.0x", "R6.1x", "R7.0x\\Integrity™ R1.1"],
                            "description": "The actual direction of movement of a leaf does not match the expected direction",
                            "response_action": "Check the drive to the leaf motors and the leaves for free movement",
                            "category": "Mechanical",
                            "severity": "High",
                            "device_component": "leaf_motors"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="component",
                        extraction_text="leaf motors",
                        attributes={
                            "type": "actuator",
                            "function": "control leaf movement direction",
                            "system": "multi_leaf_collimator"
                        }
                    )
                ]
            ),
            
            lx.data.ExampleData(
                text=textwrap.dedent("""
                Error Code 5001: CALIBRATION FAILURE
                Software Release: R7.0x, R7.1x
                Description: Beam calibration values are outside acceptable tolerance range.
                Response: Recalibrate beam delivery system. Contact service engineer if problem persists.
                Category: Software
                Severity: Critical
                """).strip(),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="error_code", 
                        extraction_text="5001",
                        attributes={
                            "message": "CALIBRATION FAILURE",
                            "software_releases": ["R7.0x", "R7.1x"],
                            "description": "Beam calibration values are outside acceptable tolerance range",
                            "response_action": "Recalibrate beam delivery system. Contact service engineer if problem persists",
                            "category": "Software",
                            "severity": "Critical",
                            "device_component": "beam_delivery_system"
                        }
                    )
                ]
            )
        ]
        
        return examples
    
    def build_component_examples(self) -> List[lx.data.ExampleData]:
        """Build few-shot examples for component extraction"""
        
        examples = [
            lx.data.ExampleData(
                text=textwrap.dedent("""
                The gantry rotation motor (Model: GRM-450X, Part Number: 12345-ABC) provides precise 
                angular positioning for the treatment head. The motor is controlled by the gantry 
                control unit and monitored by position encoders for accuracy verification.
                Specifications: 360° rotation, ±0.1° accuracy, maximum speed 6 RPM.
                """).strip(),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="component",
                        extraction_text="gantry rotation motor",
                        attributes={
                            "model": "GRM-450X",
                            "part_number": "12345-ABC", 
                            "type": "motor",
                            "function": "precise angular positioning for treatment head",
                            "parent_system": "gantry_system",
                            "controlled_by": "gantry control unit",
                            "monitored_by": "position encoders",
                            "specifications": {
                                "rotation_range": "360°",
                                "accuracy": "±0.1°",
                                "max_speed": "6 RPM"
                            }
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="component",
                        extraction_text="gantry control unit",
                        attributes={
                            "type": "controller",
                            "function": "controls gantry rotation motor",
                            "parent_system": "gantry_system"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="component", 
                        extraction_text="position encoders",
                        attributes={
                            "type": "sensor",
                            "function": "accuracy verification for motor positioning",
                            "parent_system": "gantry_system"
                        }
                    )
                ]
            )
        ]
        
        return examples
    
    def build_procedure_examples(self) -> List[lx.data.ExampleData]:
        """Build few-shot examples for procedure extraction"""
        
        examples = [
            lx.data.ExampleData(
                text=textwrap.dedent("""
                Daily QA Procedure - Beam Output Check:
                1. Power on the system and allow 30-minute warm-up period
                2. Position the dosimetry phantom at isocenter  
                3. Set up ion chamber for measurement
                4. Deliver test beam: 6MV, 100 MU, 10x10 cm field
                5. Record readings and compare with baseline values
                6. Acceptable tolerance: ±2% from baseline
                Prerequisites: System fully operational, phantom available
                Tools Required: Dosimetry phantom, ion chamber, electrometer
                Safety Level: Level 2 (Radiation area controls active)
                Estimated Time: 45 minutes
                """).strip(),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="procedure",
                        extraction_text="Daily QA Procedure - Beam Output Check",
                        attributes={
                            "type": "quality_assurance",
                            "frequency": "daily",
                            "steps": [
                                "Power on the system and allow 30-minute warm-up period",
                                "Position the dosimetry phantom at isocenter",
                                "Set up ion chamber for measurement", 
                                "Deliver test beam: 6MV, 100 MU, 10x10 cm field",
                                "Record readings and compare with baseline values"
                            ],
                            "acceptance_criteria": "±2% from baseline",
                            "prerequisites": ["System fully operational", "phantom available"],
                            "tools_required": ["Dosimetry phantom", "ion chamber", "electrometer"],
                            "safety_level": "Level 2",
                            "radiation_controls": True,
                            "estimated_time_minutes": 45,
                            "beam_parameters": {
                                "energy": "6MV",
                                "monitor_units": "100 MU", 
                                "field_size": "10x10 cm"
                            }
                        }
                    )
                ]
            )
        ]
        
        return examples
    
    def build_safety_examples(self) -> List[lx.data.ExampleData]:
        """Build few-shot examples for safety protocol extraction"""
        
        examples = [
            lx.data.ExampleData(
                text=textwrap.dedent("""
                ⚠️ WARNING: High Voltage Hazard
                Before opening the magnetron cabinet, ensure that:
                - Main power is OFF and locked out
                - High voltage discharge procedure is completed  
                - Wait minimum 10 minutes for capacitor discharge
                - Verify zero energy state with approved meter
                - Use insulated tools only
                Compliance Standard: IEC 60601-2-1, Section 12.4.3
                Violation may result in serious injury or death.
                """).strip(),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="safety_protocol",
                        extraction_text="High Voltage Hazard",
                        attributes={
                            "type": "WARNING",
                            "hazard_category": "electrical",
                            "severity": "serious_injury_or_death",
                            "equipment": "magnetron cabinet",
                            "safety_steps": [
                                "Main power is OFF and locked out",
                                "High voltage discharge procedure is completed",
                                "Wait minimum 10 minutes for capacitor discharge",
                                "Verify zero energy state with approved meter",
                                "Use insulated tools only"
                            ],
                            "compliance_standard": "IEC 60601-2-1, Section 12.4.3",
                            "minimum_wait_time_minutes": 10,
                            "required_tools": ["insulated tools", "approved meter"],
                            "lockout_required": True
                        }
                    )
                ]
            )
        ]
        
        return examples
    
    def build_linac_prompt_description(self) -> str:
        """Build comprehensive prompt description for LINAC extraction"""
        
        return textwrap.dedent("""
        Extract structured information from LINAC (Linear Accelerator) service manual content.
        
        Focus on these entity types:
        1. ERROR CODES: Diagnostic codes with messages, descriptions, and response actions
        2. COMPONENTS: Physical parts, subsystems, and assemblies with specifications  
        3. PROCEDURES: Step-by-step instructions for maintenance, calibration, and QA
        4. SAFETY PROTOCOLS: Warnings, cautions, and safety requirements
        
        For each entity:
        - Use exact text from the source (no paraphrasing)
        - Extract comprehensive attributes including technical specifications
        - Identify relationships between entities where present
        - Preserve safety-critical information with high accuracy
        - Include software version compatibility where mentioned
        
        Medical device context: Linear accelerator for radiation therapy
        Compliance requirements: IEC 60601 medical device safety standards
        """).strip()
    
    def build_hierarchical_prompt_description(self, focus_subsystem: str = None) -> str:
        """Build prompt for hierarchical ontology extraction"""
        
        focus_text = f" Focus specifically on the {focus_subsystem} subsystem." if focus_subsystem else ""
        
        return textwrap.dedent(f"""
        Extract hierarchical ontology information from LINAC service manual content.
        
        Extract these entity levels:
        1. SYSTEMS: Major system-level components (e.g., Beam Delivery System, Patient Positioning System)
        2. SUBSYSTEMS: Intermediate functional groups within systems
        3. COMPONENTS: Individual parts and assemblies  
        4. RELATIONSHIPS: Hierarchical and functional relationships between entities
        
        For hierarchical extraction:
        - Identify parent-child relationships (system → subsystem → component)
        - Extract functional relationships (controls, monitors, requires)
        - Preserve system boundaries and interfaces
        - Include spare part information where available
        
        Context: LINAC medical device ontology construction{focus_text}
        Output format: Structured entities with explicit relationship mappings
        """).strip()
    
    def get_all_examples(self) -> List[lx.data.ExampleData]:
        """Get all medical device examples for general extraction"""
        
        examples = []
        examples.extend(self.build_error_code_examples())
        examples.extend(self.build_component_examples()) 
        examples.extend(self.build_procedure_examples())
        examples.extend(self.build_safety_examples())
        
        return examples
    
    def get_examples_by_type(self, entity_type: str) -> List[lx.data.ExampleData]:
        """Get examples filtered by entity type"""
        
        type_mapping = {
            "error_codes": self.build_error_code_examples,
            "components": self.build_component_examples,
            "procedures": self.build_procedure_examples,
            "safety_protocols": self.build_safety_examples
        }
        
        if entity_type in type_mapping:
            return type_mapping[entity_type]()
        else:
            return self.get_all_examples()
    
    def validate_examples(self) -> Dict[str, Any]:
        """Validate example quality and coverage"""
        
        all_examples = self.get_all_examples()
        
        validation_result = {
            "total_examples": len(all_examples),
            "entity_types": set(),
            "attribute_coverage": {},
            "text_lengths": [],
            "extraction_counts": []
        }
        
        for example in all_examples:
            validation_result["text_lengths"].append(len(example.text))
            validation_result["extraction_counts"].append(len(example.extractions))
            
            for extraction in example.extractions:
                validation_result["entity_types"].add(extraction.extraction_class)
                
                # Track attribute usage
                for attr_name in extraction.attributes.keys():
                    if attr_name not in validation_result["attribute_coverage"]:
                        validation_result["attribute_coverage"][attr_name] = 0
                    validation_result["attribute_coverage"][attr_name] += 1
        
        # Convert set to list for JSON serialization
        validation_result["entity_types"] = list(validation_result["entity_types"])
        
        # Calculate statistics
        text_lengths = validation_result["text_lengths"]
        extraction_counts = validation_result["extraction_counts"]
        
        validation_result["statistics"] = {
            "avg_text_length": sum(text_lengths) / len(text_lengths) if text_lengths else 0,
            "avg_extractions_per_example": sum(extraction_counts) / len(extraction_counts) if extraction_counts else 0,
            "min_text_length": min(text_lengths) if text_lengths else 0,
            "max_text_length": max(text_lengths) if text_lengths else 0
        }
        
        return validation_result


if __name__ == "__main__":
    # Test the schema builder
    
    builder = MedicalSchemaBuilder()
    
    # Validate examples
    validation = builder.validate_examples()
    print(f"✅ Schema validation results:")
    print(f"   📊 Total examples: {validation['total_examples']}")
    print(f"   🏷️ Entity types: {validation['entity_types']}")
    print(f"   📝 Avg text length: {validation['statistics']['avg_text_length']:.0f} chars")
    print(f"   🎯 Avg extractions per example: {validation['statistics']['avg_extractions_per_example']:.1f}")
    
    # Test prompt generation
    prompt = builder.build_linac_prompt_description()
    print(f"\n✅ Generated LINAC prompt ({len(prompt)} chars)")
    
    # Test hierarchical prompt  
    hierarchical_prompt = builder.build_hierarchical_prompt_description("Beam Delivery System")
    print(f"✅ Generated hierarchical prompt ({len(hierarchical_prompt)} chars)")
    
    print("\n🎉 Medical schema builder test completed successfully!")