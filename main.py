"""
Main execution script for Medical Device Ontology Extraction System
Run this to test the complete pipeline: PDF -> Gemini -> Entities -> Review
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.ai_extraction.gemini_client import GeminiClient
from backend.ai_extraction.entity_parser import MedicalEntityParser
from backend.core.pdf_processor import MedicalDevicePDFProcessor
from backend.models.entity import get_entity_summary, validate_entity
from loguru import logger


class MedicalDeviceExtractionPipeline:
    """
    Complete pipeline for medical device ontology extraction
    """
    
    def __init__(self):
        """Initialize pipeline components"""
        
        # Setup logging
        logger.add(
            "logs/pipeline_{time}.log", 
            rotation="10 MB",
            retention="7 days",
            format="{time} | {level} | {name}:{function}:{line} | {message}"
        )
        
        # Initialize components
        self.gemini_client = GeminiClient()
        self.entity_parser = MedicalEntityParser()
        self.pdf_processor = MedicalDevicePDFProcessor()
        
        logger.info("Medical Device Extraction Pipeline initialized")
    
    async def process_pdf_file(self, pdf_path: str, output_dir: str = "data/extracted_entities") -> dict:
        """
        Process a PDF file through the complete pipeline
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save extracted entities
            
        Returns:
            Dictionary with extraction results and statistics
        """
        
        logger.info(f"Starting pipeline for: {pdf_path}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Step 1: Process PDF
            logger.info("Step 1: Processing PDF document...")
            pdf_document = self.pdf_processor.process_pdf(pdf_path)
            
            # Step 2: Extract entities from pages
            logger.info("Step 2: Extracting entities with Gemini Flash...")
            all_entities = []
            processing_stats = {
                'total_pages': pdf_document.total_pages,
                'processed_pages': 0,
                'failed_pages': 0,
                'total_entities': 0,
                'entities_by_type': {}
            }
            
            # Process pages (limit to first 10 for demo)
            pages_to_process = pdf_document.pages[:min(10, len(pdf_document.pages))]
            
            from dataclasses import asdict
            from backend.models.entity import entity_from_dict

            for page in pages_to_process:
                try:
                    logger.info(f"Processing page {page.page_number}...")
                    
                    # Skip very short pages
                    if len(page.text_content.strip()) < 200:
                        logger.info(f"Skipping short page {page.page_number}")
                        continue
                    
                    # Extract entities using Gemini
                    gemini_result = await self.gemini_client.extract_medical_entities(
                        page_content=page.text_content,
                        device_type="linear_accelerator",
                        manual_type="service_manual"
                    )
                    
                    # Parse entities
                    parsed_entities = self.entity_parser.parse_gemini_response(
                        response=json.dumps(gemini_result) if isinstance(gemini_result, dict) else str(gemini_result),
                        page_number=page.page_number,
                        source_text=page.text_content
                    )
                    
                    # Validate entities
                    validated_entities = []
                    for entity_type, entity_list in parsed_entities.items():
                        for entity in entity_list:
                            entity_dict = asdict(entity)
                            singular_entity_type = entity_type[:-1] if entity_type.endswith('s') else entity_type
                            entity_dict['entity_type'] = singular_entity_type
                            converted_entity = entity_from_dict(entity_dict)
                            validation_errors = validate_entity(converted_entity)
                            if not validation_errors:
                                validated_entities.append(converted_entity)
                                
                                # Update statistics
                                processing_stats['entities_by_type'][entity_type] = \
                                    processing_stats['entities_by_type'].get(entity_type, 0) + 1
                            else:
                                logger.warning(f"Entity validation failed: {validation_errors}")
                    
                    all_entities.extend(validated_entities)
                    processing_stats['processed_pages'] += 1
                    
                    logger.info(f"Page {page.page_number}: {len(validated_entities)} entities extracted")
                    
                    # Add delay to respect rate limits
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing page {page.page_number}: {str(e)}")
                    processing_stats['failed_pages'] += 1
                    continue
            
            processing_stats['total_entities'] = len(all_entities)
            
            # Step 3: Save results
            logger.info("Step 3: Saving extraction results...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = Path(pdf_path).stem
            
            # Save entities as JSON
            entities_json_path = os.path.join(output_dir, f"{base_filename}_entities_{timestamp}.json")
            
            entities_dict = {
                'metadata': {
                    'source_pdf': pdf_path,
                    'extraction_timestamp': timestamp,
                    'pipeline_version': '1.0',
                    'processing_stats': processing_stats
                },
                'entities': [entity.to_dict() for entity in all_entities]
            }
            
            with open(entities_json_path, 'w', encoding='utf-8') as f:
                json.dump(entities_dict, f, indent=2, ensure_ascii=False)
            
            # Save summary report
            summary_path = os.path.join(output_dir, f"{base_filename}_summary_{timestamp}.json")
            
            entity_summary = get_entity_summary(all_entities)
            
            summary_report = {
                'extraction_summary': {
                    'source_pdf': pdf_path,
                    'total_pages': pdf_document.total_pages,
                    'processed_pages': processing_stats['processed_pages'],
                    'failed_pages': processing_stats['failed_pages'],
                    'extraction_timestamp': timestamp
                },
                'entity_statistics': entity_summary,
                'quality_metrics': {
                    'high_confidence_entities': entity_summary['by_confidence']['high'],
                    'medium_confidence_entities': entity_summary['by_confidence']['medium'],
                    'low_confidence_entities': entity_summary['by_confidence']['low'],
                    'average_confidence': entity_summary['average_confidence'],
                    'entities_needing_review': entity_summary['total_entities'] - entity_summary['approved_count']
                },
                'next_steps': [
                    f"Review extracted entities in: {entities_json_path}",
                    "Use human review interface to verify and approve entities",
                    "Generate ontology from approved entities",
                    "Export to OWL format for knowledge graph"
                ]
            }
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Pipeline completed successfully!")
            logger.info(f"📊 Results saved to: {output_dir}")
            logger.info(f"📈 Extracted {processing_stats['total_entities']} entities from {processing_stats['processed_pages']} pages")
            
            return {
                'success': True,
                'entities_file': entities_json_path,
                'summary_file': summary_path,
                'statistics': processing_stats,
                'entity_summary': entity_summary
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_sample_text(self, sample_text: str) -> dict:
        """
        Process sample text for quick testing
        
        Args:
            sample_text: Text content to process
            
        Returns:
            Dictionary with extraction results
        """
        
        logger.info("Processing sample text with Gemini Flash...")
        
        try:
            # Extract entities using Gemini
            gemini_result = await self.gemini_client.extract_medical_entities(
                page_content=sample_text,
                device_type="linear_accelerator",
                manual_type="service_manual"
            )
            
            # Parse entities
            parsed_entities = self.entity_parser.parse_gemini_response(
                response=json.dumps(gemini_result) if isinstance(gemini_result, dict) else str(gemini_result),
                page_number=1,
                source_text=sample_text
            )
            
            # Convert entities to list for summary
            all_entities = []
            from dataclasses import asdict
            from backend.models.entity import entity_from_dict
            all_entities_converted = []
            for entity_type, entity_list in parsed_entities.items():
                for entity in entity_list:
                    entity_dict = asdict(entity)
                    singular_entity_type = entity_type[:-1] if entity_type.endswith('s') else entity_type
                    entity_dict['entity_type'] = singular_entity_type
                    all_entities_converted.append(entity_from_dict(entity_dict))
            
            entity_summary = get_entity_summary(all_entities_converted)
            
            return {
                'success': True,
                'entities': parsed_entities,
                'summary': entity_summary,
                'total_entities': len(all_entities)
            }
            
        except Exception as e:
            logger.error(f"Sample text processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


def find_test_pdf() -> Optional[str]:
    """Find a test PDF file to process"""
    
    # Possible locations for test PDFs
    test_paths = [
        "data/medical_manuals/MLCi_Manual.pdf",
        "data/input/4.2 MLCi2 Subsystem.pdf", 
        "uploads/test.pdf",
        "data/input/MLCi_Treatment_Mode.pdf",
        # Add more paths based on your project knowledge
    ]
    
    for path in test_paths:
        if os.path.exists(path):
            return path
    
    return None


async def run_demo():
    """Run demonstration of the complete pipeline"""
    
    print("🏥 Medical Device Ontology Extraction System - DEMO")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = MedicalDeviceExtractionPipeline()
    
    # Demo 1: Sample text processing
    print("\n📝 DEMO 1: Sample Text Processing")
    print("-" * 40)
    
    sample_mlci_text = """
    Error Code: 7002
    Software Release: R6.0x, R6.1x, R7.0x\Integrity™ R1.1
    Message: MOVEMENT
    Description: The actual direction of movement of a leaf does not match the expected direction, or a leaf has moved that should be stationary, or a leaf that should be moving is stationary.
    Response: Check the drive to the leaf motors and the leaves for free movement.
    
    The MLCi system consists of several key components including the leaf motor assembly, which controls individual leaf positions within the multileaf collimator. Regular calibration procedures are required to maintain system accuracy.
    
    WARNING: Always ensure system is in service mode before performing maintenance procedures.
    """
    
    sample_result = await pipeline.process_sample_text(sample_mlci_text)
    
    if sample_result['success']:
        print(f"✅ Sample processing successful!")
        print(f"📊 Entities extracted: {sample_result['total_entities']}")
        
        for entity_type, entity_list in sample_result['entities'].items():
            if entity_list:
                print(f"  - {entity_type}: {len(entity_list)} entities")
                for entity in entity_list[:2]:  # Show first 2
                    if hasattr(entity, 'code'):
                        print(f"    * Code {entity.code}: {entity.message}")
                    elif hasattr(entity, 'name'):
                        print(f"    * {entity.name}")
    else:
        print(f"❌ Sample processing failed: {sample_result['error']}")
    
    # Demo 2: PDF file processing  
    print(f"\n📄 DEMO 2: PDF File Processing")
    print("-" * 40)
    
    test_pdf = find_test_pdf()
    
    if test_pdf:
        print(f"Found test PDF: {test_pdf}")
        
        pdf_result = await pipeline.process_pdf_file(test_pdf)
        
        if pdf_result['success']:
            print(f"✅ PDF processing successful!")
            print(f"📊 Statistics:")
            print(f"  - Total pages: {pdf_result['statistics']['total_pages']}")
            print(f"  - Processed pages: {pdf_result['statistics']['processed_pages']}")
            print(f"  - Total entities: {pdf_result['statistics']['total_entities']}")
            print(f"  - Average confidence: {pdf_result['entity_summary']['average_confidence']:.2f}")
            
            print(f"\n📁 Output files:")
            print(f"  - Entities: {pdf_result['entities_file']}")
            print(f"  - Summary: {pdf_result['summary_file']}")
            
            # Show entity breakdown
            print(f"\n📈 Entity breakdown:")
            for entity_type, count in pdf_result['statistics']['entities_by_type'].items():
                print(f"  - {entity_type}: {count}")
        else:
            print(f"❌ PDF processing failed: {pdf_result['error']}")
    else:
        print("⚠️ No test PDF found. Place a medical device PDF in one of these locations:")
        test_paths = [
            "data/medical_manuals/",
            "data/input/", 
            "uploads/"
        ]
        for path in test_paths:
            print(f"  - {path}")
    
    print(f"\n🎉 Demo completed!")
    print(f"📚 Check the logs/ directory for detailed processing information")
    print(f"📂 Check data/extracted_entities/ for results")


async def main():
    """Main function"""
    
    # Check if running interactively or with arguments
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            sys.exit(1)
        
        print(f"🔄 Processing PDF: {pdf_path}")
        
        pipeline = MedicalDeviceExtractionPipeline()
        result = await pipeline.process_pdf_file(pdf_path)
        
        if result['success']:
            print(f"✅ Processing completed successfully!")
            print(f"📊 Extracted {result['statistics']['total_entities']} entities")
            sys.exit(0)
        else:
            print(f"❌ Processing failed: {result['error']}")
            sys.exit(1)
    
    else:
        # Run interactive demo
        await run_demo()


if __name__ == "__main__":
    # Create necessary directories
    directories = [
        "data/medical_manuals",
        "data/extracted_entities",
        "data/reviewed_data",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Run the main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(3)
