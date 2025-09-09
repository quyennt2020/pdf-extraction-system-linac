"""
Ontology Concept Mapper for Medical Device Entities
Maps extracted entities to standard medical device ontology concepts
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from loguru import logger
import uuid
from datetime import datetime


@dataclass
class OntologyConcept:
    """Standard ontology concept"""
    concept_id: str
    concept_name: str
    concept_type: str
    namespace: str
    definition: str = "unknown"
    synonyms: List[str] = None
    parent_concepts: List[str] = None
    
    def __post_init__(self):
        if self.synonyms is None:
            self.synonyms = []
        if self.parent_concepts is None:
            self.parent_concepts = []


@dataclass
class ConceptMapping:
    """Mapping between extracted entity and ontology concept"""
    entity_id: str
    entity_name: str
    entity_type: str
    concept_id: str
    concept_name: str
    mapping_confidence: float
    mapping_type: str  # exact_match, partial_match, inferred, manual
    evidence: str = "unknown"
    validation_status: str = "pending"  # pending, approved, rejected
    mapped_by: str = "system"
    mapping_timestamp: float = 0.0
    
    def __post_init__(self):
        if not self.mapping_timestamp:
            self.mapping_timestamp = datetime.now().timestamp()


class MedicalDeviceOntologyMapper:
    """
    Maps extracted medical device entities to standard ontology concepts
    Supports UMLS, SNOMED CT, and IEC 60601 standards
    """
    
    def __init__(self):
        """Initialize ontology mapper"""
        
        # Medical device ontology concepts
        self.medical_device_concepts = self._load_medical_device_concepts()
        
        # UMLS terminology mappings
        self.umls_mappings = self._load_umls_mappings()
        
        # SNOMED CT mappings
        self.snomed_mappings = self._load_snomed_mappings()
        
        # IEC 60601 compliance mappings
        self.iec_60601_mappings = self._load_iec_60601_mappings()
        
        # Concept similarity thresholds
        self.similarity_thresholds = {
            "exact_match": 0.95,
            "partial_match": 0.8,
            "inferred": 0.6,
            "minimum": 0.5
        }
        
        logger.info("Medical device ontology mapper initialized")
    
    def map_entities_to_concepts(
        self,
        entities: Dict[str, List[Any]],
        device_type: str = "linear_accelerator"
    ) -> Dict[str, List[ConceptMapping]]:
        """
        Map extracted entities to standard ontology concepts
        
        Args:
            entities: Dictionary of extracted entities
            device_type: Type of medical device
            
        Returns:
            Dictionary of concept mappings by entity type
        """
        
        logger.info(f"Starting ontology concept mapping for {device_type}")
        
        mappings = {}
        
        # Map each entity type
        for entity_type, entity_list in entities.items():
            if entity_type == "extraction_metadata":
                continue
            
            mappings[entity_type] = []
            
            for entity in entity_list:
                entity_mappings = self._map_single_entity(entity, entity_type, device_type)
                mappings[entity_type].extend(entity_mappings)
        
        # Validate mappings
        mappings = self._validate_concept_mappings(mappings)
        
        logger.info(f"Completed ontology mapping: {self._count_mappings(mappings)} total mappings")
        
        return mappings
    
    def _map_single_entity(
        self,
        entity: Any,
        entity_type: str,
        device_type: str
    ) -> List[ConceptMapping]:
        """Map a single entity to ontology concepts"""
        
        mappings = []
        
        # Get entity name and properties
        entity_name = getattr(entity, 'name', getattr(entity, 'code', 'unknown'))
        entity_id = getattr(entity, 'id', str(uuid.uuid4()))
        
        # Try different mapping strategies
        
        # 1. Exact match in medical device concepts
        exact_matches = self._find_exact_matches(entity_name, entity_type, device_type)
        for concept in exact_matches:
            mapping = ConceptMapping(
                entity_id=entity_id,
                entity_name=entity_name,
                entity_type=entity_type,
                concept_id=concept.concept_id,
                concept_name=concept.concept_name,
                mapping_confidence=0.95,
                mapping_type="exact_match",
                evidence=f"Exact match in {concept.namespace}"
            )
            mappings.append(mapping)
        
        # 2. Partial match using synonyms
        if not exact_matches:
            partial_matches = self._find_partial_matches(entity_name, entity_type, device_type)
            for concept, confidence in partial_matches:
                mapping = ConceptMapping(
                    entity_id=entity_id,
                    entity_name=entity_name,
                    entity_type=entity_type,
                    concept_id=concept.concept_id,
                    concept_name=concept.concept_name,
                    mapping_confidence=confidence,
                    mapping_type="partial_match",
                    evidence=f"Partial match in {concept.namespace}"
                )
                mappings.append(mapping)
        
        # 3. UMLS terminology mapping
        umls_mappings = self._map_to_umls(entity_name, entity_type)
        mappings.extend(umls_mappings)
        
        # 4. SNOMED CT mapping
        snomed_mappings = self._map_to_snomed(entity_name, entity_type)
        mappings.extend(snomed_mappings)
        
        # 5. IEC 60601 compliance mapping
        iec_mappings = self._map_to_iec_60601(entity, entity_type)
        mappings.extend(iec_mappings)
        
        return mappings
    
    def _find_exact_matches(
        self,
        entity_name: str,
        entity_type: str,
        device_type: str
    ) -> List[OntologyConcept]:
        """Find exact matches in medical device concepts"""
        
        matches = []
        
        # Normalize entity name
        normalized_name = self._normalize_concept_name(entity_name)
        
        # Search in device-specific concepts
        device_concepts = self.medical_device_concepts.get(device_type, {})
        type_concepts = device_concepts.get(entity_type, [])
        
        for concept in type_concepts:
            # Check exact match
            if normalized_name == self._normalize_concept_name(concept.concept_name):
                matches.append(concept)
                continue
            
            # Check synonyms
            for synonym in concept.synonyms:
                if normalized_name == self._normalize_concept_name(synonym):
                    matches.append(concept)
                    break
        
        return matches
    
    def _find_partial_matches(
        self,
        entity_name: str,
        entity_type: str,
        device_type: str
    ) -> List[Tuple[OntologyConcept, float]]:
        """Find partial matches using similarity scoring"""
        
        matches = []
        
        # Normalize entity name
        normalized_name = self._normalize_concept_name(entity_name)
        
        # Search in device-specific concepts
        device_concepts = self.medical_device_concepts.get(device_type, {})
        type_concepts = device_concepts.get(entity_type, [])
        
        for concept in type_concepts:
            # Calculate similarity with concept name
            similarity = self._calculate_name_similarity(normalized_name, concept.concept_name)
            
            if similarity >= self.similarity_thresholds["minimum"]:
                matches.append((concept, similarity))
            
            # Check synonyms
            for synonym in concept.synonyms:
                synonym_similarity = self._calculate_name_similarity(normalized_name, synonym)
                if synonym_similarity >= self.similarity_thresholds["minimum"]:
                    matches.append((concept, synonym_similarity))
        
        # Sort by similarity score
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # Return top matches above threshold
        return [(concept, score) for concept, score in matches if score >= self.similarity_thresholds["partial_match"]]
    
    def _map_to_umls(self, entity_name: str, entity_type: str) -> List[ConceptMapping]:
        """Map entity to UMLS terminology"""
        
        mappings = []
        
        # Normalize entity name
        normalized_name = self._normalize_concept_name(entity_name)
        
        # Search UMLS mappings
        for umls_concept in self.umls_mappings.get(entity_type, []):
            similarity = self._calculate_name_similarity(normalized_name, umls_concept["name"])
            
            if similarity >= self.similarity_thresholds["partial_match"]:
                mapping = ConceptMapping(
                    entity_id=str(uuid.uuid4()),
                    entity_name=entity_name,
                    entity_type=entity_type,
                    concept_id=umls_concept["cui"],
                    concept_name=umls_concept["name"],
                    mapping_confidence=similarity,
                    mapping_type="partial_match" if similarity >= self.similarity_thresholds["partial_match"] else "inferred",
                    evidence=f"UMLS mapping: {umls_concept['semantic_type']}"
                )
                mappings.append(mapping)
        
        return mappings
    
    def _map_to_snomed(self, entity_name: str, entity_type: str) -> List[ConceptMapping]:
        """Map entity to SNOMED CT terminology"""
        
        mappings = []
        
        # Normalize entity name
        normalized_name = self._normalize_concept_name(entity_name)
        
        # Search SNOMED mappings
        for snomed_concept in self.snomed_mappings.get(entity_type, []):
            similarity = self._calculate_name_similarity(normalized_name, snomed_concept["term"])
            
            if similarity >= self.similarity_thresholds["partial_match"]:
                mapping = ConceptMapping(
                    entity_id=str(uuid.uuid4()),
                    entity_name=entity_name,
                    entity_type=entity_type,
                    concept_id=snomed_concept["sctid"],
                    concept_name=snomed_concept["term"],
                    mapping_confidence=similarity,
                    mapping_type="partial_match" if similarity >= self.similarity_thresholds["partial_match"] else "inferred",
                    evidence=f"SNOMED CT mapping: {snomed_concept['hierarchy']}"
                )
                mappings.append(mapping)
        
        return mappings
    
    def _map_to_iec_60601(self, entity: Any, entity_type: str) -> List[ConceptMapping]:
        """Map entity to IEC 60601 compliance concepts"""
        
        mappings = []
        
        # Get entity properties
        entity_name = getattr(entity, 'name', getattr(entity, 'code', 'unknown'))
        entity_id = getattr(entity, 'id', str(uuid.uuid4()))
        
        # Check IEC 60601 compliance mappings
        for iec_concept in self.iec_60601_mappings.get(entity_type, []):
            # Check if entity matches IEC concept criteria
            if self._matches_iec_criteria(entity, iec_concept):
                mapping = ConceptMapping(
                    entity_id=entity_id,
                    entity_name=entity_name,
                    entity_type=entity_type,
                    concept_id=iec_concept["standard_id"],
                    concept_name=iec_concept["standard_name"],
                    mapping_confidence=0.9,
                    mapping_type="exact_match",
                    evidence=f"IEC 60601 compliance: {iec_concept['section']}"
                )
                mappings.append(mapping)
        
        return mappings
    
    def _matches_iec_criteria(self, entity: Any, iec_concept: Dict[str, Any]) -> bool:
        """Check if entity matches IEC 60601 criteria"""
        
        # Get entity text for analysis
        entity_text = ""
        if hasattr(entity, 'name'):
            entity_text += entity.name + " "
        if hasattr(entity, 'description'):
            entity_text += entity.description + " "
        if hasattr(entity, 'function'):
            entity_text += entity.function + " "
        
        entity_text = entity_text.lower()
        
        # Check if any IEC keywords match
        for keyword in iec_concept.get("keywords", []):
            if keyword.lower() in entity_text:
                return True
        
        return False
    
    def _validate_concept_mappings(
        self,
        mappings: Dict[str, List[ConceptMapping]]
    ) -> Dict[str, List[ConceptMapping]]:
        """Validate and filter concept mappings"""
        
        validated_mappings = {}
        
        for entity_type, mapping_list in mappings.items():
            validated_list = []
            
            # Group mappings by entity
            entity_mappings = {}
            for mapping in mapping_list:
                entity_key = f"{mapping.entity_id}_{mapping.entity_name}"
                if entity_key not in entity_mappings:
                    entity_mappings[entity_key] = []
                entity_mappings[entity_key].append(mapping)
            
            # Select best mappings for each entity
            for entity_key, entity_mapping_list in entity_mappings.items():
                # Sort by confidence
                entity_mapping_list.sort(key=lambda x: x.mapping_confidence, reverse=True)
                
                # Take top 3 mappings above minimum threshold
                best_mappings = [
                    m for m in entity_mapping_list[:3] 
                    if m.mapping_confidence >= self.similarity_thresholds["minimum"]
                ]
                
                validated_list.extend(best_mappings)
            
            validated_mappings[entity_type] = validated_list
        
        return validated_mappings
    
    def _normalize_concept_name(self, name: str) -> str:
        """Normalize concept name for comparison"""
        
        if not name or name == "unknown":
            return ""
        
        # Convert to lowercase
        normalized = name.lower()
        
        # Remove special characters
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Remove common prefixes/suffixes
        prefixes = ['the ', 'a ', 'an ']
        suffixes = [' system', ' assembly', ' unit', ' device']
        
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
        
        return normalized.strip()
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two concept names"""
        
        # Normalize both names
        norm1 = self._normalize_concept_name(name1)
        norm2 = self._normalize_concept_name(name2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Exact match
        if norm1 == norm2:
            return 1.0
        
        # Jaccard similarity on words
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # Substring similarity
        substring_similarity = 0.0
        if norm1 in norm2 or norm2 in norm1:
            substring_similarity = 0.3
        
        # Combined similarity
        return min(1.0, jaccard_similarity + substring_similarity)
    
    def _count_mappings(self, mappings: Dict[str, List[ConceptMapping]]) -> int:
        """Count total number of mappings"""
        
        return sum(len(mapping_list) for mapping_list in mappings.values())
    
    def _load_medical_device_concepts(self) -> Dict[str, Dict[str, List[OntologyConcept]]]:
        """Load medical device ontology concepts"""
        
        # LINAC-specific concepts
        linac_concepts = {
            "systems": [
                OntologyConcept(
                    concept_id="MDO:0001",
                    concept_name="Linear Accelerator System",
                    concept_type="MedicalDevice",
                    namespace="medical_device_ontology",
                    definition="Medical linear accelerator for radiation therapy",
                    synonyms=["LINAC", "Linear Accelerator", "Medical Accelerator"]
                )
            ],
            "subsystems": [
                OntologyConcept(
                    concept_id="MDO:0010",
                    concept_name="Beam Delivery System",
                    concept_type="Subsystem",
                    namespace="medical_device_ontology",
                    definition="System responsible for generating and delivering therapeutic radiation beam",
                    synonyms=["Beam Generation System", "Radiation Delivery System"]
                ),
                OntologyConcept(
                    concept_id="MDO:0011",
                    concept_name="Multi-Leaf Collimator System",
                    concept_type="Subsystem",
                    namespace="medical_device_ontology",
                    definition="System for shaping radiation beam using movable leaves",
                    synonyms=["MLC System", "MLCi System", "Beam Shaping System"]
                ),
                OntologyConcept(
                    concept_id="MDO:0012",
                    concept_name="Patient Positioning System",
                    concept_type="Subsystem",
                    namespace="medical_device_ontology",
                    definition="System for positioning and immobilizing patients during treatment",
                    synonyms=["Couch System", "Treatment Table System", "Patient Support System"]
                ),
                OntologyConcept(
                    concept_id="MDO:0013",
                    concept_name="Gantry System",
                    concept_type="Subsystem",
                    namespace="medical_device_ontology",
                    definition="System for rotating treatment head around patient",
                    synonyms=["Gantry Rotation System", "Angular Positioning System"]
                )
            ],
            "components": [
                OntologyConcept(
                    concept_id="MDO:0100",
                    concept_name="Leaf Motor",
                    concept_type="Component",
                    namespace="medical_device_ontology",
                    definition="Motor for controlling individual MLC leaf position",
                    synonyms=["MLC Motor", "Leaf Drive Motor", "Collimator Motor"]
                ),
                OntologyConcept(
                    concept_id="MDO:0101",
                    concept_name="Position Sensor",
                    concept_type="Component",
                    namespace="medical_device_ontology",
                    definition="Sensor for monitoring component position",
                    synonyms=["Encoder", "Position Feedback", "Position Monitor"]
                ),
                OntologyConcept(
                    concept_id="MDO:0102",
                    concept_name="Servo Motor",
                    concept_type="Component",
                    namespace="medical_device_ontology",
                    definition="Precision motor for controlled movement",
                    synonyms=["Servo Drive", "Precision Motor", "Control Motor"]
                )
            ],
            "error_codes": [
                OntologyConcept(
                    concept_id="MDO:7002",
                    concept_name="Movement Error",
                    concept_type="ErrorCode",
                    namespace="medical_device_ontology",
                    definition="Error indicating incorrect component movement",
                    synonyms=["Motion Error", "Movement Fault", "Position Error"]
                )
            ]
        }
        
        return {
            "linear_accelerator": linac_concepts
        }
    
    def _load_umls_mappings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load UMLS terminology mappings"""
        
        return {
            "components": [
                {
                    "cui": "C0025080",
                    "name": "Medical Device",
                    "semantic_type": "Medical Device"
                },
                {
                    "cui": "C0025369", 
                    "name": "Motor",
                    "semantic_type": "Manufactured Object"
                },
                {
                    "cui": "C0183210",
                    "name": "Sensor",
                    "semantic_type": "Medical Device"
                }
            ],
            "procedures": [
                {
                    "cui": "C0024501",
                    "name": "Maintenance",
                    "semantic_type": "Health Care Activity"
                },
                {
                    "cui": "C0006751",
                    "name": "Calibration",
                    "semantic_type": "Health Care Activity"
                }
            ]
        }
    
    def _load_snomed_mappings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load SNOMED CT terminology mappings"""
        
        return {
            "components": [
                {
                    "sctid": "49062001",
                    "term": "Device",
                    "hierarchy": "Physical object > Manufactured object > Device"
                },
                {
                    "sctid": "360030002",
                    "term": "Medical equipment",
                    "hierarchy": "Physical object > Manufactured object > Device > Medical equipment"
                }
            ],
            "procedures": [
                {
                    "sctid": "387713003",
                    "term": "Surgical procedure",
                    "hierarchy": "Procedure > Surgical procedure"
                }
            ]
        }
    
    def _load_iec_60601_mappings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load IEC 60601 compliance mappings"""
        
        return {
            "safety_protocols": [
                {
                    "standard_id": "IEC60601-1",
                    "standard_name": "General requirements for basic safety and essential performance",
                    "section": "General Safety",
                    "keywords": ["safety", "interlock", "emergency", "protection"]
                },
                {
                    "standard_id": "IEC60601-2-1",
                    "standard_name": "Particular requirements for electron accelerators",
                    "section": "Electron Accelerator Safety",
                    "keywords": ["electron", "accelerator", "beam", "radiation"]
                }
            ],
            "components": [
                {
                    "standard_id": "IEC60601-1-8",
                    "standard_name": "Alarm systems",
                    "section": "Alarm Requirements",
                    "keywords": ["alarm", "monitor", "alert", "warning"]
                }
            ]
        }


# Utility functions

def create_concept_mapping_report(mappings: Dict[str, List[ConceptMapping]]) -> Dict[str, Any]:
    """Create a summary report of concept mappings"""
    
    report = {
        "total_mappings": 0,
        "mapping_types": {},
        "confidence_distribution": {},
        "entity_coverage": {},
        "validation_status": {}
    }
    
    all_mappings = []
    for mapping_list in mappings.values():
        all_mappings.extend(mapping_list)
    
    report["total_mappings"] = len(all_mappings)
    
    # Count mapping types
    for mapping in all_mappings:
        mapping_type = mapping.mapping_type
        report["mapping_types"][mapping_type] = report["mapping_types"].get(mapping_type, 0) + 1
    
    # Confidence distribution
    confidence_ranges = [(0.9, 1.0), (0.8, 0.9), (0.7, 0.8), (0.6, 0.7), (0.5, 0.6)]
    for min_conf, max_conf in confidence_ranges:
        range_key = f"{min_conf}-{max_conf}"
        count = sum(1 for m in all_mappings if min_conf <= m.mapping_confidence < max_conf)
        report["confidence_distribution"][range_key] = count
    
    # Entity coverage
    for entity_type, mapping_list in mappings.items():
        unique_entities = len(set(m.entity_name for m in mapping_list))
        report["entity_coverage"][entity_type] = unique_entities
    
    # Validation status
    for mapping in all_mappings:
        status = mapping.validation_status
        report["validation_status"][status] = report["validation_status"].get(status, 0) + 1
    
    return report


if __name__ == "__main__":
    # Test the ontology mapper
    
    # Create sample entities
    from .entity_parser import create_sample_entities
    
    mapper = MedicalDeviceOntologyMapper()
    sample_entities = create_sample_entities()
    
    # Map entities to concepts
    mappings = mapper.map_entities_to_concepts(sample_entities, "linear_accelerator")
    
    # Generate report
    report = create_concept_mapping_report(mappings)
    
    print("✅ Ontology mapper test completed!")
    print(f"📊 Total mappings: {report['total_mappings']}")
    print(f"🎯 Mapping types: {report['mapping_types']}")
    print(f"📈 Entity coverage: {report['entity_coverage']}")