"""
Hierarchical Medical Entity Extractor
Integrates Gemini prompts, entity parsing, and ontology mapping for hierarchical extraction
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from loguru import logger
import time

from .gemini_client import GeminiClient, ExtractionConfig
from .entity_parser import HierarchicalEntityParser
from .ontology_mapper import MedicalDeviceOntologyMapper, create_concept_mapping_report


class HierarchicalEntityExtractor:
    """
    Main class for hierarchical medical device entity extraction
    Combines AI extraction, parsing, and ontology mapping
    """
    
    def __init__(self, api_key: str = None, config: ExtractionConfig = None):
        """Initialize hierarchical extractor"""
        
        # Initialize components
        self.gemini_client = GeminiClient(api_key=api_key, config=config)
        self.entity_parser = HierarchicalEntityParser()
        self.ontology_mapper = MedicalDeviceOntologyMapper()
        
        logger.info("Hierarchical entity extractor initialized")
    
    async def extract_hierarchical_entities(
        self,
        page_content: str,
        device_type: str = "linear_accelerator",
        focus_subsystem: str = None,
        page_number: int = 0
    ) -> Dict[str, Any]:
        """
        Extract hierarchical entities from page content
        
        Args:
            page_content: Text content to analyze
            device_type: Type of medical device
            focus_subsystem: Specific subsystem to focus on
            page_number: Source page number
            
        Returns:
            Complete hierarchical extraction result
        """
        
        logger.info(f"Starting hierarchical extraction for page {page_number}")
        
        try:
            # Step 1: Extract entities using Gemini
            raw_entities = await self.gemini_client.extract_medical_entities(
                page_content=page_content,
                device_type=device_type,
                hierarchical_mode=True,
                focus_subsystem=focus_subsystem
            )
            
            # Step 2: Parse and structure entities
            parsed_entities = self.entity_parser.parse_hierarchical_entities(
                response=str(raw_entities),
                page_number=page_number,
                source_text=page_content,
                device_type=device_type
            )
            
            # Step 3: Map to ontology concepts
            concept_mappings = self.ontology_mapper.map_entities_to_concepts(
                entities=parsed_entities,
                device_type=device_type
            )
            
            # Step 4: Generate confidence scores
            confidence_scores = self.entity_parser.extract_entity_confidence_scores(parsed_entities)
            
            # Step 5: Create mapping report
            mapping_report = create_concept_mapping_report(concept_mappings)
            
            # Compile results
            result = {
                "entities": self._convert_entities_to_dict(parsed_entities),
                "concept_mappings": self._convert_mappings_to_dict(concept_mappings),
                "confidence_scores": confidence_scores,
                "mapping_report": mapping_report,
                "extraction_metadata": {
                    "page_number": page_number,
                    "device_type": device_type,
                    "focus_subsystem": focus_subsystem,
                    "extraction_timestamp": time.time(),
                    "content_length": len(page_content),
                    "total_entities": sum(len(entity_list) for entity_list in parsed_entities.values()),
                    "total_mappings": mapping_report["total_mappings"]
                }
            }
            
            logger.info(f"Hierarchical extraction completed: {result['extraction_metadata']['total_entities']} entities, {result['extraction_metadata']['total_mappings']} mappings")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in hierarchical extraction: {str(e)}")
            raise
    
    async def extract_subsystem_specific(
        self,
        page_content: str,
        subsystem_name: str,
        device_type: str = "linear_accelerator",
        page_number: int = 0
    ) -> Dict[str, Any]:
        """
        Extract entities specific to a particular subsystem
        
        Args:
            page_content: Text content to analyze
            subsystem_name: Name of the subsystem to focus on
            device_type: Type of medical device
            page_number: Source page number
            
        Returns:
            Subsystem-specific extraction result
        """
        
        logger.info(f"Starting subsystem-specific extraction for {subsystem_name}")
        
        try:
            # Extract subsystem entities using Gemini
            subsystem_entities = await self.gemini_client.extract_subsystem_entities(
                page_content=page_content,
                subsystem_name=subsystem_name,
                device_type=device_type
            )
            
            # Parse entities
            parsed_entities = self.entity_parser.parse_gemini_response(
                response=str(subsystem_entities),
                page_number=page_number,
                source_text=page_content
            )
            
            # Map to ontology concepts
            concept_mappings = self.ontology_mapper.map_entities_to_concepts(
                entities=parsed_entities,
                device_type=device_type
            )
            
            # Generate confidence scores
            confidence_scores = self.entity_parser.extract_entity_confidence_scores(parsed_entities)
            
            result = {
                "subsystem": subsystem_name,
                "entities": self._convert_entities_to_dict(parsed_entities),
                "concept_mappings": self._convert_mappings_to_dict(concept_mappings),
                "confidence_scores": confidence_scores,
                "extraction_metadata": {
                    "page_number": page_number,
                    "device_type": device_type,
                    "target_subsystem": subsystem_name,
                    "extraction_timestamp": time.time(),
                    "content_length": len(page_content)
                }
            }
            
            logger.info(f"Subsystem extraction completed for {subsystem_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in subsystem extraction: {str(e)}")
            raise
    
    async def extract_entity_relationships(
        self,
        entities: List[Dict[str, Any]],
        context_text: str,
        device_type: str = "linear_accelerator"
    ) -> Dict[str, Any]:
        """
        Extract relationships between entities
        
        Args:
            entities: List of extracted entities
            context_text: Original text context
            device_type: Type of medical device
            
        Returns:
            Relationship extraction result
        """
        
        logger.info(f"Starting relationship extraction for {len(entities)} entities")
        
        try:
            # Extract relationships using Gemini
            relationships = await self.gemini_client.extract_entity_relationships(
                entities=entities,
                context_text=context_text,
                device_type=device_type
            )
            
            # Parse relationships
            parsed_relationships = self.entity_parser.parse_gemini_response(
                response=str(relationships),
                source_text=context_text
            )
            
            result = {
                "relationships": self._convert_entities_to_dict(parsed_relationships),
                "extraction_metadata": {
                    "device_type": device_type,
                    "entity_count": len(entities),
                    "extraction_timestamp": time.time(),
                    "context_length": len(context_text)
                }
            }
            
            logger.info(f"Relationship extraction completed: {len(parsed_relationships.get('relationships', []))} relationships")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in relationship extraction: {str(e)}")
            raise
    
    async def batch_hierarchical_extraction(
        self,
        pages: List[str],
        device_type: str = "linear_accelerator",
        focus_subsystem: str = None
    ) -> List[Dict[str, Any]]:
        """
        Extract hierarchical entities from multiple pages
        
        Args:
            pages: List of page contents
            device_type: Type of medical device
            focus_subsystem: Specific subsystem to focus on
            
        Returns:
            List of extraction results for each page
        """
        
        logger.info(f"Starting batch hierarchical extraction for {len(pages)} pages")
        
        results = []
        
        for i, page_content in enumerate(pages):
            try:
                logger.info(f"Processing page {i+1}/{len(pages)}")
                
                result = await self.extract_hierarchical_entities(
                    page_content=page_content,
                    device_type=device_type,
                    focus_subsystem=focus_subsystem,
                    page_number=i + 1
                )
                
                results.append(result)
                
                # Add delay to respect rate limits
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing page {i+1}: {str(e)}")
                results.append({
                    "page_number": i + 1,
                    "error": str(e),
                    "extraction_metadata": {
                        "timestamp": time.time(),
                        "status": "failed"
                    }
                })
        
        logger.info(f"Batch hierarchical extraction completed: {len(results)} pages processed")
        
        return results
    
    def merge_extraction_results(
        self,
        results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge multiple extraction results into a unified ontology
        
        Args:
            results: List of extraction results from different pages
            
        Returns:
            Merged extraction result
        """
        
        logger.info(f"Merging {len(results)} extraction results")
        
        merged_entities = {}
        merged_mappings = {}
        all_confidence_scores = []
        
        # Merge entities from all results
        for result in results:
            if "error" in result:
                continue
            
            entities = result.get("entities", {})
            mappings = result.get("concept_mappings", {})
            confidence = result.get("confidence_scores", {})
            
            # Merge entities
            for entity_type, entity_list in entities.items():
                if entity_type not in merged_entities:
                    merged_entities[entity_type] = []
                merged_entities[entity_type].extend(entity_list)
            
            # Merge mappings
            for entity_type, mapping_list in mappings.items():
                if entity_type not in merged_mappings:
                    merged_mappings[entity_type] = []
                merged_mappings[entity_type].extend(mapping_list)
            
            # Collect confidence scores
            if confidence:
                all_confidence_scores.append(confidence)
        
        # Deduplicate merged entities
        merged_entities = self._deduplicate_merged_entities(merged_entities)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(all_confidence_scores)
        
        # Generate final mapping report
        final_mapping_report = create_concept_mapping_report(merged_mappings)
        
        merged_result = {
            "entities": merged_entities,
            "concept_mappings": merged_mappings,
            "confidence_scores": overall_confidence,
            "mapping_report": final_mapping_report,
            "extraction_metadata": {
                "total_pages": len(results),
                "successful_pages": len([r for r in results if "error" not in r]),
                "merge_timestamp": time.time(),
                "total_entities": sum(len(entity_list) for entity_list in merged_entities.values()),
                "total_mappings": final_mapping_report["total_mappings"]
            }
        }
        
        logger.info(f"Merge completed: {merged_result['extraction_metadata']['total_entities']} entities, {merged_result['extraction_metadata']['total_mappings']} mappings")
        
        return merged_result
    
    def _convert_entities_to_dict(self, entities: Dict[str, List[Any]]) -> Dict[str, List[Dict]]:
        """Convert entity objects to dictionary format"""
        
        dict_entities = {}
        
        for entity_type, entity_list in entities.items():
            dict_entities[entity_type] = []
            
            for entity in entity_list:
                if hasattr(entity, '__dict__'):
                    entity_dict = asdict(entity)
                elif isinstance(entity, dict):
                    entity_dict = entity
                else:
                    entity_dict = {"value": str(entity)}
                
                dict_entities[entity_type].append(entity_dict)
        
        return dict_entities
    
    def _convert_mappings_to_dict(self, mappings: Dict[str, List[Any]]) -> Dict[str, List[Dict]]:
        """Convert mapping objects to dictionary format"""
        
        dict_mappings = {}
        
        for entity_type, mapping_list in mappings.items():
            dict_mappings[entity_type] = []
            
            for mapping in mapping_list:
                if hasattr(mapping, '__dict__'):
                    mapping_dict = asdict(mapping)
                elif isinstance(mapping, dict):
                    mapping_dict = mapping
                else:
                    mapping_dict = {"value": str(mapping)}
                
                dict_mappings[entity_type].append(mapping_dict)
        
        return dict_mappings
    
    def _deduplicate_merged_entities(self, entities: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Deduplicate entities across merged results"""
        
        deduplicated = {}
        
        for entity_type, entity_list in entities.items():
            seen_entities = {}
            
            for entity in entity_list:
                # Create unique key based on name/code and type
                entity_name = entity.get('name', entity.get('code', 'unknown'))
                entity_key = f"{entity_name}_{entity.get('type', 'unknown')}".lower()
                
                if entity_key not in seen_entities:
                    seen_entities[entity_key] = entity
                else:
                    # Keep the one with higher confidence
                    existing_confidence = seen_entities[entity_key].get('confidence', 0)
                    new_confidence = entity.get('confidence', 0)
                    
                    if new_confidence > existing_confidence:
                        seen_entities[entity_key] = entity
            
            deduplicated[entity_type] = list(seen_entities.values())
        
        return deduplicated
    
    def _calculate_overall_confidence(self, confidence_scores: List[Dict[str, float]]) -> Dict[str, float]:
        """Calculate overall confidence scores from multiple results"""
        
        if not confidence_scores:
            return {}
        
        # Aggregate confidence scores
        aggregated = {}
        
        for scores in confidence_scores:
            for entity_type, confidence in scores.items():
                if entity_type not in aggregated:
                    aggregated[entity_type] = []
                aggregated[entity_type].append(confidence)
        
        # Calculate averages
        overall_confidence = {}
        for entity_type, confidence_list in aggregated.items():
            overall_confidence[entity_type] = round(sum(confidence_list) / len(confidence_list), 3)
        
        return overall_confidence


# Utility functions

async def test_hierarchical_extraction(api_key: str = None) -> Dict[str, Any]:
    """Test hierarchical extraction with sample content"""
    
    extractor = HierarchicalEntityExtractor(api_key=api_key)
    
    sample_content = """
    Error Code 7002: MOVEMENT
    Software Release: R6.0x, R6.1x, R7.0x\\Integrity™ R1.1
    Description: The actual direction of movement of a leaf does not match the expected direction.
    Response: Check the drive to the leaf motors and the leaves for free movement.
    
    The MLC system consists of multiple subsystems including the leaf motor assembly,
    position feedback sensors, and the MLC controller. Each leaf motor controls the
    position of individual collimator leaves for precise beam shaping.
    
    The beam delivery system includes the electron gun, accelerating waveguide,
    and target assembly for photon beam generation.
    """
    
    try:
        result = await extractor.extract_hierarchical_entities(
            page_content=sample_content,
            device_type="linear_accelerator",
            page_number=1
        )
        
        return {
            "success": True,
            "result": result,
            "entities_found": result["extraction_metadata"]["total_entities"],
            "mappings_found": result["extraction_metadata"]["total_mappings"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the hierarchical extractor
    
    async def main():
        test_result = await test_hierarchical_extraction()
        
        if test_result["success"]:
            print("✅ Hierarchical extraction test successful!")
            print(f"📊 Entities found: {test_result['entities_found']}")
            print(f"🎯 Mappings found: {test_result['mappings_found']}")
        else:
            print("❌ Hierarchical extraction test failed!")
            print(f"💥 Error: {test_result['error']}")
    
    asyncio.run(main())