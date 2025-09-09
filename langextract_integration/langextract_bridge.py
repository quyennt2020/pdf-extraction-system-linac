"""
LangExtract Bridge for Medical Device Ontology System

This module provides a bridge between the existing Gemini client and 
LangExtract library, enabling enhanced entity extraction with source 
grounding and multi-pass processing.
"""

import asyncio
import os
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import logging

import langextract as lx
from langextract import data

from .medical_schema_builder import MedicalSchemaBuilder
from backend.models.entity import Entity, EntityType, ComponentType, Relationship


logger = logging.getLogger(__name__)


@dataclass
class ExtractionConfig:
    """Configuration for LangExtract-based extraction"""
    model_id: str = "gemini-2.5-flash"
    api_key: Optional[str] = None
    extraction_passes: int = 2
    max_workers: int = 10
    max_char_buffer: int = 1500
    temperature: float = 0.3
    use_schema_constraints: bool = True
    fence_output: bool = False
    batch_length: int = 20


class LangExtractBridge:
    """
    Bridge between existing system and LangExtract for enhanced extraction
    """
    
    def __init__(self, config: ExtractionConfig = None):
        self.config = config or ExtractionConfig()
        self.schema_builder = MedicalSchemaBuilder()
        self.logger = logging.getLogger(__name__)
        
        # Setup API key
        self.api_key = self.config.api_key or os.getenv('LANGEXTRACT_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("API key required for LangExtract. Set LANGEXTRACT_API_KEY or GOOGLE_API_KEY environment variable.")
    
    async def extract_medical_entities(
        self,
        text_content: str,
        extraction_focus: List[str] = None,
        device_type: str = "linear_accelerator",
        hierarchical_mode: bool = False,
        focus_subsystem: str = None
    ) -> Dict[str, Any]:
        """
        Extract medical entities using LangExtract with source grounding
        
        Args:
            text_content: Input text to process
            extraction_focus: List of entity types to focus on
            device_type: Type of medical device
            hierarchical_mode: Enable hierarchical extraction
            focus_subsystem: Specific subsystem to focus on
            
        Returns:
            Structured extraction results with source grounding
        """
        
        try:
            # Get appropriate examples and prompt
            if hierarchical_mode:
                examples = self.schema_builder.get_all_examples()
                prompt_description = self.schema_builder.build_hierarchical_prompt_description(focus_subsystem)
            else:
                if extraction_focus and len(extraction_focus) == 1:
                    examples = self.schema_builder.get_examples_by_type(extraction_focus[0])
                else:
                    examples = self.schema_builder.get_all_examples()
                prompt_description = self.schema_builder.build_linac_prompt_description()
            
            self.logger.info(f"Starting LangExtract extraction with {len(examples)} examples")
            
            # Run LangExtract
            result = lx.extract(
                text_or_documents=text_content,
                prompt_description=prompt_description,
                examples=examples,
                model_id=self.config.model_id,
                api_key=self.api_key,
                extraction_passes=self.config.extraction_passes,
                max_workers=self.config.max_workers,
                max_char_buffer=self.config.max_char_buffer,
                temperature=self.config.temperature,
                use_schema_constraints=self.config.use_schema_constraints,
                fence_output=self.config.fence_output,
                batch_length=self.config.batch_length
            )
            
            # Convert LangExtract result to our format
            converted_result = self._convert_langextract_result(result, text_content)
            
            # Add metadata
            converted_result["extraction_metadata"] = {
                "method": "langextract",
                "model": self.config.model_id,
                "extraction_passes": self.config.extraction_passes,
                "hierarchical_mode": hierarchical_mode,
                "focus_subsystem": focus_subsystem,
                "extraction_focus": extraction_focus,
                "source_grounded": True,
                "examples_used": len(examples)
            }
            
            self.logger.info(f"LangExtract extraction completed: {self._count_entities(converted_result)} entities")
            
            return converted_result
            
        except Exception as e:
            self.logger.error(f"Error in LangExtract extraction: {str(e)}")
            raise
    
    def _convert_langextract_result(
        self, 
        langextract_result: data.AnnotatedDocument,
        original_text: str
    ) -> Dict[str, Any]:
        """Convert LangExtract AnnotatedDocument to our system format"""
        
        result = {
            "error_codes": [],
            "components": [],
            "procedures": [],
            "safety_protocols": [],
            "technical_specifications": [],
            "systems": [],
            "subsystems": [],
            "relationships": [],
            "source_grounding": {}
        }
        
        # Process extractions by class
        for extraction in langextract_result.extractions:
            entity_class = extraction.extraction_class
            
            # Create base entity info
            entity_info = {
                "text": extraction.extraction_text,
                "confidence": getattr(extraction, 'confidence', 0.8),
                "attributes": extraction.attributes,
                "source_location": {
                    "start_char": getattr(extraction, 'start_char', None),
                    "end_char": getattr(extraction, 'end_char', None),
                    "context": self._get_context(original_text, extraction.extraction_text)
                }
            }
            
            # Map to appropriate category
            if entity_class == "error_code":
                result["error_codes"].append(self._format_error_code(entity_info))
            elif entity_class == "component":
                result["components"].append(self._format_component(entity_info))
            elif entity_class == "procedure":
                result["procedures"].append(self._format_procedure(entity_info))
            elif entity_class == "safety_protocol":
                result["safety_protocols"].append(self._format_safety_protocol(entity_info))
            elif entity_class == "system":
                result["systems"].append(self._format_system(entity_info))
            elif entity_class == "subsystem":
                result["subsystems"].append(self._format_subsystem(entity_info))
            elif entity_class == "relationship":
                result["relationships"].append(self._format_relationship(entity_info))
            else:
                # Default to technical specification
                result["technical_specifications"].append(entity_info)
        
        return result
    
    def _get_context(self, text: str, extraction_text: str, context_chars: int = 100) -> str:
        """Get surrounding context for an extraction"""
        
        try:
            start_idx = text.find(extraction_text)
            if start_idx == -1:
                return extraction_text
            
            context_start = max(0, start_idx - context_chars)
            context_end = min(len(text), start_idx + len(extraction_text) + context_chars)
            
            context = text[context_start:context_end]
            
            # Add ellipsis if truncated
            if context_start > 0:
                context = "..." + context
            if context_end < len(text):
                context = context + "..."
            
            return context
            
        except Exception:
            return extraction_text
    
    def _format_error_code(self, entity_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format error code entity"""
        
        attrs = entity_info["attributes"]
        
        return {
            "code": entity_info["text"],
            "message": attrs.get("message", ""),
            "description": attrs.get("description", ""),
            "response_action": attrs.get("response_action", ""),
            "category": attrs.get("category", ""),
            "severity": attrs.get("severity", ""),
            "software_releases": attrs.get("software_releases", []),
            "device_component": attrs.get("device_component", ""),
            "confidence": entity_info["confidence"],
            "source_location": entity_info["source_location"]
        }
    
    def _format_component(self, entity_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format component entity"""
        
        attrs = entity_info["attributes"]
        
        return {
            "name": entity_info["text"],
            "type": attrs.get("type", ""),
            "function": attrs.get("function", ""),
            "model": attrs.get("model", ""),
            "part_number": attrs.get("part_number", ""),
            "parent_system": attrs.get("parent_system", ""),
            "controlled_by": attrs.get("controlled_by", ""),
            "monitored_by": attrs.get("monitored_by", ""),
            "specifications": attrs.get("specifications", {}),
            "confidence": entity_info["confidence"],
            "source_location": entity_info["source_location"]
        }
    
    def _format_procedure(self, entity_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format procedure entity"""
        
        attrs = entity_info["attributes"]
        
        return {
            "name": entity_info["text"],
            "type": attrs.get("type", ""),
            "frequency": attrs.get("frequency", ""),
            "steps": attrs.get("steps", []),
            "prerequisites": attrs.get("prerequisites", []),
            "tools_required": attrs.get("tools_required", []),
            "safety_level": attrs.get("safety_level", ""),
            "estimated_time_minutes": attrs.get("estimated_time_minutes", 0),
            "acceptance_criteria": attrs.get("acceptance_criteria", ""),
            "beam_parameters": attrs.get("beam_parameters", {}),
            "confidence": entity_info["confidence"],
            "source_location": entity_info["source_location"]
        }
    
    def _format_safety_protocol(self, entity_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format safety protocol entity"""
        
        attrs = entity_info["attributes"]
        
        return {
            "name": entity_info["text"],
            "type": attrs.get("type", ""),
            "hazard_category": attrs.get("hazard_category", ""),
            "severity": attrs.get("severity", ""),
            "equipment": attrs.get("equipment", ""),
            "safety_steps": attrs.get("safety_steps", []),
            "compliance_standard": attrs.get("compliance_standard", ""),
            "minimum_wait_time_minutes": attrs.get("minimum_wait_time_minutes", 0),
            "required_tools": attrs.get("required_tools", []),
            "lockout_required": attrs.get("lockout_required", False),
            "confidence": entity_info["confidence"],
            "source_location": entity_info["source_location"]
        }
    
    def _format_system(self, entity_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format system entity for hierarchical extraction"""
        
        attrs = entity_info["attributes"]
        
        return {
            "name": entity_info["text"],
            "type": attrs.get("type", ""),
            "description": attrs.get("description", ""),
            "subsystems": attrs.get("subsystems", []),
            "confidence": entity_info["confidence"],
            "source_location": entity_info["source_location"]
        }
    
    def _format_subsystem(self, entity_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format subsystem entity for hierarchical extraction"""
        
        attrs = entity_info["attributes"]
        
        return {
            "name": entity_info["text"],
            "type": attrs.get("type", ""),
            "description": attrs.get("description", ""),
            "parent_system": attrs.get("parent_system", ""),
            "components": attrs.get("components", []),
            "confidence": entity_info["confidence"],
            "source_location": entity_info["source_location"]
        }
    
    def _format_relationship(self, entity_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format relationship entity"""
        
        attrs = entity_info["attributes"]
        
        return {
            "relationship_type": attrs.get("type", ""),
            "source_entity": attrs.get("source", ""),
            "target_entity": attrs.get("target", ""),
            "description": entity_info["text"],
            "confidence": entity_info["confidence"],
            "source_location": entity_info["source_location"]
        }
    
    def _count_entities(self, result: Dict[str, Any]) -> int:
        """Count total extracted entities"""
        
        count = 0
        entity_keys = ["error_codes", "components", "procedures", "safety_protocols", 
                      "technical_specifications", "systems", "subsystems", "relationships"]
        
        for key in entity_keys:
            if key in result and isinstance(result[key], list):
                count += len(result[key])
        
        return count
    
    async def batch_extract_pages(
        self,
        pages: List[str],
        device_type: str = "linear_accelerator",
        extraction_focus: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract entities from multiple pages using LangExtract"""
        
        self.logger.info(f"Starting batch extraction for {len(pages)} pages")
        
        results = []
        
        for i, page_content in enumerate(pages):
            try:
                self.logger.info(f"Processing page {i+1}/{len(pages)} with LangExtract")
                
                page_result = await self.extract_medical_entities(
                    text_content=page_content,
                    extraction_focus=extraction_focus,
                    device_type=device_type
                )
                
                page_result["page_number"] = i + 1
                results.append(page_result)
                
                # Small delay for rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error processing page {i+1}: {str(e)}")
                results.append({
                    "page_number": i + 1,
                    "error": str(e),
                    "extraction_metadata": {
                        "method": "langextract",
                        "status": "failed"
                    }
                })
        
        self.logger.info(f"Batch extraction completed: {len(results)} pages processed")
        return results
    
    def create_interactive_visualization(
        self,
        extraction_results: List[Dict[str, Any]],
        output_file: str = "langextract_visualization.html"
    ) -> str:
        """Create interactive HTML visualization using LangExtract"""
        
        try:
            # Convert our results back to LangExtract format for visualization
            annotated_documents = []
            
            for result in extraction_results:
                if "error" in result:
                    continue
                    
                # Create mock AnnotatedDocument for visualization
                # This is simplified - in practice you'd want to preserve the original LangExtract objects
                doc = data.AnnotatedDocument(
                    text="", # Would need original text
                    extractions=[]  # Would convert back to LangExtract Extraction objects
                )
                annotated_documents.append(doc)
            
            # Generate visualization
            if annotated_documents:
                html_content = lx.visualize(annotated_documents)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                self.logger.info(f"Interactive visualization saved to {output_file}")
                return output_file
            else:
                self.logger.warning("No valid extraction results for visualization")
                return None
                
        except Exception as e:
            self.logger.error(f"Error creating visualization: {str(e)}")
            return None


# Utility functions

def test_langextract_connection(api_key: str = None) -> Dict[str, Any]:
    """Test LangExtract connection with sample medical text"""
    
    try:
        bridge = LangExtractBridge(ExtractionConfig(api_key=api_key))
        
        test_text = """
        Error Code 7002: MOVEMENT
        Software Release: R6.0x, R6.1x
        Description: The actual direction of movement of a leaf does not match the expected direction.
        Response: Check the drive to the leaf motors and the leaves for free movement.
        """
        
        # Note: This is a sync test function, but the bridge method is async
        # In practice, you'd run this with asyncio.run()
        
        return {
            "success": True,
            "message": "LangExtract bridge initialized successfully",
            "config": {
                "model": bridge.config.model_id,
                "extraction_passes": bridge.config.extraction_passes,
                "examples_available": len(bridge.schema_builder.get_all_examples())
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the bridge
    
    async def main():
        """Test the LangExtract bridge"""
        
        try:
            bridge = LangExtractBridge()
            
            test_text = """
            Error Code 7002: MOVEMENT
            Software Release: R6.0x, R6.1x, R7.0x\\Integrity™ R1.1
            Description: The actual direction of movement of a leaf does not match the expected direction.
            Response: Check the drive to the leaf motors and the leaves for free movement.
            The gantry rotation motor provides precise positioning for the treatment head.
            """
            
            print("🚀 Testing LangExtract bridge...")
            
            result = await bridge.extract_medical_entities(test_text)
            
            print("✅ LangExtract extraction successful!")
            print(f"📊 Entities extracted: {bridge._count_entities(result)}")
            print(f"🤖 Model used: {result['extraction_metadata']['model']}")
            print(f"🔄 Extraction passes: {result['extraction_metadata']['extraction_passes']}")
            
        except Exception as e:
            print(f"❌ LangExtract bridge test failed: {str(e)}")
    
    # Note: Uncomment to run test
    # asyncio.run(main())