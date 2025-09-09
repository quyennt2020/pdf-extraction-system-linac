"""
Medical Entity Parser for processing Gemini Flash responses
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from loguru import logger
import uuid
from datetime import datetime


@dataclass
class EntityExtraction:
    """Base class for extracted entities"""
    id: str = None
    confidence: float = 0.0
    source_page: int = 0
    source_text: str = ""
    extraction_timestamp: float = 0.0
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.extraction_timestamp:
            self.extraction_timestamp = datetime.now().timestamp()


@dataclass
class ErrorCodeEntity(EntityExtraction):
    """Error code entity structure"""
    code: str = None
    software_release: str = "unknown"
    message: str = "unknown"
    description: str = "unknown"
    response: str = "unknown"
    category: str = "System"
    severity: str = "Medium"
    context: str = ""


@dataclass
class ComponentEntity(EntityExtraction):
    """Component entity structure"""
    name: str = None
    type: str = "unknown"
    function: str = "unknown"
    parent_system: str = "unknown"
    specifications: str = "unknown"


@dataclass
class ProcedureEntity(EntityExtraction):
    """Procedure entity structure"""
    name: str = None
    type: str = "Maintenance"
    description: str = "unknown"
    steps: List[str] = None
    prerequisites: List[str] = None
    safety_level: str = "Level_2"
    estimated_time: str = "unknown"
    
    def __post_init__(self):
        super().__post_init__()
        if self.steps is None:
            self.steps = []
        if self.prerequisites is None:
            self.prerequisites = []


@dataclass
class SafetyProtocolEntity(EntityExtraction):
    """Safety protocol entity structure"""
    type: str = "NOTE"
    title: str = "unknown"
    description: str = "unknown"
    applicable_procedures: List[str] = None
    compliance_standard: str = "unknown"
    
    def __post_init__(self):
        super().__post_init__()
        if self.applicable_procedures is None:
            self.applicable_procedures = []


@dataclass
class TechnicalSpecificationEntity(EntityExtraction):
    """Technical specification entity structure"""
    parameter: str = None
    value: str = "unknown"
    unit: str = "unknown"
    tolerance: str = "unknown"
    measurement_method: str = "unknown"


@dataclass
class SystemEntity(EntityExtraction):
    """System entity structure for hierarchical ontology"""
    name: str = None
    type: str = "unknown"
    model: str = "unknown"
    manufacturer: str = "unknown"
    primary_function: str = "unknown"
    subsystems: List[str] = None
    status: str = "unknown"
    
    def __post_init__(self):
        super().__post_init__()
        if self.subsystems is None:
            self.subsystems = []


@dataclass
class SubsystemEntity(EntityExtraction):
    """Subsystem entity structure for hierarchical ontology"""
    name: str = None
    type: str = "unknown"
    parent_system: str = "unknown"
    components: List[str] = None
    function: str = "unknown"
    control_method: str = "unknown"
    interfaces: List[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        if self.components is None:
            self.components = []
        if self.interfaces is None:
            self.interfaces = []


@dataclass
class HierarchicalComponentEntity(EntityExtraction):
    """Enhanced component entity for hierarchical ontology"""
    name: str = None
    type: str = "unknown"
    function: str = "unknown"
    parent_subsystem: str = "unknown"
    specifications: str = "unknown"
    spare_parts: List[str] = None
    maintenance_cycle: str = "unknown"
    
    def __post_init__(self):
        super().__post_init__()
        if self.spare_parts is None:
            self.spare_parts = []


@dataclass
class SparePartEntity(EntityExtraction):
    """Spare part entity structure"""
    part_number: str = None
    name: str = "unknown"
    component: str = "unknown"
    supplier: str = "unknown"
    lifecycle_status: str = "active"
    maintenance_cycle: str = "unknown"
    specifications: str = "unknown"


@dataclass
class RelationshipEntity(EntityExtraction):
    """Relationship entity structure"""
    source_entity: str = None
    target_entity: str = None
    relationship_type: str = "unknown"
    description: str = "unknown"
    evidence_text: str = "unknown"


class MedicalEntityParser:
    """
    Parser for converting Gemini Flash responses into structured medical entities
    """
    
    def __init__(self):
        """Initialize parser"""
        
        self.entity_classes = {
            "error_codes": ErrorCodeEntity,
            "components": ComponentEntity,
            "procedures": ProcedureEntity,
            "safety_protocols": SafetyProtocolEntity,
            "technical_specifications": TechnicalSpecificationEntity,
            "systems": SystemEntity,
            "subsystems": SubsystemEntity,
            "hierarchical_components": HierarchicalComponentEntity,
            "spare_parts": SparePartEntity,
            "relationships": RelationshipEntity
        }
        
        # Pattern matching for fallback parsing
        self.error_code_patterns = [
            r'(\d{4})\s+([R\d\.\,\s\\™x]+)\s+([A-Z\s\-]+)\s+(.*?)(?=Response:|$)',
            r'Error\s+Code\s*:?\s*(\d{4})',
            r'Code\s*(\d{4})',
            r'\b(\d{4})\b'
        ]
        
        self.component_patterns = [
            r'(motor|sensor|controller|actuator|detector|monitor|chamber|beam|couch|gantry)',
            r'(MLC|MLCi|collimator|leaf)',
            r'(assembly|system|unit|device)'
        ]
        
        logger.info("Medical entity parser initialized")
    
    def parse_gemini_response(
        self,
        response: str,
        page_number: int = 0,
        source_text: str = ""
    ) -> Dict[str, List[EntityExtraction]]:
        """
        Parse Gemini response into structured medical entities
        
        Args:
            response: Raw response from Gemini Flash
            page_number: Source page number
            source_text: Original source text
            
        Returns:
            Dictionary of parsed entities by type
        """
        
        logger.info(f"Parsing Gemini response for page {page_number}")
        
        try:
            # First attempt: Parse as JSON
            if self._is_json_response(response):
                entities = self._parse_json_response(response, page_number, source_text)
            else:
                # Fallback: Parse as structured text
                entities = self._parse_text_response(response, page_number, source_text)
            
            # Validate and clean entities
            entities = self._validate_entities(entities)
            
            # Add metadata
            self._add_parsing_metadata(entities, response)
            
            logger.info(f"Successfully parsed entities: {self._count_entities(entities)}")
            
            return entities
            
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            return self._create_empty_entity_dict()
    
    def _is_json_response(self, response: str) -> bool:
        """Check if response is valid JSON"""
        
        response = response.strip()
        
        # Remove markdown code blocks if present
        if response.startswith('```json'):
            response = response.replace('```json', '').replace('```', '').strip()
        elif response.startswith('```'):
            response = response.replace('```', '').strip()
        
        try:
            json.loads(response)
            return True
        except json.JSONDecodeError:
            return False
    
    def _parse_json_response(
        self,
        response: str,
        page_number: int,
        source_text: str
    ) -> Dict[str, List[EntityExtraction]]:
        """Parse JSON response from Gemini"""
        
        # Clean response
        response = response.strip()
        if response.startswith('```json'):
            response = response.replace('```json', '').replace('```', '').strip()
        elif response.startswith('```'):
            response = response.replace('```', '').strip()
        
        # Parse JSON
        json_data = json.loads(response)
        
        entities = {}
        
        for entity_type, entity_list in json_data.items():
            if entity_type in self.entity_classes and isinstance(entity_list, list):
                entities[entity_type] = []
                
                for entity_data in entity_list:
                    if isinstance(entity_data, dict):
                        entity = self._create_entity_from_dict(
                            entity_type=entity_type,
                            entity_data=entity_data,
                            page_number=page_number,
                            source_text=source_text
                        )
                        if entity:
                            entities[entity_type].append(entity)
        
        return entities
    
    def _parse_text_response(
        self,
        response: str,
        page_number: int,
        source_text: str
    ) -> Dict[str, List[EntityExtraction]]:
        """Parse unstructured text response from Gemini"""
        
        entities = self._create_empty_entity_dict()
        
        # Split response into sections
        sections = self._split_response_into_sections(response)
        
        for section in sections:
            section_type = self._identify_section_type(section)
            
            if section_type == "error_codes":
                error_codes = self._extract_error_codes_from_text(section, page_number, source_text)
                entities["error_codes"].extend(error_codes)
            
            elif section_type == "components":
                components = self._extract_components_from_text(section, page_number, source_text)
                entities["components"].extend(components)
            
            elif section_type == "procedures":
                procedures = self._extract_procedures_from_text(section, page_number, source_text)
                entities["procedures"].extend(procedures)
            
            elif section_type == "safety_protocols":
                safety_protocols = self._extract_safety_from_text(section, page_number, source_text)
                entities["safety_protocols"].extend(safety_protocols)
        
        return entities
    
    def _create_entity_from_dict(
        self,
        entity_type: str,
        entity_data: Dict[str, Any],
        page_number: int,
        source_text: str
    ) -> Optional[EntityExtraction]:
        """Create entity object from dictionary data"""
        
        try:
            entity_class = self.entity_classes[entity_type]
            
            # Add base fields
            entity_data["source_page"] = page_number
            entity_data["source_text"] = source_text[:500]  # Limit source text length
            
            # Ensure required fields have default values
            if "confidence" not in entity_data:
                entity_data["confidence"] = 0.8
            
            # Handle entity-specific field requirements
            if entity_type == "error_codes" and "code" not in entity_data:
                logger.warning("Error code entity missing required 'code' field")
                return None
            
            if entity_type == "components" and "name" not in entity_data:
                logger.warning("Component entity missing required 'name' field")
                return None
            
            if entity_type == "procedures" and "name" not in entity_data:
                logger.warning("Procedure entity missing required 'name' field")
                return None
            
            if entity_type == "safety_protocols" and "description" not in entity_data:
                logger.warning("Safety protocol entity missing required 'description' field")
                return None
            
            if entity_type == "technical_specifications" and "parameter" not in entity_data:
                logger.warning("Technical specification entity missing required 'parameter' field")
                return None
            
            # Create entity instance
            entity = entity_class(**entity_data)
            
            return entity
            
        except Exception as e:
            logger.error(f"Error creating {entity_type} entity: {str(e)}")
            return None
    
    def _extract_safety_from_text(
        self,
        text: str,
        page_number: int,
        source_text: str
    ) -> List[SafetyProtocolEntity]:
        """Extract safety protocols from unstructured text"""
        
        safety_protocols = []
        
        safety_patterns = [
            r'(WARNING|CAUTION|DANGER|NOTE)\s*:?\s*([^.]+)',
            r'⚠️\s*([^.]+)',
            r'🚨\s*([^.]+)'
        ]
        
        for pattern in safety_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                safety_type = match.group(1).upper() if len(match.groups()) > 1 else "NOTE"
                description = match.group(2) if len(match.groups()) > 1 else match.group(1)
                
                safety_protocol = SafetyProtocolEntity(
                    id=str(uuid.uuid4()),
                    type=safety_type,
                    title=f"{safety_type} Notice",
                    description=description.strip(),
                    confidence=0.8,
                    source_page=page_number,
                    source_text=match.group(0)[:200]
                )
                
                safety_protocols.append(safety_protocol)
        
        return safety_protocols
    
    def _validate_entities(self, entities: Dict[str, List[EntityExtraction]]) -> Dict[str, List[EntityExtraction]]:
        """Validate and clean extracted entities"""
        
        validated_entities = {}
        
        for entity_type, entity_list in entities.items():
            validated_list = []
            
            for entity in entity_list:
                # Basic validation
                if entity.confidence < 0.5:
                    logger.warning(f"Low confidence entity filtered: {entity.confidence}")
                    continue
                
                # Entity-specific validation
                if entity_type == "error_codes" and hasattr(entity, 'code'):
                    if not re.match(r'^\d{4}$', entity.code):
                        logger.warning(f"Invalid error code format: {entity.code}")
                        continue
                
                validated_list.append(entity)
            
            validated_entities[entity_type] = validated_list
        
        return validated_entities
    
    def _add_parsing_metadata(self, entities: Dict[str, List[EntityExtraction]], response: str):
        """Add parsing metadata to entities"""
        
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                # Add metadata if not present
                if not hasattr(entity, 'parsing_metadata'):
                    entity.parsing_metadata = {
                        'response_length': len(response),
                        'parsing_method': 'json' if self._is_json_response(response) else 'text',
                        'parser_version': '1.0'
                    }
    
    def _create_empty_entity_dict(self) -> Dict[str, List[EntityExtraction]]:
        """Create empty entity dictionary with all types"""
        
        return {
            "error_codes": [],
            "components": [],
            "procedures": [],
            "safety_protocols": [],
            "technical_specifications": []
        }
    
    def _count_entities(self, entities: Dict[str, List[EntityExtraction]]) -> int:
        """Count total number of entities"""
        
        return sum(len(entity_list) for entity_list in entities.values())
    
    def _split_response_into_sections(self, response: str) -> List[str]:
        """Split response text into logical sections"""
        
        sections = []
        
        # First try to split by section headers
        section_markers = [
            r'\*\*ERROR CODE.*?\*\*', 
            r'\*\*COMPONENT.*?\*\*', 
            r'\*\*PROCEDURE.*?\*\*', 
            r'\*\*SAFETY.*?\*\*', 
            r'\*\*SPECIFICATION.*?\*\*'
        ]
        
        current_section = ""
        lines = response.split('\n')
        
        for line in lines:
            # Check if line is a section header
            is_header = any(re.match(pattern, line, re.IGNORECASE) for pattern in section_markers)
            
            if is_header and current_section:
                sections.append(current_section.strip())
                current_section = line + '\n'
            else:
                current_section += line + '\n'
        
        if current_section:
            sections.append(current_section.strip())
        
        # If no clear sections found, split by paragraphs
        if not sections or len(sections) == 1:
            sections = [s.strip() for s in response.split('\n\n') if s.strip()]
        
        return sections
    
    def _identify_section_type(self, section: str) -> str:
        """Identify the type of content in a section"""
        
        section_lower = section.lower()
        
        # Check for error code indicators
        if any(keyword in section_lower for keyword in ['error', 'code', 'fault']):
            if re.search(r'\b\d{4}\b', section):
                return "error_codes"
        
        # Check for component indicators
        if any(keyword in section_lower for keyword in ['motor', 'sensor', 'component', 'part', 'assembly', 'mlc', 'leaf']):
            return "components"
        
        # Check for procedure indicators
        if any(keyword in section_lower for keyword in ['procedure', 'step', 'check', 'calibrat', 'test', 'verify']):
            return "procedures"
        
        # Check for safety indicators
        if any(keyword in section_lower for keyword in ['warning', 'caution', 'danger', 'safety', 'note']):
            return "safety_protocols"
        
        return "components"
    
    def _extract_error_codes_from_text(
        self,
        text: str,
        page_number: int,
        source_text: str
    ) -> List[ErrorCodeEntity]:
        """Extract error codes from unstructured text"""
        
        error_codes = []
        
        # Try different error code patterns
        for pattern in self.error_code_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                try:
                    groups = match.groups()
                    
                    if len(groups) >= 1:
                        code = groups[0].strip()
                        
                        # Extract additional information
                        software_release = groups[1].strip() if len(groups) > 1 else "unknown"
                        message = groups[2].strip() if len(groups) > 2 else "unknown"
                        description = groups[3].strip() if len(groups) > 3 else "unknown"
                        
                        # Clean up extracted text
                        software_release = re.sub(r'[^\w\d\.\,\s\\™]', '', software_release)
                        message = re.sub(r'[^A-Z\s\-]', '', message).strip()
                        
                        error_code = ErrorCodeEntity(
                            id=str(uuid.uuid4()),
                            code=code,
                            software_release=software_release,
                            message=message,
                            description=description,
                            confidence=0.8,
                            source_page=page_number,
                            source_text=match.group(0)[:200]
                        )
                        
                        error_codes.append(error_code)
                        
                except Exception as e:
                    logger.warning(f"Error extracting error code from match: {str(e)}")
                    continue
        
        return error_codes
    
    def _extract_components_from_text(
        self,
        text: str,
        page_number: int,
        source_text: str
    ) -> List[ComponentEntity]:
        """Extract components from unstructured text"""
        
        components = []
        
        # Look for component names using patterns
        for pattern in self.component_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                component_name = match.group(0).title()
                
                # Try to extract surrounding context for more info
                start_pos = max(0, match.start() - 50)
                end_pos = min(len(text), match.end() + 100)
                context = text[start_pos:end_pos]
                
                component = ComponentEntity(
                    id=str(uuid.uuid4()),
                    name=component_name,
                    confidence=0.7,
                    source_page=page_number,
                    source_text=context
                )
                
                components.append(component)
        
        return components
    
    def _extract_procedures_from_text(
        self,
        text: str,
        page_number: int,
        source_text: str
    ) -> List[ProcedureEntity]:
        """Extract procedures from unstructured text"""
        
        procedures = []
        
        # Look for procedure patterns
        procedure_patterns = [
            r'(check|calibrat|verify|test|measure)\s+([^.]+)',
            r'procedure\s*:?\s*([^.]+)',
            r'step\s*\d+\s*:?\s*([^.]+)'
        ]
        
        for pattern in procedure_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                procedure_name = match.group(0).strip().title()
                
                procedure = ProcedureEntity(
                    id=str(uuid.uuid4()),
                    name=procedure_name,
                    confidence=0.75,
                    source_page=page_number,
                    source_text=match.group(0)
                )
                
                procedures.append(procedure)
        
        return procedures
    
    def convert_entities_to_dict(self, entities: Dict[str, List[EntityExtraction]]) -> Dict[str, List[Dict]]:
        """Convert entity objects to dictionary format for JSON serialization"""
        
        dict_entities = {}
        
        for entity_type, entity_list in entities.items():
            dict_entities[entity_type] = []
            
            for entity in entity_list:
                entity_dict = asdict(entity)
                dict_entities[entity_type].append(entity_dict)
        
        return dict_entities
    
    def merge_duplicate_entities(self, entities: Dict[str, List[EntityExtraction]]) -> Dict[str, List[EntityExtraction]]:
        """Merge duplicate entities based on similarity"""
        
        merged_entities = {}
        
        for entity_type, entity_list in entities.items():
            if not entity_list:
                merged_entities[entity_type] = []
                continue
            
            # For error codes, merge by code
            if entity_type == "error_codes":
                code_map = {}
                for entity in entity_list:
                    if hasattr(entity, 'code'):
                        if entity.code not in code_map:
                            code_map[entity.code] = entity
                        else:
                            # Keep the one with higher confidence
                            if entity.confidence > code_map[entity.code].confidence:
                                code_map[entity.code] = entity
                
                merged_entities[entity_type] = list(code_map.values())
            
            # For components, merge by name
            elif entity_type == "components":
                name_map = {}
                for entity in entity_list:
                    if hasattr(entity, 'name'):
                        name_key = entity.name.lower()
                        if name_key not in name_map:
                            name_map[name_key] = entity
                        else:
                            # Keep the one with higher confidence
                            if entity.confidence > name_map[name_key].confidence:
                                name_map[name_key] = entity
                
                merged_entities[entity_type] = list(name_map.values())
            
            else:
                # For other types, just remove exact duplicates
                seen = set()
                unique_entities = []
                
                for entity in entity_list:
                    entity_key = str(asdict(entity))
                    if entity_key not in seen:
                        seen.add(entity_key)
                        unique_entities.append(entity)
                
                merged_entities[entity_type] = unique_entities
        
        return merged_entities


class HierarchicalEntityParser(MedicalEntityParser):
    """
    Specialized parser for hierarchical medical device ontology extraction
    """
    
    def __init__(self):
        """Initialize hierarchical parser"""
        super().__init__()
        
        # Hierarchical validation rules
        self.hierarchy_levels = {
            "systems": 1,
            "subsystems": 2, 
            "components": 3,
            "spare_parts": 4
        }
        
        # Relationship validation
        self.valid_relationship_types = [
            "causal", "spatial", "functional", "temporal", "dependency"
        ]
        
        # LINAC subsystem mapping
        self.linac_subsystem_keywords = {
            "BeamDeliverySystem": ["beam", "delivery", "electron", "photon", "target", "waveguide"],
            "PatientPositioningSystem": ["couch", "table", "positioning", "patient", "immobilization"],
            "MLCSystem": ["mlc", "leaf", "collimator", "multi-leaf", "beam shaping"],
            "GantrySystem": ["gantry", "rotation", "angular", "counterweight", "slip ring"],
            "ImagingSystem": ["imaging", "kv", "mv", "cbct", "portal", "detector"],
            "SafetySystem": ["safety", "interlock", "radiation", "monitor", "emergency"],
            "ControlSystem": ["control", "interface", "network", "data", "coordination"]
        }
        
        logger.info("Hierarchical entity parser initialized")
    
    def parse_hierarchical_entities(
        self,
        response: str,
        page_number: int = 0,
        source_text: str = "",
        device_type: str = "linear_accelerator"
    ) -> Dict[str, List[EntityExtraction]]:
        """
        Parse hierarchical entities with validation and relationship mapping
        
        Args:
            response: Gemini response containing hierarchical entities
            page_number: Source page number
            source_text: Original source text
            device_type: Type of medical device
            
        Returns:
            Dictionary of parsed hierarchical entities
        """
        
        logger.info(f"Parsing hierarchical entities for page {page_number}")
        
        try:
            # Parse base entities
            entities = self.parse_gemini_response(response, page_number, source_text)
            
            # Validate hierarchical structure
            entities = self._validate_hierarchical_structure(entities)
            
            # Map subsystem classifications for LINAC
            if device_type == "linear_accelerator":
                entities = self._classify_linac_subsystems(entities)
            
            # Extract and validate relationships
            entities = self._extract_hierarchical_relationships(entities, source_text)
            
            # Perform entity deduplication and merging
            entities = self._deduplicate_hierarchical_entities(entities)
            
            # Calculate confidence scores
            entities = self._calculate_hierarchical_confidence(entities)
            
            logger.info(f"Successfully parsed hierarchical entities: {self._count_entities(entities)}")
            
            return entities
            
        except Exception as e:
            logger.error(f"Error parsing hierarchical entities: {str(e)}")
            return self._create_empty_hierarchical_dict()
    
    def _validate_hierarchical_structure(
        self, 
        entities: Dict[str, List[EntityExtraction]]
    ) -> Dict[str, List[EntityExtraction]]:
        """Validate hierarchical relationships between entities"""
        
        validated_entities = {}
        
        # Create entity lookup maps
        system_names = {e.name for e in entities.get("systems", [])}
        subsystem_names = {e.name for e in entities.get("subsystems", [])}
        component_names = {e.name for e in entities.get("components", [])}
        
        # Validate systems
        validated_entities["systems"] = []
        for system in entities.get("systems", []):
            # Validate subsystem references
            valid_subsystems = [s for s in system.subsystems if s in subsystem_names]
            system.subsystems = valid_subsystems
            validated_entities["systems"].append(system)
        
        # Validate subsystems
        validated_entities["subsystems"] = []
        for subsystem in entities.get("subsystems", []):
            # Validate parent system reference
            if subsystem.parent_system and subsystem.parent_system not in system_names:
                logger.warning(f"Subsystem {subsystem.name} references unknown system {subsystem.parent_system}")
                subsystem.confidence *= 0.8  # Reduce confidence
            
            # Validate component references
            valid_components = [c for c in subsystem.components if c in component_names]
            subsystem.components = valid_components
            validated_entities["subsystems"].append(subsystem)
        
        # Validate components
        validated_entities["components"] = []
        for component in entities.get("components", []):
            # Validate parent subsystem reference
            if component.parent_subsystem and component.parent_subsystem not in subsystem_names:
                logger.warning(f"Component {component.name} references unknown subsystem {component.parent_subsystem}")
                component.confidence *= 0.8
            
            validated_entities["components"].append(component)
        
        # Copy other entity types
        for entity_type in ["spare_parts", "relationships", "error_codes", "procedures", "safety_protocols"]:
            validated_entities[entity_type] = entities.get(entity_type, [])
        
        return validated_entities
    
    def _classify_linac_subsystems(
        self, 
        entities: Dict[str, List[EntityExtraction]]
    ) -> Dict[str, List[EntityExtraction]]:
        """Classify entities into LINAC subsystems based on keywords"""
        
        # Classify subsystems
        for subsystem in entities.get("subsystems", []):
            if subsystem.type == "unknown":
                subsystem.type = self._identify_linac_subsystem_type(subsystem.name, subsystem.function)
        
        # Classify components
        for component in entities.get("components", []):
            if component.parent_subsystem == "unknown":
                component.parent_subsystem = self._identify_component_subsystem(component.name, component.function)
        
        return entities
    
    def _identify_linac_subsystem_type(self, name: str, function: str) -> str:
        """Identify LINAC subsystem type based on name and function"""
        
        text_to_analyze = f"{name} {function}".lower()
        
        best_match = "unknown"
        best_score = 0
        
        for subsystem_type, keywords in self.linac_subsystem_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_to_analyze)
            if score > best_score:
                best_score = score
                best_match = subsystem_type
        
        return best_match if best_score > 0 else "unknown"
    
    def _identify_component_subsystem(self, name: str, function: str) -> str:
        """Identify which subsystem a component belongs to"""
        
        text_to_analyze = f"{name} {function}".lower()
        
        # Direct keyword matching
        if any(keyword in text_to_analyze for keyword in ["mlc", "leaf", "collimator"]):
            return "MLCSystem"
        elif any(keyword in text_to_analyze for keyword in ["couch", "table", "positioning"]):
            return "PatientPositioningSystem"
        elif any(keyword in text_to_analyze for keyword in ["gantry", "rotation"]):
            return "GantrySystem"
        elif any(keyword in text_to_analyze for keyword in ["beam", "target", "waveguide"]):
            return "BeamDeliverySystem"
        elif any(keyword in text_to_analyze for keyword in ["imaging", "detector", "kv", "mv"]):
            return "ImagingSystem"
        elif any(keyword in text_to_analyze for keyword in ["safety", "interlock", "monitor"]):
            return "SafetySystem"
        elif any(keyword in text_to_analyze for keyword in ["control", "interface", "network"]):
            return "ControlSystem"
        
        return "unknown"
    
    def _extract_hierarchical_relationships(
        self, 
        entities: Dict[str, List[EntityExtraction]], 
        source_text: str
    ) -> Dict[str, List[EntityExtraction]]:
        """Extract implicit hierarchical relationships"""
        
        if "relationships" not in entities:
            entities["relationships"] = []
        
        # Extract part_of relationships from hierarchy
        for subsystem in entities.get("subsystems", []):
            if subsystem.parent_system != "unknown":
                relationship = RelationshipEntity(
                    id=str(uuid.uuid4()),
                    source_entity=subsystem.name,
                    target_entity=subsystem.parent_system,
                    relationship_type="spatial",
                    description=f"{subsystem.name} is part of {subsystem.parent_system}",
                    confidence=0.9,
                    source_text=source_text[:200]
                )
                entities["relationships"].append(relationship)
        
        for component in entities.get("components", []):
            if component.parent_subsystem != "unknown":
                relationship = RelationshipEntity(
                    id=str(uuid.uuid4()),
                    source_entity=component.name,
                    target_entity=component.parent_subsystem,
                    relationship_type="spatial",
                    description=f"{component.name} is part of {component.parent_subsystem}",
                    confidence=0.9,
                    source_text=source_text[:200]
                )
                entities["relationships"].append(relationship)
        
        # Extract causal relationships from error codes
        for error_code in entities.get("error_codes", []):
            # Look for components mentioned in error description
            error_text = f"{error_code.description} {error_code.response}".lower()
            
            for component in entities.get("components", []):
                if component.name.lower() in error_text:
                    relationship = RelationshipEntity(
                        id=str(uuid.uuid4()),
                        source_entity=f"Error {error_code.code}",
                        target_entity=component.name,
                        relationship_type="causal",
                        description=f"Error {error_code.code} affects {component.name}",
                        confidence=0.8,
                        source_text=error_text[:200]
                    )
                    entities["relationships"].append(relationship)
        
        return entities
    
    def _deduplicate_hierarchical_entities(
        self, 
        entities: Dict[str, List[EntityExtraction]]
    ) -> Dict[str, List[EntityExtraction]]:
        """Deduplicate entities with hierarchical awareness"""
        
        deduplicated = {}
        
        # Deduplicate by name for hierarchical entities
        for entity_type in ["systems", "subsystems", "components", "spare_parts"]:
            if entity_type not in entities:
                deduplicated[entity_type] = []
                continue
            
            name_map = {}
            for entity in entities[entity_type]:
                name_key = entity.name.lower().strip()
                
                if name_key not in name_map:
                    name_map[name_key] = entity
                else:
                    # Merge entities with same name
                    existing = name_map[name_key]
                    merged = self._merge_similar_entities(existing, entity)
                    name_map[name_key] = merged
            
            deduplicated[entity_type] = list(name_map.values())
        
        # Deduplicate relationships by source-target-type combination
        if "relationships" in entities:
            relationship_map = {}
            for relationship in entities["relationships"]:
                rel_key = f"{relationship.source_entity}|{relationship.target_entity}|{relationship.relationship_type}"
                
                if rel_key not in relationship_map:
                    relationship_map[rel_key] = relationship
                else:
                    # Keep the one with higher confidence
                    if relationship.confidence > relationship_map[rel_key].confidence:
                        relationship_map[rel_key] = relationship
            
            deduplicated["relationships"] = list(relationship_map.values())
        
        # Copy other entity types
        for entity_type in ["error_codes", "procedures", "safety_protocols", "technical_specifications"]:
            deduplicated[entity_type] = entities.get(entity_type, [])
        
        return deduplicated
    
    def _merge_similar_entities(self, entity1: EntityExtraction, entity2: EntityExtraction) -> EntityExtraction:
        """Merge two similar entities, keeping the best information"""
        
        # Keep the entity with higher confidence as base
        if entity2.confidence > entity1.confidence:
            base_entity = entity2
            merge_entity = entity1
        else:
            base_entity = entity1
            merge_entity = entity2
        
        # Merge fields that are "unknown" in base but known in merge
        for field_name in base_entity.__dataclass_fields__:
            base_value = getattr(base_entity, field_name)
            merge_value = getattr(merge_entity, field_name, None)
            
            if base_value == "unknown" and merge_value and merge_value != "unknown":
                setattr(base_entity, field_name, merge_value)
            elif isinstance(base_value, list) and isinstance(merge_value, list):
                # Merge lists, removing duplicates
                merged_list = list(set(base_value + merge_value))
                setattr(base_entity, field_name, merged_list)
        
        # Average confidence scores
        base_entity.confidence = (base_entity.confidence + merge_entity.confidence) / 2
        
        return base_entity
    
    def _calculate_hierarchical_confidence(
        self, 
        entities: Dict[str, List[EntityExtraction]]
    ) -> Dict[str, List[EntityExtraction]]:
        """Calculate confidence scores based on hierarchical consistency"""
        
        # Boost confidence for entities with valid hierarchical relationships
        system_names = {e.name for e in entities.get("systems", [])}
        subsystem_names = {e.name for e in entities.get("subsystems", [])}
        
        # Boost subsystem confidence if parent system exists
        for subsystem in entities.get("subsystems", []):
            if subsystem.parent_system in system_names:
                subsystem.confidence = min(1.0, subsystem.confidence + 0.1)
        
        # Boost component confidence if parent subsystem exists
        for component in entities.get("components", []):
            if component.parent_subsystem in subsystem_names:
                component.confidence = min(1.0, component.confidence + 0.1)
        
        # Boost relationship confidence for hierarchical relationships
        for relationship in entities.get("relationships", []):
            if relationship.relationship_type == "spatial" and "part of" in relationship.description:
                relationship.confidence = min(1.0, relationship.confidence + 0.1)
        
        return entities
    
    def _create_empty_hierarchical_dict(self) -> Dict[str, List[EntityExtraction]]:
        """Create empty hierarchical entity dictionary"""
        
        return {
            "systems": [],
            "subsystems": [],
            "components": [],
            "spare_parts": [],
            "relationships": [],
            "error_codes": [],
            "procedures": [],
            "safety_protocols": [],
            "technical_specifications": []
        }
    
    def extract_entity_confidence_scores(self, entities: Dict[str, List[EntityExtraction]]) -> Dict[str, float]:
        """Calculate overall confidence metrics for extracted entities"""
        
        confidence_scores = {}
        
        for entity_type, entity_list in entities.items():
            if entity_list:
                avg_confidence = sum(e.confidence for e in entity_list) / len(entity_list)
                confidence_scores[entity_type] = round(avg_confidence, 3)
            else:
                confidence_scores[entity_type] = 0.0
        
        # Calculate overall confidence
        all_confidences = [score for score in confidence_scores.values() if score > 0]
        confidence_scores["overall"] = round(sum(all_confidences) / len(all_confidences), 3) if all_confidences else 0.0
        
        return confidence_scores


# Utility functions

def create_sample_entities() -> Dict[str, List[EntityExtraction]]:
    """Create sample entities for testing"""
    
    sample_entities = {
        "error_codes": [
            ErrorCodeEntity(
                id="ec_001",
                code="7002",
                software_release="R6.0x, R6.1x, R7.0x\Integrity™ R1.1",
                message="MOVEMENT",
                description="The actual direction of movement of a leaf does not match the expected direction",
                response="Check the drive to the leaf motors and the leaves for free movement",
                category="Mechanical",
                severity="High",
                confidence=0.95
            )
        ],
        "components": [
            ComponentEntity(
                id="comp_001",
                name="Leaf Motor Assembly",
                type="Actuator",
                function="Control individual leaf positions",
                parent_system="MLC System",
                specifications="Stepper motor",
                confidence=0.90
            )
        ],
        "procedures": [],
        "safety_protocols": [],
        "technical_specifications": []
    }
    
    return sample_entities


if __name__ == "__main__":
    # Test the parser
    parser = MedicalEntityParser()
    
    # Test JSON response parsing
    json_response = '''
    {
        "error_codes": [
            {
                "code": "7002",
                "software_release": "R6.0x, R6.1x, R7.0x\\Integrity™ R1.1",
                "message": "MOVEMENT",
                "description": "The actual direction of movement of a leaf does not match the expected direction",
                "response": "Check the drive to the leaf motors and the leaves for free movement",
                "category": "Mechanical",
                "severity": "High",
                "confidence": 0.95
            }
        ],
        "components": [],
        "procedures": [],
        "safety_protocols": []
    }
    '''
    
    entities = parser.parse_gemini_response(json_response, page_number=1)
    
    print("✅ Parser test completed!")
    print(f"📊 Total entities parsed: {parser._count_entities(entities)}")
    
    for entity_type, entity_list in entities.items():
        print(f"  - {entity_type}: {len(entity_list)} entities")