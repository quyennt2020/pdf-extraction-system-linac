"""
Google Gemini Flash client for medical device entity extraction
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import google.generativeai as genai
from loguru import logger
import time
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class ExtractionConfig:
    """Configuration for Gemini extraction"""
    model: str = "gemini-1.5-flash"
    temperature: float = 0.1
    max_output_tokens: int = 2048
    top_p: float = 0.8
    top_k: int = 10
    timeout: int = 300
    retry_attempts: int = 3


class GeminiClient:
    """
    Google Gemini Flash client specialized for medical device entity extraction
    """
    
    def __init__(self, api_key: str = None, config: ExtractionConfig = None):
        """Initialize Gemini client"""
        
        # Setup API key
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google AI API key is required")
            
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Setup configuration
        self.config = config or ExtractionConfig()
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.config.model,
            generation_config={
                "temperature": self.config.temperature,
                "top_p": self.config.top_p,
                "top_k": self.config.top_k,
                "max_output_tokens": self.config.max_output_tokens,
            }
        )
        
        logger.info(f"Gemini client initialized with model: {self.config.model}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def extract_medical_entities(
        self,
        page_content: str,
        device_type: str = "linear_accelerator",
        manual_type: str = "service_manual",
        extraction_focus: List[str] = None,
        hierarchical_mode: bool = False,
        focus_subsystem: str = None
    ) -> Dict[str, Any]:
        """
        Extract medical device entities from page content using Gemini Flash
        
        Args:
            page_content: Text content from PDF page
            device_type: Type of medical device (e.g., linear_accelerator)
            manual_type: Type of manual (service_manual, user_manual, etc.)
            extraction_focus: List of entity types to focus on
            hierarchical_mode: Enable hierarchical ontology extraction
            focus_subsystem: Specific subsystem to focus on (for LINAC)
            
        Returns:
            Dictionary containing extracted entities with confidence scores
        """
        
        if not extraction_focus:
            if hierarchical_mode:
                extraction_focus = ["systems", "subsystems", "components", "spare_parts", "relationships", "error_codes"]
            else:
                extraction_focus = ["error_codes", "components", "procedures", "safety_protocols"]
        
        try:
            # Build extraction prompt
            if hierarchical_mode:
                prompt = self._build_hierarchical_extraction_prompt(
                    page_content=page_content,
                    device_type=device_type,
                    focus_subsystem=focus_subsystem
                )
            else:
                prompt = self._build_extraction_prompt(
                    page_content=page_content,
                    device_type=device_type,
                    manual_type=manual_type,
                    extraction_focus=extraction_focus
                )
            
            logger.info(f"Starting Gemini extraction for {device_type} content")
            
            # Generate response
            response = await self._generate_response(prompt)
            
            # Parse response
            entities = self._parse_gemini_response(response)
            
            # Add metadata
            entities["extraction_metadata"] = {
                "model": self.config.model,
                "device_type": device_type,
                "manual_type": manual_type,
                "extraction_focus": extraction_focus,
                "hierarchical_mode": hierarchical_mode,
                "focus_subsystem": focus_subsystem,
                "timestamp": time.time(),
                "content_length": len(page_content)
            }
            
            logger.info(f"Successfully extracted {self._count_entities(entities)} entities")
            
            return entities
            
        except Exception as e:
            logger.error(f"Error in Gemini extraction: {str(e)}")
            raise
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response from Gemini with error handling"""
        
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(self.model.generate_content, prompt),
                timeout=self.config.timeout
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
                
            return response.text
            
        except asyncio.TimeoutError:
            logger.error(f"Gemini request timeout after {self.config.timeout} seconds")
            raise
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def _build_extraction_prompt(
        self,
        page_content: str,
        device_type: str,
        manual_type: str,
        extraction_focus: List[str]
    ) -> str:
        """Build specialized prompt for medical device extraction"""
        
        from .prompt_templates import MedicalDevicePrompts
        
        prompt_builder = MedicalDevicePrompts()
        
        return prompt_builder.build_extraction_prompt(
            page_content=page_content,
            device_type=device_type,
            manual_type=manual_type,
            extraction_focus=extraction_focus
        )
    
    def _build_hierarchical_extraction_prompt(
        self,
        page_content: str,
        device_type: str,
        focus_subsystem: str = None
    ) -> str:
        """Build specialized prompt for hierarchical ontology extraction"""
        
        from .prompt_templates import MedicalDevicePrompts
        
        prompt_builder = MedicalDevicePrompts()
        
        return prompt_builder.build_hierarchical_extraction_prompt(
            page_content=page_content,
            device_type=device_type,
            focus_subsystem=focus_subsystem
        )
    
    def _parse_gemini_response(self, response: str) -> Dict[str, Any]:
        """Parse Gemini response into structured entities"""
        
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{') and response.strip().endswith('}'):
                return json.loads(response)
            
            # Parse structured text response
            return self._parse_text_response(response)
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, attempting text parsing")
            return self._parse_text_response(response)
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        
        entities = {
            "error_codes": [],
            "components": [],
            "procedures": [],
            "safety_protocols": [],
            "technical_specifications": []
        }
        
        # Split response into sections
        sections = response.split('\n\n')
        
        for section in sections:
            if not section.strip():
                continue
                
            # Identify section type and extract entities
            section_lower = section.lower()
            
            if any(keyword in section_lower for keyword in ['error', 'code', 'fault']):
                entities["error_codes"].extend(self._extract_error_codes_from_text(section))
            elif any(keyword in section_lower for keyword in ['component', 'part', 'motor', 'sensor']):
                entities["components"].extend(self._extract_components_from_text(section))
            elif any(keyword in section_lower for keyword in ['procedure', 'step', 'check', 'calibrat']):
                entities["procedures"].extend(self._extract_procedures_from_text(section))
            elif any(keyword in section_lower for keyword in ['warning', 'caution', 'danger', 'safety']):
                entities["safety_protocols"].extend(self._extract_safety_from_text(section))
        
        return entities
    
    def _extract_error_codes_from_text(self, text: str) -> List[Dict]:
        """Extract error codes from text section"""
        import re
        
        error_codes = []
        
        # Pattern for error codes (4-digit numbers)
        code_pattern = r'\b(\d{4})\b'
        codes = re.findall(code_pattern, text)
        
        for code in codes:
            # Try to extract additional info around the code
            code_info = {
                "code": code,
                "confidence": 0.8,
                "context": text[:200] + "..." if len(text) > 200 else text
            }
            
            # Extract message if present
            message_match = re.search(rf'{code}.*?([A-Z][A-Z\s\-]+)', text)
            if message_match:
                code_info["message"] = message_match.group(1).strip()
                code_info["confidence"] = 0.9
            
            error_codes.append(code_info)
        
        return error_codes
    
    def _extract_components_from_text(self, text: str) -> List[Dict]:
        """Extract components from text section"""
        
        components = []
        
        # Common component keywords for linear accelerators
        component_keywords = [
            'motor', 'sensor', 'actuator', 'controller', 'display',
            'valve', 'pump', 'filter', 'detector', 'collimator',
            'gantry', 'couch', 'beam', 'monitor', 'chamber'
        ]
        
        for keyword in component_keywords:
            if keyword.lower() in text.lower():
                components.append({
                    "name": keyword.title(),
                    "context": text[:200] + "..." if len(text) > 200 else text,
                    "confidence": 0.7
                })
        
        return components
    
    def _extract_procedures_from_text(self, text: str) -> List[Dict]:
        """Extract procedures from text section"""
        
        procedures = []
        
        # Look for procedure indicators
        procedure_patterns = [
            r'check\s+([^.]+)',
            r'calibrate\s+([^.]+)',
            r'verify\s+([^.]+)',
            r'test\s+([^.]+)',
            r'measure\s+([^.]+)'
        ]
        
        import re
        
        for pattern in procedure_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                procedures.append({
                    "name": match.group(0).title(),
                    "description": match.group(1).strip(),
                    "confidence": 0.75
                })
        
        return procedures
    
    def _extract_safety_from_text(self, text: str) -> List[Dict]:
        """Extract safety protocols from text section"""
        
        safety_protocols = []
        
        safety_keywords = ['warning', 'caution', 'danger', 'note', 'important']
        
        for keyword in safety_keywords:
            if keyword.lower() in text.lower():
                safety_protocols.append({
                    "type": keyword.upper(),
                    "description": text[:200] + "..." if len(text) > 200 else text,
                    "confidence": 0.8
                })
        
        return safety_protocols
    
    def _count_entities(self, entities: Dict[str, Any]) -> int:
        """Count total number of extracted entities"""
        
        count = 0
        
        for entity_type, entity_list in entities.items():
            if entity_type != "extraction_metadata" and isinstance(entity_list, list):
                count += len(entity_list)
        
        return count
    
    async def batch_extract(
        self,
        pages: List[str],
        device_type: str = "linear_accelerator",
        manual_type: str = "service_manual"
    ) -> List[Dict[str, Any]]:
        """Extract entities from multiple pages in batch"""
        
        logger.info(f"Starting batch extraction for {len(pages)} pages")
        
        results = []
        
        for i, page_content in enumerate(pages):
            try:
                logger.info(f"Processing page {i+1}/{len(pages)}")
                
                entities = await self.extract_medical_entities(
                    page_content=page_content,
                    device_type=device_type,
                    manual_type=manual_type
                )
                
                entities["page_number"] = i + 1
                results.append(entities)
                
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
        
        logger.info(f"Batch extraction completed: {len(results)} pages processed")
        
        return results
    
    async def extract_entity_relationships(
        self,
        entities: List[Dict[str, Any]],
        context_text: str,
        device_type: str = "linear_accelerator"
    ) -> Dict[str, Any]:
        """
        Extract relationships between already identified entities
        
        Args:
            entities: List of extracted entities
            context_text: Original text context
            device_type: Type of medical device
            
        Returns:
            Dictionary containing extracted relationships
        """
        
        try:
            from .prompt_templates import build_relationship_detection_prompt
            
            # Build relationship detection prompt
            prompt = build_relationship_detection_prompt(
                entities=entities,
                context_text=context_text,
                device_type=device_type
            )
            
            logger.info(f"Starting relationship extraction for {len(entities)} entities")
            
            # Generate response
            response = await self._generate_response(prompt)
            
            # Parse response
            relationships = self._parse_gemini_response(response)
            
            # Add metadata
            relationships["extraction_metadata"] = {
                "model": self.config.model,
                "device_type": device_type,
                "entity_count": len(entities),
                "extraction_type": "relationships",
                "timestamp": time.time()
            }
            
            logger.info(f"Successfully extracted {len(relationships.get('relationships', []))} relationships")
            
            return relationships
            
        except Exception as e:
            logger.error(f"Error in relationship extraction: {str(e)}")
            raise
    
    async def extract_subsystem_entities(
        self,
        page_content: str,
        subsystem_name: str,
        device_type: str = "linear_accelerator"
    ) -> Dict[str, Any]:
        """
        Extract entities specific to a particular subsystem
        
        Args:
            page_content: Text content to analyze
            subsystem_name: Name of the subsystem to focus on
            device_type: Type of medical device
            
        Returns:
            Dictionary containing subsystem-specific entities
        """
        
        try:
            from .prompt_templates import build_linac_subsystem_prompt
            
            # Build subsystem-specific prompt
            prompt = build_linac_subsystem_prompt(
                page_content=page_content,
                target_subsystem=subsystem_name
            )
            
            logger.info(f"Starting subsystem extraction for {subsystem_name}")
            
            # Generate response
            response = await self._generate_response(prompt)
            
            # Parse response
            entities = self._parse_gemini_response(response)
            
            # Add metadata
            entities["extraction_metadata"] = {
                "model": self.config.model,
                "device_type": device_type,
                "target_subsystem": subsystem_name,
                "extraction_type": "subsystem_specific",
                "timestamp": time.time(),
                "content_length": len(page_content)
            }
            
            logger.info(f"Successfully extracted subsystem entities for {subsystem_name}")
            
            return entities
            
        except Exception as e:
            logger.error(f"Error in subsystem extraction: {str(e)}")
            raise


# Utility functions

def validate_api_key(api_key: str) -> bool:
    """Validate Google AI API key"""
    
    if not api_key or len(api_key) < 30:
        return False
    
    if not api_key.startswith('AIza'):
        return False
    
    return True


async def test_gemini_connection(api_key: str = None) -> Dict[str, Any]:
    """Test Gemini API connection"""
    
    try:
        client = GeminiClient(api_key=api_key)
        
        test_content = """
        Error Code 7002: MOVEMENT
        Software Release: R6.0x, R6.1x, R7.0x\Integrity™ R1.1
        Description: The actual direction of movement of a leaf does not match the expected direction.
        Response: Check the drive to the leaf motors and the leaves for free movement.
        """
        
        result = await client.extract_medical_entities(test_content)
        
        return {
            "success": True,
            "model": client.config.model,
            "entities_found": client._count_entities(result),
            "test_result": result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Test the Gemini client
    
    async def main():
        test_result = await test_gemini_connection()
        
        if test_result["success"]:
            print("✅ Gemini Flash connection successful!")
            print(f"🤖 Model: {test_result['model']}")
            print(f"📊 Entities found: {test_result['entities_found']}")
        else:
            print("❌ Gemini Flash connection failed!")
            print(f"💥 Error: {test_result['error']}")
    
    asyncio.run(main())
