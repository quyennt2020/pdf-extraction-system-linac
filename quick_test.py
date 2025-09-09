"""
Quick test script for Medical Device Ontology Extraction System
Tests Gemini Flash integration with PDF processing
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.ai_extraction.gemini_client import GeminiClient, test_gemini_connection
from backend.ai_extraction.entity_parser import MedicalEntityParser
from backend.core.pdf_processor import MedicalDevicePDFProcessor, validate_pdf_file
from loguru import logger
import json


class QuickTestRunner:
    """Quick test runner for the medical device extraction system"""
    
    def __init__(self):
        """Initialize test components"""
        
        self.gemini_client = None
        self.entity_parser = MedicalEntityParser()
        self.pdf_processor = MedicalDevicePDFProcessor()
        
        # Setup logging
        logger.add("logs/quick_test.log", rotation="10 MB")
        logger.info("Quick test runner initialized")
    
    async def test_gemini_connection(self) -> bool:
        """Test Gemini Flash API connection"""
        
        logger.info("Testing Gemini Flash connection...")
        
        try:
            result = await test_gemini_connection()
            
            if result["success"]:
                logger.info("✅ Gemini Flash connection successful!")
                logger.info(f"🤖 Model: {result['model']}")
                logger.info(f"📊 Test entities found: {result['entities_found']}")
                return True
            else:
                logger.error("❌ Gemini Flash connection failed!")
                logger.error(f"💥 Error: {result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"Exception testing Gemini connection: {str(e)}")
            return False
    
    async def test_with_sample_text(self) -> bool:
        """Test extraction with sample medical device text"""
        
        logger.info("Testing with sample MLCi error code text...")
        
        # Sample text from MLCi manual (based on project knowledge)
        sample_text = """
        Error Code: 7002
        Software Release: R6.0x, R6.1x, R7.0x\\Integrity™ R1.1
        Message: MOVEMENT
        Description: The actual direction of movement of a leaf does not match the expected direction, or a leaf has moved that should be stationary, or a leaf that should be moving is stationary.
        Response: Check the drive to the leaf motors and the leaves for free movement.
        
        Error Code: 7001
        Software Release: R5.0, R6.0x, R6.1x, R7.0x\\Integrity™ R1.1
        Message: NOT CALIBRATED
        Description: Calibration data missing or incorrect, resulting in MLCi/MLCi2 control system not being calibrated.
        Response: Check calibration files are present and correct. Check video line calibration, particularly for correct spacing.
        """
        
        try:
            # Initialize Gemini client
            self.gemini_client = GeminiClient()
            
            # Extract entities
            result = await self.gemini_client.extract_medical_entities(
                page_content=sample_text,
                device_type="linear_accelerator",
                extraction_focus=["error_codes", "components", "procedures"]
            )
            
            # Parse entities
            parsed_entities = self.entity_parser.parse_gemini_response(
                response=json.dumps(result) if isinstance(result, dict) else str(result),
                page_number=1,
                source_text=sample_text
            )
            
            # Display results
            logger.info("📊 EXTRACTION RESULTS:")
            
            for entity_type, entity_list in parsed_entities.items():
                if entity_list:
                    logger.info(f"  🔹 {entity_type}: {len(entity_list)} entities")
                    
                    for entity in entity_list[:2]:  # Show first 2 entities
                        if hasattr(entity, 'code'):
                            logger.info(f"    - Code: {entity.code}, Confidence: {entity.confidence}")
                        elif hasattr(entity, 'name'):
                            logger.info(f"    - Name: {entity.name}, Confidence: {entity.confidence}")
            
            total_entities = sum(len(entity_list) for entity_list in parsed_entities.values())
            
            if total_entities > 0:
                logger.info(f"✅ Successfully extracted {total_entities} entities!")
                return True
            else:
                logger.warning("⚠️ No entities extracted from sample text")
                return False
                
        except Exception as e:
            logger.error(f"Error in sample text test: {str(e)}")
            return False
    
    async def test_with_pdf_file(self, pdf_path: str) -> bool:
        """Test extraction with actual PDF file"""
        
        logger.info(f"Testing with PDF file: {pdf_path}")
        
        # Validate PDF file first
        validation = validate_pdf_file(pdf_path)
        
        if not validation["is_valid"]:
            logger.error("❌ PDF file validation failed:")
            for error in validation["errors"]:
                logger.error(f"  - {error}")
            return False
        
        logger.info(f"✅ PDF validated: {validation['page_count']} pages, {validation['file_size']/1024/1024:.1f}MB")
        
        try:
            # Process PDF
            pdf_document = self.pdf_processor.process_pdf(pdf_path)
            
            logger.info(f"📄 PDF processed: {pdf_document.total_pages} pages")
            
            # Get error code pages (most relevant for testing)
            error_code_pages = self.pdf_processor.get_error_code_pages(pdf_document)
            
            if not error_code_pages:
                logger.warning("⚠️ No error code pages found in PDF")
                # Use first few pages instead
                test_pages = pdf_document.pages[:3]
            else:
                test_pages = error_code_pages[:2]  # Test first 2 error code pages
            
            logger.info(f"🔍 Testing extraction on {len(test_pages)} pages")
            
            # Initialize Gemini client if not already done
            if not self.gemini_client:
                self.gemini_client = GeminiClient()
            
            total_entities_found = 0
            
            for page in test_pages:
                logger.info(f"  Processing page {page.page_number}...")
                
                # Skip very short pages
                if len(page.text_content.strip()) < 100:
                    logger.info(f"    Skipping short page ({len(page.text_content)} chars)")
                    continue
                
                # Extract entities using Gemini
                result = await self.gemini_client.extract_medical_entities(
                    page_content=page.text_content,
                    device_type="linear_accelerator"
                )
                
                # Parse result
                parsed_entities = self.entity_parser.parse_gemini_response(
                    response=json.dumps(result) if isinstance(result, dict) else str(result),
                    page_number=page.page_number,
                    source_text=page.text_content
                )
                
                # Count entities for this page
                page_entities = sum(len(entity_list) for entity_list in parsed_entities.values())
                total_entities_found += page_entities
                
                logger.info(f"    Found {page_entities} entities on page {page.page_number}")
                
                # Show sample entities
                for entity_type, entity_list in parsed_entities.items():
                    if entity_list:
                        sample_entity = entity_list[0]
                        if hasattr(sample_entity, 'code'):
                            logger.info(f"      Sample {entity_type}: {sample_entity.code}")
                        elif hasattr(sample_entity, 'name'):
                            logger.info(f"      Sample {entity_type}: {sample_entity.name}")
            
            if total_entities_found > 0:
                logger.info(f"✅ Successfully extracted {total_entities_found} total entities from PDF!")
                return True
            else:
                logger.warning("⚠️ No entities extracted from PDF")
                return False
                
        except Exception as e:
            logger.error(f"Error in PDF test: {str(e)}")
            return False
    
    async def run_full_test_suite(self) -> Dict[str, bool]:
        """Run complete test suite"""
        
        logger.info("🚀 Starting full test suite for Medical Device Ontology Extraction System")
        
        results = {}
        
        # Test 1: Gemini connection
        logger.info("\n" + "="*60)
        logger.info("TEST 1: Gemini Flash API Connection")
        logger.info("="*60)
        results["gemini_connection"] = await self.test_gemini_connection()
        
        if not results["gemini_connection"]:
            logger.error("❌ Gemini connection failed - skipping other tests")
            return results
        
        # Test 2: Sample text extraction
        logger.info("\n" + "="*60)
        logger.info("TEST 2: Sample Text Extraction")
        logger.info("="*60)
        results["sample_text"] = await self.test_with_sample_text()
        
        # Test 3: PDF file processing
        logger.info("\n" + "="*60)
        logger.info("TEST 3: PDF File Processing")
        logger.info("="*60)
        
        # Look for test PDF files
        pdf_paths = [
            "data/medical_manuals/MLCi_Manual.pdf",
            "data/input/4.2 MLCi2 Subsystem.pdf",
            "uploads/test.pdf"
        ]
        
        pdf_test_success = False
        
        for pdf_path in pdf_paths:
            if os.path.exists(pdf_path):
                logger.info(f"Found PDF file: {pdf_path}")
                pdf_test_success = await self.test_with_pdf_file(pdf_path)
                break
        
        if not pdf_test_success:
            logger.warning("⚠️ No test PDF files found. Checked:")
            for path in pdf_paths:
                logger.warning(f"  - {path}")
            logger.warning("Place a medical device PDF in one of these locations to test PDF processing")
        
        results["pdf_processing"] = pdf_test_success
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        for test_name, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{test_name:20}: {status}")
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All tests passed! System is ready for use.")
        elif passed_tests >= 2:
            logger.info("⚠️ Core functionality working. Some tests failed.")
        else:
            logger.error("❌ Multiple test failures. Check configuration.")
        
        return results
    
    def create_test_directories(self):
        """Create necessary test directories"""
        
        directories = [
            "data/medical_manuals",
            "data/extracted_entities", 
            "data/reviewed_data",
            "logs",
            "uploads"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
            # Create .gitkeep files
            gitkeep_path = os.path.join(directory, ".gitkeep")
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, "w") as f:
                    f.write("# Keep this directory in git\n")


async def main():
    """Main test function"""
    
    print("🏥 Medical Device Ontology Extraction System - Quick Test")
    print("=" * 60)
    
    # Create test runner
    test_runner = QuickTestRunner()
    
    # Create directories
    test_runner.create_test_directories()
    
    # Run tests
    try:
        results = await test_runner.run_full_test_suite()
        
        # Exit with appropriate code
        if all(results.values()):
            sys.exit(0)  # All tests passed
        else:
            sys.exit(1)  # Some tests failed
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(2)
    except Exception as e:
        logger.error(f"Test suite failed with exception: {str(e)}")
        sys.exit(3)


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
