"""
LINAC Extractor - Specialized LangExtract wrapper for Linear Accelerator systems

This module provides a high-level interface specifically designed for LINAC 
medical device service manual processing with ontology construction capabilities.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json
import logging
from pathlib import Path

from .langextract_bridge import LangExtractBridge, ExtractionConfig
from .medical_schema_builder import MedicalSchemaBuilder
from backend.core.ontology_builder import OntologyBuilder, OWLOntology
from backend.models.entity import Entity, EntityType, ComponentType


logger = logging.getLogger(__name__)


@dataclass
class LinacExtractionConfig:
    """Configuration specific to LINAC extraction"""
    # LangExtract settings
    model_id: str = "gemini-2.5-flash"
    extraction_passes: int = 3
    max_workers: int = 15
    max_char_buffer: int = 1200
    temperature: float = 0.2
    
    # LINAC specific settings
    focus_subsystems: List[str] = None
    enable_hierarchical_extraction: bool = True
    enable_relationship_extraction: bool = True
    confidence_threshold: float = 0.7
    
    # Output settings
    save_intermediate_results: bool = True
    generate_visualizations: bool = True
    create_ontology: bool = True


class LinacExtractor:
    """
    High-level LINAC-specific extractor using LangExtract
    
    This class orchestrates the entire extraction pipeline from PDF content
    to structured ontology, with specialized handling for LINAC systems.
    """
    
    def __init__(self, config: LinacExtractionConfig = None, api_key: str = None):
        self.config = config or LinacExtractionConfig()
        
        # Initialize LangExtract bridge
        extract_config = ExtractionConfig(
            model_id=self.config.model_id,
            extraction_passes=self.config.extraction_passes,
            max_workers=self.config.max_workers,
            max_char_buffer=self.config.max_char_buffer,
            temperature=self.config.temperature,
            api_key=api_key
        )
        
        self.bridge = LangExtractBridge(extract_config)
        self.ontology_builder = OntologyBuilder()
        self.logger = logging.getLogger(__name__)
        
        # LINAC subsystems for hierarchical processing
        self.linac_subsystems = [
            "Beam Delivery System",
            "Multi-Leaf Collimator (MLC)",
            "Patient Positioning System", 
            "Imaging System",
            "Treatment Control System",
            "Safety Interlock System",
            "Cooling System",
            "Power Supply System"
        ]
    
    async def extract_from_service_manual(
        self,
        manual_content: str,
        manual_title: str = "LINAC Service Manual",
        save_results: bool = None
    ) -> Dict[str, Any]:
        """
        Extract comprehensive ontology information from LINAC service manual
        
        Args:
            manual_content: Full text content of the service manual
            manual_title: Title/identifier for the manual
            save_results: Whether to save intermediate results
            
        Returns:
            Complete extraction results with ontology
        """
        
        save_results = save_results if save_results is not None else self.config.save_intermediate_results
        
        try:
            self.logger.info(f"Starting LINAC extraction for: {manual_title}")
            
            results = {
                "manual_title": manual_title,
                "extraction_method": "langextract_hierarchical",
                "stages": {}
            }
            
            # Stage 1: General entity extraction
            self.logger.info("Stage 1: General entity extraction")
            general_entities = await self.bridge.extract_medical_entities(
                text_content=manual_content,
                device_type="linear_accelerator",
                hierarchical_mode=False
            )
            results["stages"]["general_extraction"] = general_entities
            
            # Stage 2: Hierarchical system extraction (if enabled)
            if self.config.enable_hierarchical_extraction:
                self.logger.info("Stage 2: Hierarchical system extraction")
                hierarchical_entities = await self._extract_hierarchical_systems(manual_content)
                results["stages"]["hierarchical_extraction"] = hierarchical_entities
            
            # Stage 3: Subsystem-specific extraction
            self.logger.info("Stage 3: Subsystem-specific extraction")
            subsystem_entities = await self._extract_by_subsystems(manual_content)
            results["stages"]["subsystem_extraction"] = subsystem_entities
            
            # Stage 4: Relationship extraction (if enabled)
            if self.config.enable_relationship_extraction:
                self.logger.info("Stage 4: Relationship extraction")
                relationships = await self._extract_relationships(manual_content, results)
                results["stages"]["relationship_extraction"] = relationships
            
            # Stage 5: Consolidate and filter results
            self.logger.info("Stage 5: Consolidating results")
            consolidated_results = self._consolidate_extractions(results)
            results["consolidated_entities"] = consolidated_results
            
            # Stage 6: Create ontology (if enabled)
            if self.config.create_ontology:
                self.logger.info("Stage 6: Creating LINAC ontology")
                ontology = await self._create_linac_ontology(consolidated_results, manual_title)
                results["ontology"] = ontology
            
            # Save intermediate results if requested
            if save_results:
                await self._save_extraction_results(results, manual_title)
            
            # Generate visualizations if requested
            if self.config.generate_visualizations:
                visualization_file = await self._generate_visualizations(results, manual_title)
                results["visualization_file"] = visualization_file
            
            self.logger.info(f"LINAC extraction completed successfully for {manual_title}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in LINAC extraction: {str(e)}")
            raise
    
    async def _extract_hierarchical_systems(self, content: str) -> Dict[str, Any]:
        """Extract hierarchical system structure"""
        
        return await self.bridge.extract_medical_entities(
            text_content=content,
            device_type="linear_accelerator",
            hierarchical_mode=True
        )
    
    async def _extract_by_subsystems(self, content: str) -> Dict[str, Any]:
        """Extract entities focusing on each LINAC subsystem"""
        
        subsystem_results = {}
        
        for subsystem in self.linac_subsystems:
            try:
                self.logger.info(f"Extracting entities for {subsystem}")
                
                subsystem_entities = await self.bridge.extract_medical_entities(
                    text_content=content,
                    device_type="linear_accelerator",
                    hierarchical_mode=True,
                    focus_subsystem=subsystem
                )
                
                subsystem_results[subsystem] = subsystem_entities
                
                # Small delay between subsystem extractions
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error extracting {subsystem}: {str(e)}")
                subsystem_results[subsystem] = {"error": str(e)}
        
        return subsystem_results
    
    async def _extract_relationships(
        self, 
        content: str, 
        existing_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract relationships between identified entities"""
        
        try:
            # Collect all entities from previous stages
            all_entities = []
            
            # From general extraction
            general = existing_results["stages"].get("general_extraction", {})
            for entity_type in ["error_codes", "components", "procedures", "safety_protocols"]:
                all_entities.extend(general.get(entity_type, []))
            
            # From hierarchical extraction
            hierarchical = existing_results["stages"].get("hierarchical_extraction", {})
            for entity_type in ["systems", "subsystems", "components"]:
                all_entities.extend(hierarchical.get(entity_type, []))
            
            if not all_entities:
                return {"relationships": [], "extraction_metadata": {"status": "no_entities"}}
            
            # Use a focused approach for relationship extraction
            # This is a simplified implementation - you might want to use the bridge's relationship extraction
            
            relationship_prompt = f"""
            Given the following LINAC entities, identify and extract relationships between them:
            
            Entities: {json.dumps([e.get('name', e.get('code', str(e))) for e in all_entities[:20]], indent=2)}
            
            Extract relationships such as:
            - Component A controls Component B
            - Error Code X affects Subsystem Y  
            - Procedure P requires Component C
            - System S contains Subsystem T
            """
            
            relationships = await self.bridge.extract_medical_entities(
                text_content=relationship_prompt + "\n\n" + content[:2000],  # Limit context
                extraction_focus=["relationships"],
                device_type="linear_accelerator"
            )
            
            return relationships
            
        except Exception as e:
            self.logger.error(f"Error in relationship extraction: {str(e)}")
            return {"relationships": [], "error": str(e)}
    
    def _consolidate_extractions(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate and deduplicate entities from all extraction stages"""
        
        consolidated = {
            "error_codes": [],
            "components": [], 
            "procedures": [],
            "safety_protocols": [],
            "systems": [],
            "subsystems": [],
            "relationships": [],
            "technical_specifications": []
        }
        
        # Collect from all stages
        for stage_name, stage_results in results["stages"].items():
            if isinstance(stage_results, dict) and "error" not in stage_results:
                
                # Handle subsystem extraction (nested structure)
                if stage_name == "subsystem_extraction":
                    for subsystem_name, subsystem_data in stage_results.items():
                        if isinstance(subsystem_data, dict) and "error" not in subsystem_data:
                            for entity_type, entities in subsystem_data.items():
                                if entity_type in consolidated and isinstance(entities, list):
                                    consolidated[entity_type].extend(entities)
                else:
                    # Handle other stages
                    for entity_type, entities in stage_results.items():
                        if entity_type in consolidated and isinstance(entities, list):
                            consolidated[entity_type].extend(entities)
        
        # Deduplicate based on text content and confidence
        for entity_type in consolidated:
            consolidated[entity_type] = self._deduplicate_entities(consolidated[entity_type])
        
        # Filter by confidence threshold
        for entity_type in consolidated:
            consolidated[entity_type] = [
                entity for entity in consolidated[entity_type]
                if entity.get("confidence", 0) >= self.config.confidence_threshold
            ]
        
        # Add statistics
        consolidated["statistics"] = {
            "total_entities": sum(len(entities) for entities in consolidated.values() if isinstance(entities, list)),
            "entity_counts": {
                entity_type: len(entities) for entity_type, entities in consolidated.items()
                if isinstance(entities, list)
            },
            "confidence_threshold": self.config.confidence_threshold
        }
        
        return consolidated
    
    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate entities based on text similarity"""
        
        if not entities:
            return entities
        
        deduplicated = []
        seen_texts = set()
        
        # Sort by confidence (highest first)
        entities_sorted = sorted(entities, key=lambda x: x.get("confidence", 0), reverse=True)
        
        for entity in entities_sorted:
            entity_text = entity.get("text", entity.get("name", entity.get("code", "")))
            
            # Simple deduplication - exact match
            if entity_text not in seen_texts:
                deduplicated.append(entity)
                seen_texts.add(entity_text)
        
        return deduplicated
    
    async def _create_linac_ontology(
        self, 
        consolidated_entities: Dict[str, Any], 
        manual_title: str
    ) -> Dict[str, Any]:
        """Create OWL ontology from consolidated entities"""
        
        try:
            # Create base LINAC ontology
            ontology_id = manual_title.lower().replace(" ", "_").replace("-", "_")
            ontology = self.ontology_builder.create_linac_ontology(
                ontology_id=ontology_id,
                label=f"LINAC Ontology - {manual_title}",
                description=f"Medical device ontology extracted from {manual_title} using LangExtract"
            )
            
            # Convert extracted entities to ontology entities
            # This is a simplified conversion - you'd want more sophisticated mapping
            
            entity_count = 0
            
            # Add components
            for component_data in consolidated_entities.get("components", []):
                try:
                    # Convert to ontology component format
                    # This would need proper mapping to your ontology models
                    entity_count += 1
                except Exception as e:
                    self.logger.error(f"Error adding component to ontology: {str(e)}")
            
            # Add systems and subsystems
            for system_data in consolidated_entities.get("systems", []):
                try:
                    # Convert to ontology system format
                    entity_count += 1
                except Exception as e:
                    self.logger.error(f"Error adding system to ontology: {str(e)}")
            
            # Validate ontology
            validation_result = self.ontology_builder.validate_ontology_consistency(ontology)
            
            # Export to JSON-LD format
            ontology_json = ontology.to_json_ld()
            
            return {
                "ontology_id": ontology_id,
                "ontology_json": ontology_json,
                "validation": validation_result,
                "statistics": ontology.get_statistics(),
                "entities_added": entity_count
            }
            
        except Exception as e:
            self.logger.error(f"Error creating ontology: {str(e)}")
            return {"error": str(e)}
    
    async def _save_extraction_results(
        self, 
        results: Dict[str, Any], 
        manual_title: str
    ) -> None:
        """Save extraction results to files"""
        
        try:
            # Create output directory
            output_dir = Path("data/langextract_results")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save main results
            results_file = output_dir / f"{manual_title.replace(' ', '_')}_extraction_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            # Save consolidated entities separately
            if "consolidated_entities" in results:
                entities_file = output_dir / f"{manual_title.replace(' ', '_')}_entities.json"
                with open(entities_file, 'w', encoding='utf-8') as f:
                    json.dump(results["consolidated_entities"], f, indent=2, ensure_ascii=False, default=str)
            
            # Save ontology if available
            if "ontology" in results and "ontology_json" in results["ontology"]:
                ontology_file = output_dir / f"{manual_title.replace(' ', '_')}_ontology.json"
                with open(ontology_file, 'w', encoding='utf-8') as f:
                    json.dump(results["ontology"]["ontology_json"], f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Extraction results saved to {output_dir}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
    
    async def _generate_visualizations(
        self, 
        results: Dict[str, Any], 
        manual_title: str
    ) -> Optional[str]:
        """Generate interactive visualizations"""
        
        try:
            # This would use the LangExtract visualization capabilities
            # For now, return placeholder
            
            visualization_file = f"data/langextract_results/{manual_title.replace(' ', '_')}_visualization.html"
            
            # Simple HTML visualization placeholder
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>LINAC Extraction Visualization - {manual_title}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .entity {{ margin: 10px; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }}
                    .error-code {{ background-color: #ffe6e6; }}
                    .component {{ background-color: #e6f3ff; }}
                    .procedure {{ background-color: #e6ffe6; }}
                    .safety {{ background-color: #fff0e6; }}
                </style>
            </head>
            <body>
                <h1>LINAC Extraction Results: {manual_title}</h1>
                <p>Interactive visualization would be generated here using LangExtract's visualization capabilities.</p>
                <p>Total entities extracted: {results.get('consolidated_entities', {}).get('statistics', {}).get('total_entities', 0)}</p>
            </body>
            </html>
            """
            
            with open(visualization_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Visualization saved to {visualization_file}")
            return visualization_file
            
        except Exception as e:
            self.logger.error(f"Error generating visualization: {str(e)}")
            return None
    
    def get_extraction_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive statistics from extraction results"""
        
        stats = {
            "manual_title": results.get("manual_title", "Unknown"),
            "extraction_stages": len(results.get("stages", {})),
            "total_entities": 0,
            "entity_breakdown": {},
            "confidence_distribution": {"high": 0, "medium": 0, "low": 0},
            "subsystem_coverage": 0
        }
        
        # Get consolidated statistics
        consolidated = results.get("consolidated_entities", {})
        if "statistics" in consolidated:
            stats.update(consolidated["statistics"])
        
        # Calculate confidence distribution
        all_entities = []
        for entity_type, entities in consolidated.items():
            if isinstance(entities, list):
                all_entities.extend(entities)
        
        for entity in all_entities:
            confidence = entity.get("confidence", 0)
            if confidence >= 0.8:
                stats["confidence_distribution"]["high"] += 1
            elif confidence >= 0.6:
                stats["confidence_distribution"]["medium"] += 1
            else:
                stats["confidence_distribution"]["low"] += 1
        
        # Subsystem coverage
        subsystem_results = results.get("stages", {}).get("subsystem_extraction", {})
        if subsystem_results:
            successful_subsystems = sum(1 for result in subsystem_results.values() 
                                      if isinstance(result, dict) and "error" not in result)
            stats["subsystem_coverage"] = successful_subsystems / len(self.linac_subsystems)
        
        return stats


# Utility functions

async def quick_linac_extraction(
    content: str,
    manual_title: str = "Quick Test Manual",
    api_key: str = None
) -> Dict[str, Any]:
    """Quick extraction for testing purposes"""
    
    config = LinacExtractionConfig(
        extraction_passes=1,
        max_workers=5,
        enable_hierarchical_extraction=False,
        save_intermediate_results=False,
        generate_visualizations=False,
        create_ontology=False
    )
    
    extractor = LinacExtractor(config, api_key)
    return await extractor.extract_from_service_manual(content, manual_title, save_results=False)


if __name__ == "__main__":
    # Test the LINAC extractor
    
    async def main():
        """Test LINAC extractor with sample content"""
        
        sample_content = """
        LINAC Service Manual - MLCi System
        
        Error Code 7002: MOVEMENT
        Software Release: R6.0x, R6.1x, R7.0x
        Description: The actual direction of movement of a leaf does not match the expected direction.
        Response: Check the drive to the leaf motors and the leaves for free movement.
        
        The Multi-Leaf Collimator (MLC) system consists of multiple components:
        - Leaf motors (Part Number: 12345-ABC) for precise positioning
        - Position encoders for feedback control
        - Control unit for motor coordination
        
        Daily QA Procedure:
        1. Check leaf positioning accuracy
        2. Verify motor response time
        3. Test safety interlocks
        
        WARNING: High voltage present in control cabinet.
        Ensure power is OFF before maintenance.
        """
        
        try:
            print("🚀 Testing LINAC extractor...")
            
            result = await quick_linac_extraction(sample_content, "Test Manual")
            
            print("✅ LINAC extraction test successful!")
            
            # Get statistics
            if "consolidated_entities" in result:
                stats = result["consolidated_entities"].get("statistics", {})
                print(f"📊 Total entities: {stats.get('total_entities', 0)}")
                print(f"📝 Entity breakdown: {stats.get('entity_counts', {})}")
            
        except Exception as e:
            print(f"❌ LINAC extractor test failed: {str(e)}")
    
    # Uncomment to run test
    # asyncio.run(main())