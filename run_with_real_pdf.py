"""
Complete Pipeline Test with Real Service Manual PDF
This script processes a real medical device service manual through the complete ontology extraction pipeline
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import argparse
from typing import List, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.ai_extraction.gemini_client import GeminiClient
from backend.ai_extraction.entity_parser import MedicalEntityParser
from backend.core.pdf_processor import MedicalDevicePDFProcessor
from backend.models.entity import get_entity_summary, validate_entity
from backend.core.ontology_builder import OntologyBuilder
from backend.verification.ontology_validator import OntologyValidator
from loguru import logger


class RealPDFProcessor:
    """Complete pipeline for processing real service manual PDFs"""
    
    def __init__(self, api_key: str = None):
        """Initialize with optional Gemini API key"""
        
        # Setup logging
        logger.add(
            "logs/real_pdf_processing_{time}.log", 
            rotation="10 MB",
            retention="7 days",
            format="{time} | {level} | {name}:{function}:{line} | {message}"
        )
        
        # Initialize components
        self.gemini_client = GeminiClient(api_key=api_key)
        self.entity_parser = MedicalEntityParser()
        self.pdf_processor = MedicalDevicePDFProcessor()
        self.ontology_builder = OntologyBuilder()
        self.ontology_validator = OntologyValidator()
        
        logger.info("Real PDF Processor initialized")
    
    async def process_service_manual(
        self, 
        pdf_path: str, 
        device_type: str = "linear_accelerator",
        max_pages: int = 20,
        output_dir: str = "data/real_pdf_results"
    ) -> dict:
        """
        Process a real service manual PDF through the complete pipeline
        
        Args:
            pdf_path: Path to the service manual PDF
            device_type: Type of medical device (linear_accelerator, ct_scanner, etc.)
            max_pages: Maximum number of pages to process
            output_dir: Directory to save results
            
        Returns:
            Dictionary with processing results and file paths
        """
        
        logger.info(f"🔄 Starting real PDF processing: {pdf_path}")
        
        # Validate input file
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Step 1: Extract text from PDF
            logger.info("📄 Step 1: Extracting text from PDF...")
            pdf_document = self.pdf_processor.process_pdf(pdf_path)
            
            logger.info(f"   - Total pages: {pdf_document.total_pages}")
            logger.info(f"   - Processing first {min(max_pages, pdf_document.total_pages)} pages")
            
            # Step 2: Process pages with AI extraction
            logger.info("🤖 Step 2: AI entity extraction...")
            all_entities = []
            processing_stats = {
                'total_pages': pdf_document.total_pages,
                'processed_pages': 0,
                'failed_pages': 0,
                'total_entities': 0,
                'entities_by_type': {},
                'processing_errors': []
            }
            
            # Process pages (limit to max_pages)
            pages_to_process = pdf_document.pages[:min(max_pages, len(pdf_document.pages))]
            
            for i, page in enumerate(pages_to_process):
                try:
                    logger.info(f"   Processing page {page.page_number}/{len(pages_to_process)}...")
                    
                    # Skip very short pages (likely headers/footers)
                    if len(page.text_content.strip()) < 100:
                        logger.info(f"   Skipping short page {page.page_number}")
                        continue
                    
                    # Extract entities using Gemini with hierarchical mode and diverse focus
                    gemini_result = await self.gemini_client.extract_medical_entities(
                        page_content=page.text_content,
                        device_type=device_type,
                        manual_type="service_manual",
                        extraction_focus=["systems", "subsystems", "components", "spare_parts", "error_codes", "procedures"],
                        hierarchical_mode=True
                    )
                    
                    # Parse entities
                    parsed_entities = self.entity_parser.parse_gemini_response(
                        response=json.dumps(gemini_result) if isinstance(gemini_result, dict) else str(gemini_result),
                        page_number=page.page_number,
                        source_text=page.text_content
                    )
                    
                    # Validate and collect entities
                    page_entities = []
                    for entity_type, entity_list in parsed_entities.items():
                        for entity in entity_list:
                            validation_errors = validate_entity(entity)
                            if not validation_errors:
                                page_entities.append(entity)
                                processing_stats['entities_by_type'][entity_type] = \
                                    processing_stats['entities_by_type'].get(entity_type, 0) + 1
                            else:
                                logger.warning(f"Entity validation failed: {validation_errors}")
                    
                    all_entities.extend(page_entities)
                    processing_stats['processed_pages'] += 1
                    
                    logger.info(f"   Page {page.page_number}: {len(page_entities)} valid entities extracted")
                    
                    # Add delay to respect API rate limits
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    error_msg = f"Error processing page {page.page_number}: {str(e)}"
                    logger.error(error_msg)
                    processing_stats['failed_pages'] += 1
                    processing_stats['processing_errors'].append(error_msg)
                    continue
            
            processing_stats['total_entities'] = len(all_entities)
            
            # Step 2.5: Deduplicate entities found across multiple pages
            logger.info("🔄 Step 2.5: Deduplicating entities across pages...")
            deduplicated_entities = self.deduplicate_entities(all_entities)
            processing_stats['deduplicated_entities'] = len(deduplicated_entities)
            processing_stats['duplicates_removed'] = len(all_entities) - len(deduplicated_entities)
            
            logger.info(f"   Removed {processing_stats['duplicates_removed']} duplicate entities")
            logger.info(f"   Final entity count: {len(deduplicated_entities)}")
            
            # Step 3: Build ontology from deduplicated entities
            logger.info("🏗️ Step 3: Building ontology structure...")
            ontology_result = await self.build_ontology_from_entities(deduplicated_entities, device_type)
            
            # Step 4: Validate ontology
            logger.info("✅ Step 4: Validating ontology...")
            validation_result = self.validate_ontology(ontology_result)
            
            # Step 5: Save results
            logger.info("💾 Step 5: Saving results...")
            result_files = await self.save_processing_results(
                pdf_path, deduplicated_entities, ontology_result, validation_result, 
                processing_stats, output_dir
            )
            
            logger.info(f"✅ Processing completed successfully!")
            logger.info(f"📊 Results: {processing_stats['total_entities']} entities from {processing_stats['processed_pages']} pages")
            
            return {
                'success': True,
                'pdf_path': pdf_path,
                'processing_stats': processing_stats,
                'ontology_stats': ontology_result.get('stats', {}),
                'validation_results': validation_result,
                'output_files': result_files
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'pdf_path': pdf_path
            }
    
    async def build_ontology_from_entities(self, entities: list, device_type: str) -> dict:
        """Build ontology structure from extracted entities"""
        
        try:
            # Group entities by type
            entities_by_type = {}
            for entity in entities:
                # Handle different entity types
                if hasattr(entity, 'entity_type'):
                    entity_type = entity.entity_type
                    if hasattr(entity_type, 'value'):
                        entity_type = entity_type.value
                    else:
                        entity_type = str(entity_type)
                elif hasattr(entity, '__class__'):
                    # Use class name as entity type
                    entity_type = entity.__class__.__name__.lower().replace('entity', '')
                else:
                    entity_type = 'unknown'
                if entity_type not in entities_by_type:
                    entities_by_type[entity_type] = []
                entities_by_type[entity_type].append(entity)
            
            # Build hierarchical structure (simplified for now)
            ontology_structure = {
                "device_type": device_type,
                "entities_by_type": entities_by_type,
                "total_entities": len(entities)
            }
            
            # Generate basic relationships (simplified for now)
            relationships = []
            
            return {
                'structure': ontology_structure,
                'relationships': relationships,
                'entities_by_type': entities_by_type,
                'stats': {
                    'total_entities': len(entities),
                    'entity_types': len(entities_by_type),
                    'relationships': len(relationships),
                    'hierarchy_levels': self._count_hierarchy_levels(ontology_structure)
                }
            }
            
        except Exception as e:
            logger.error(f"Error building ontology: {e}")
            return {'error': str(e)}
    
    def validate_ontology(self, ontology_result: dict) -> dict:
        """Validate the built ontology"""
        
        try:
            if 'error' in ontology_result:
                return {'error': 'Cannot validate ontology due to build errors'}
            
            structure = ontology_result.get('structure', {})
            relationships = ontology_result.get('relationships', [])
            
            # Validate structure consistency
            structure_validation = self.ontology_validator.validate_hierarchical_structure(structure)
            
            # Validate relationships
            relationship_validation = self.ontology_validator.validate_relationships(relationships)
            
            # Check for completeness
            completeness_check = self.ontology_validator.check_completeness(structure, relationships)
            
            return {
                'structure_validation': structure_validation,
                'relationship_validation': relationship_validation,
                'completeness_check': completeness_check,
                'overall_valid': (
                    structure_validation.get('valid', False) and
                    relationship_validation.get('valid', False) and
                    completeness_check.get('complete', False)
                )
            }
            
        except Exception as e:
            logger.error(f"Error validating ontology: {e}")
            return {'error': str(e)}
    
    async def save_processing_results(
        self, 
        pdf_path: str, 
        entities: list, 
        ontology_result: dict, 
        validation_result: dict,
        processing_stats: dict,
        output_dir: str
    ) -> dict:
        """Save all processing results to files"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = Path(pdf_path).stem
        
        result_files = {}
        
        try:
            # Save extracted entities
            entities_file = os.path.join(output_dir, f"{base_filename}_entities_{timestamp}.json")
            entities_data = {
                'metadata': {
                    'source_pdf': pdf_path,
                    'extraction_timestamp': timestamp,
                    'processing_stats': processing_stats
                },
                'entities': [self._serialize_entity(entity) for entity in entities]
            }
            
            with open(entities_file, 'w', encoding='utf-8') as f:
                json.dump(entities_data, f, indent=2, ensure_ascii=False)
            result_files['entities'] = entities_file
            
            # Save ontology structure
            ontology_file = os.path.join(output_dir, f"{base_filename}_ontology_{timestamp}.json")
            with open(ontology_file, 'w', encoding='utf-8') as f:
                json.dump(ontology_result, f, indent=2, ensure_ascii=False, default=str)
            result_files['ontology'] = ontology_file
            
            # Save validation results
            validation_file = os.path.join(output_dir, f"{base_filename}_validation_{timestamp}.json")
            with open(validation_file, 'w', encoding='utf-8') as f:
                json.dump(validation_result, f, indent=2, ensure_ascii=False, default=str)
            result_files['validation'] = validation_file
            
            # Save comprehensive report
            report_file = os.path.join(output_dir, f"{base_filename}_report_{timestamp}.json")
            
            entity_summary = get_entity_summary(entities)
            
            comprehensive_report = {
                'processing_summary': {
                    'source_pdf': pdf_path,
                    'processing_timestamp': timestamp,
                    'total_pages': processing_stats['total_pages'],
                    'processed_pages': processing_stats['processed_pages'],
                    'failed_pages': processing_stats['failed_pages'],
                    'success_rate': processing_stats['processed_pages'] / processing_stats['total_pages'] * 100
                },
                'extraction_results': {
                    'total_entities': len(entities),
                    'entities_by_type': processing_stats['entities_by_type'],
                    'entity_summary': entity_summary,
                    'average_confidence': entity_summary.get('average_confidence', 0)
                },
                'ontology_results': ontology_result.get('stats', {}),
                'validation_results': validation_result,
                'quality_metrics': {
                    'extraction_success_rate': processing_stats['processed_pages'] / processing_stats['total_pages'],
                    'entity_validation_rate': len(entities) / max(1, processing_stats['total_entities']),
                    'ontology_validity': validation_result.get('overall_valid', False),
                    'high_confidence_entities': entity_summary.get('by_confidence', {}).get('high', 0)
                },
                'recommendations': self._generate_recommendations(processing_stats, entity_summary, validation_result),
                'next_steps': [
                    "Review extracted entities in the expert dashboard",
                    "Validate and approve high-confidence entities",
                    "Manually review and correct low-confidence extractions",
                    "Use relationship editor to refine ontology structure",
                    "Export validated ontology to OWL format"
                ]
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_report, f, indent=2, ensure_ascii=False)
            result_files['report'] = report_file
            
            logger.info(f"📁 Results saved to {output_dir}")
            
            return result_files
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return {'error': str(e)}
    
    def deduplicate_entities(self, entities: List[Any]) -> List[Any]:
        """
        Remove duplicate entities found across multiple pages
        
        Args:
            entities: List of extracted entities
            
        Returns:
            List of deduplicated entities with merged information
        """
        
        try:
            # Group entities by type and key
            entity_groups = {}
            
            for entity in entities:
                entity_type = getattr(entity, 'entity_type', 'unknown')
                
                # Generate deduplication key based on entity type
                dedup_key = self._generate_deduplication_key(entity)
                
                group_key = f"{entity_type}:{dedup_key}"
                
                if group_key not in entity_groups:
                    entity_groups[group_key] = []
                
                entity_groups[group_key].append(entity)
            
            # Merge duplicates and keep the best version
            deduplicated = []
            
            for group_key, group_entities in entity_groups.items():
                if len(group_entities) == 1:
                    # No duplicates, keep as is
                    deduplicated.append(group_entities[0])
                else:
                    # Merge duplicates
                    merged_entity = self._merge_duplicate_entities(group_entities)
                    deduplicated.append(merged_entity)
                    
                    logger.info(f"   Merged {len(group_entities)} duplicates for: {group_key}")
            
            return deduplicated
            
        except Exception as e:
            logger.error(f"Error in deduplication: {e}")
            return entities  # Return original entities if deduplication fails
    
    def _generate_deduplication_key(self, entity) -> str:
        """Generate a key for deduplication based on entity type and content"""
        
        entity_type = getattr(entity, 'entity_type', 'unknown')
        
        if entity_type == 'error_code':
            # For error codes, use code + message as key
            code = getattr(entity, 'code', '')
            message = getattr(entity, 'message', '')
            return f"{code}:{message}".lower().strip()
            
        elif entity_type == 'component':
            # For components, use name + type as key
            name = getattr(entity, 'name', '')
            comp_type = getattr(entity, 'component_type', '')
            return f"{name}:{comp_type}".lower().strip()
            
        elif entity_type == 'procedure':
            # For procedures, use name + type as key
            name = getattr(entity, 'name', '')
            proc_type = getattr(entity, 'procedure_type', '')
            return f"{name}:{proc_type}".lower().strip()
            
        elif entity_type == 'safety_protocol':
            # For safety protocols, use type + title as key
            protocol_type = getattr(entity, 'protocol_type', '')
            title = getattr(entity, 'title', '')
            return f"{protocol_type}:{title}".lower().strip()
            
        else:
            # For other types, use a combination of available fields
            name = getattr(entity, 'name', '')
            description = getattr(entity, 'description', '')[:50]  # First 50 chars
            return f"{name}:{description}".lower().strip()
    
    def _merge_duplicate_entities(self, entities: List[Any]) -> Any:
        """
        Merge duplicate entities by combining information and keeping the best version
        
        Args:
            entities: List of duplicate entities to merge
            
        Returns:
            Single merged entity with combined information
        """
        
        if not entities:
            return None
        
        if len(entities) == 1:
            return entities[0]
        
        # Start with the entity that has the highest confidence
        best_entity = max(entities, key=lambda e: getattr(e, 'confidence_score', 0))
        
        # Merge information from other entities
        for entity in entities:
            if entity == best_entity:
                continue
                
            # Merge descriptions (take the longest non-empty one)
            if hasattr(entity, 'description') and hasattr(best_entity, 'description'):
                entity_desc = getattr(entity, 'description', '').strip()
                best_desc = getattr(best_entity, 'description', '').strip()
                
                if len(entity_desc) > len(best_desc) and entity_desc != 'unknown':
                    best_entity.description = entity_desc
            
            # Merge response information for error codes
            if hasattr(entity, 'response') and hasattr(best_entity, 'response'):
                entity_response = getattr(entity, 'response', '').strip()
                best_response = getattr(best_entity, 'response', '').strip()
                
                if len(entity_response) > len(best_response) and entity_response != 'unknown':
                    best_entity.response = entity_response
            
            # Combine source pages
            if hasattr(entity, 'source_page') and hasattr(best_entity, 'source_pages'):
                if not hasattr(best_entity, 'source_pages'):
                    best_entity.source_pages = [getattr(best_entity, 'source_page', 0)]
                
                entity_page = getattr(entity, 'source_page', 0)
                if entity_page not in best_entity.source_pages:
                    best_entity.source_pages.append(entity_page)
            
            # Update confidence to average of all instances
            entity_conf = getattr(entity, 'confidence_score', 0)
            best_conf = getattr(best_entity, 'confidence_score', 0)
            
            # Take the higher confidence score
            if entity_conf > best_conf:
                best_entity.confidence_score = entity_conf
        
        return best_entity

    def _count_hierarchy_levels(self, structure: dict) -> int:
        """Count the number of hierarchy levels in the ontology structure"""
        if not structure:
            return 0
        
        def count_levels(node, current_level=1):
            if not isinstance(node, dict):
                return current_level
            
            max_level = current_level
            for key, value in node.items():
                if isinstance(value, dict):
                    level = count_levels(value, current_level + 1)
                    max_level = max(max_level, level)
            
            return max_level
        
        return count_levels(structure)
    
    def _serialize_entity(self, entity) -> dict:
        """Serialize entity to dictionary for JSON storage"""
        try:
            if hasattr(entity, '__dict__'):
                entity_dict = entity.__dict__.copy()
                
                # Handle entity_type serialization
                if 'entity_type' in entity_dict and hasattr(entity_dict['entity_type'], 'value'):
                    entity_dict['entity_type'] = entity_dict['entity_type'].value
                
                # Convert any datetime objects to strings
                for key, value in entity_dict.items():
                    if hasattr(value, 'isoformat'):
                        entity_dict[key] = value.isoformat()
                
                return entity_dict
            else:
                return {"entity": str(entity), "type": type(entity).__name__}
        except Exception as e:
            return {"error": f"Failed to serialize entity: {str(e)}", "entity_str": str(entity)}
    
    def _generate_recommendations(self, processing_stats: dict, entity_summary: dict, validation_result: dict) -> list:
        """Generate recommendations based on processing results"""
        
        recommendations = []
        
        # Processing quality recommendations
        success_rate = processing_stats['processed_pages'] / processing_stats['total_pages']
        if success_rate < 0.8:
            recommendations.append(
                f"Low processing success rate ({success_rate:.1%}). Consider preprocessing the PDF or adjusting extraction parameters."
            )
        
        # Entity quality recommendations
        avg_confidence = entity_summary.get('average_confidence', 0)
        if avg_confidence < 0.7:
            recommendations.append(
                f"Low average entity confidence ({avg_confidence:.1%}). Manual review and validation recommended."
            )
        
        # Ontology validation recommendations
        if not validation_result.get('overall_valid', False):
            recommendations.append(
                "Ontology validation failed. Review structure and relationships in the expert dashboard."
            )
        
        # Entity distribution recommendations
        entity_counts = processing_stats.get('entities_by_type', {})
        if len(entity_counts) < 3:
            recommendations.append(
                "Limited entity type diversity detected. Consider adjusting extraction prompts or manual annotation."
            )
        
        return recommendations


def setup_directories():
    """Create necessary directories for processing"""
    directories = [
        "data/real_pdf_results",
        "data/input_pdfs",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


async def main():
    """Main function with command line interface"""
    
    parser = argparse.ArgumentParser(description="Process real service manual PDF through ontology extraction pipeline")
    parser.add_argument("pdf_path", help="Path to the service manual PDF file")
    parser.add_argument("--device-type", default="linear_accelerator", 
                       choices=["linear_accelerator", "ct_scanner", "mri", "ultrasound"],
                       help="Type of medical device")
    parser.add_argument("--max-pages", type=int, default=20, 
                       help="Maximum number of pages to process")
    parser.add_argument("--output-dir", default="data/real_pdf_results",
                       help="Output directory for results")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY environment variable)")
    parser.add_argument("--start-dashboard", action="store_true",
                       help="Start expert review dashboard after processing")
    
    args = parser.parse_args()
    
    print("🏥 Real Service Manual PDF Processing Pipeline")
    print("=" * 60)
    
    # Setup directories
    setup_directories()
    
    # Load configuration
    from config import config
    
    # Get API key from command line, config file, or environment
    api_key = args.api_key or config.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: Gemini API key required")
        print("   Option 1: Edit .env file and add your API key")
        print("   Option 2: Set GEMINI_API_KEY environment variable")
        print("   Option 3: Use --api-key argument")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        sys.exit(1)
    
    # Validate PDF file
    if not os.path.exists(args.pdf_path):
        print(f"❌ Error: PDF file not found: {args.pdf_path}")
        print("\n💡 Place your service manual PDF in one of these locations:")
        print("   - data/input_pdfs/")
        print("   - Or provide full path to your PDF")
        sys.exit(1)
    
    try:
        # Initialize processor
        processor = RealPDFProcessor(api_key=api_key)
        
        print(f"\n📄 Processing PDF: {args.pdf_path}")
        print(f"🔧 Device type: {args.device_type}")
        print(f"📊 Max pages: {args.max_pages}")
        print(f"📁 Output directory: {args.output_dir}")
        
        # Process the PDF
        result = await processor.process_service_manual(
            pdf_path=args.pdf_path,
            device_type=args.device_type,
            max_pages=args.max_pages,
            output_dir=args.output_dir
        )
        
        if result['success']:
            print(f"\n✅ Processing completed successfully!")
            print(f"📊 Statistics:")
            stats = result['processing_stats']
            print(f"   - Pages processed: {stats['processed_pages']}/{stats['total_pages']}")
            print(f"   - Entities extracted: {stats['total_entities']}")
            print(f"   - Entity types: {len(stats['entities_by_type'])}")
            
            if result.get('ontology_stats'):
                ont_stats = result['ontology_stats']
                print(f"   - Relationships: {ont_stats.get('relationships', 0)}")
                print(f"   - Hierarchy levels: {ont_stats.get('hierarchy_levels', 0)}")
            
            print(f"\n📁 Output files:")
            for file_type, file_path in result['output_files'].items():
                print(f"   - {file_type.title()}: {file_path}")
            
            # Show entity breakdown
            if stats['entities_by_type']:
                print(f"\n📈 Entity breakdown:")
                for entity_type, count in stats['entities_by_type'].items():
                    print(f"   - {entity_type}: {count}")
            
            # Start dashboard if requested
            if args.start_dashboard:
                print(f"\n🚀 Starting expert review dashboard...")
                print("📊 Dashboard will load PDF results automatically")
                print("📊 Dashboard available at: http://localhost:9000")
                print("🔧 Starting dashboard server...")
                
                # Run dashboard in a separate process to avoid asyncio conflicts
                import subprocess
                subprocess.run([sys.executable, "launch_dashboard.py"])
        
        else:
            print(f"\n❌ Processing failed: {result['error']}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Processing interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())