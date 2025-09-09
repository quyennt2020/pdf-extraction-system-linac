"""
Test LangExtract Integration

This script tests the complete LangExtract integration with sample LINAC data
to verify that all components work together correctly.
"""

import asyncio
import os
import json
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our integration modules
from langextract_integration import (
    LinacExtractor,
    LinacExtractionConfig,
    MedicalSchemaBuilder,
    LangExtractBridge,
    GroundingVisualizer
)


class LangExtractIntegrationTest:
    """Comprehensive test suite for LangExtract integration"""
    
    def __init__(self):
        self.test_results = {}
        self.sample_linac_content = """
LINAC Service Manual - MLCi and MLCi2 Systems
Software Version: R6.0x, R6.1x, R7.0x\\Integrity™ R1.1

SECTION 1: ERROR CODES AND TROUBLESHOOTING

Error Code 7002: MOVEMENT
Software Release: R6.0x, R6.1x, R7.0x\\Integrity™ R1.1
Description: The actual direction of movement of a leaf does not match the expected direction.
Response: Check the drive to the leaf motors and the leaves for free movement.
Category: Mechanical
Severity: High

Error Code 5001: CALIBRATION FAILURE  
Software Release: R7.0x, R7.1x
Description: Beam calibration values are outside acceptable tolerance range.
Response: Recalibrate beam delivery system. Contact service engineer if problem persists.
Category: Software
Severity: Critical

SECTION 2: COMPONENTS AND SUBSYSTEMS

Multi-Leaf Collimator (MLC) System:
The gantry rotation motor (Model: GRM-450X, Part Number: 12345-ABC) provides precise 
angular positioning for the treatment head. The motor is controlled by the gantry 
control unit and monitored by position encoders for accuracy verification.
Specifications: 360° rotation, ±0.1° accuracy, maximum speed 6 RPM.

Beam Delivery System:
- Primary collimator: Defines maximum field size
- Secondary collimator: Provides rectangular field shaping
- Multi-leaf collimator: Enables conformal field shaping
- Monitor chambers: Verify dose delivery accuracy

Patient Positioning System:
- Treatment couch with 6-axis movement capability
- Patient immobilization devices
- Laser positioning system for setup verification
- Image-guided positioning (IGRT) integration

SECTION 3: MAINTENANCE PROCEDURES

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

Weekly QA Procedure - Mechanical Checks:
1. Verify gantry rotation accuracy at cardinal angles
2. Check collimator rotation and jaw positions
3. Test treatment couch movements and positioning
4. Inspect laser alignment system
5. Document all measurements
Prerequisites: System in service mode
Tools Required: Mechanical QA phantom, measurement tools
Safety Level: Level 1 (Standard precautions)
Estimated Time: 2 hours

SECTION 4: SAFETY PROTOCOLS

⚠️ WARNING: High Voltage Hazard
Before opening the magnetron cabinet, ensure that:
- Main power is OFF and locked out
- High voltage discharge procedure is completed  
- Wait minimum 10 minutes for capacitor discharge
- Verify zero energy state with approved meter
- Use insulated tools only
Compliance Standard: IEC 60601-2-1, Section 12.4.3
Violation may result in serious injury or death.

⚠️ CAUTION: Radiation Area
When beam is enabled:
- Ensure all personnel are clear of treatment room
- Verify interlock system functionality
- Monitor radiation levels with appropriate detectors
- Follow institutional radiation safety procedures
Compliance Standard: IEC 60601-2-1, Radiation Safety

SECTION 5: TECHNICAL SPECIFICATIONS

System Power Requirements:
- Primary power: 480V, 3-phase, 60Hz
- Maximum power consumption: 50 kW
- Emergency stop circuits: Hardwired, fail-safe design
- Uninterruptible power supply (UPS): 15-minute backup

Environmental Requirements:
- Operating temperature: 20-25°C (±2°C)
- Humidity: 45-65% RH (non-condensing)
- Atmospheric pressure: 86-106 kPa
- Vibration: Maximum 0.5g acceleration
- Electromagnetic compatibility: IEC 60601-1-2 compliance
"""
    
    async def run_all_tests(self):
        """Run comprehensive integration tests"""
        
        logger.info("🚀 Starting LangExtract Integration Tests")
        
        try:
            # Test 1: Medical Schema Builder
            await self.test_medical_schema_builder()
            
            # Test 2: LangExtract Bridge 
            await self.test_langextract_bridge()
            
            # Test 3: LINAC Extractor
            await self.test_linac_extractor()
            
            # Test 4: Grounding Visualizer
            await self.test_grounding_visualizer()
            
            # Test 5: End-to-End Integration
            await self.test_end_to_end_integration()
            
            # Generate test report
            self.generate_test_report()
            
            logger.info("✅ All LangExtract integration tests completed")
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {str(e)}")
            raise
    
    async def test_medical_schema_builder(self):
        """Test Medical Schema Builder"""
        
        logger.info("Testing Medical Schema Builder...")
        
        try:
            builder = MedicalSchemaBuilder()
            
            # Test example generation
            error_examples = builder.build_error_code_examples()
            component_examples = builder.build_component_examples()
            procedure_examples = builder.build_procedure_examples()
            safety_examples = builder.build_safety_examples()
            
            # Test prompt generation
            linac_prompt = builder.build_linac_prompt_description()
            hierarchical_prompt = builder.build_hierarchical_prompt_description("Beam Delivery System")
            
            # Test validation
            validation = builder.validate_examples()
            
            self.test_results["medical_schema_builder"] = {
                "status": "passed",
                "error_examples": len(error_examples),
                "component_examples": len(component_examples),
                "procedure_examples": len(procedure_examples), 
                "safety_examples": len(safety_examples),
                "linac_prompt_length": len(linac_prompt),
                "hierarchical_prompt_length": len(hierarchical_prompt),
                "validation": validation
            }
            
            logger.info(f"✅ Medical Schema Builder: {validation['total_examples']} examples, {len(validation['entity_types'])} entity types")
            
        except Exception as e:
            self.test_results["medical_schema_builder"] = {
                "status": "failed",
                "error": str(e)
            }
            logger.error(f"❌ Medical Schema Builder failed: {str(e)}")
    
    async def test_langextract_bridge(self):
        """Test LangExtract Bridge"""
        
        logger.info("Testing LangExtract Bridge...")
        
        try:
            # Check API key
            api_key = os.getenv('LANGEXTRACT_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if not api_key:
                self.test_results["langextract_bridge"] = {
                    "status": "skipped",
                    "reason": "No API key found"
                }
                logger.warning("⚠️ LangExtract Bridge test skipped - no API key")
                return
            
            from langextract_integration.langextract_bridge import ExtractionConfig
            
            config = ExtractionConfig(
                extraction_passes=1,  # Reduced for testing
                max_workers=5,
                api_key=api_key
            )
            
            bridge = LangExtractBridge(config)
            
            # Test with sample content
            test_content = """
            Error Code 7002: MOVEMENT
            Description: Leaf movement direction mismatch.
            The gantry rotation motor provides precise positioning.
            """
            
            result = await bridge.extract_medical_entities(test_content)
            
            entity_count = bridge._count_entities(result)
            
            self.test_results["langextract_bridge"] = {
                "status": "passed",
                "entities_extracted": entity_count,
                "extraction_metadata": result.get("extraction_metadata", {}),
                "entity_types": list(result.keys())
            }
            
            logger.info(f"✅ LangExtract Bridge: {entity_count} entities extracted")
            
        except Exception as e:
            self.test_results["langextract_bridge"] = {
                "status": "failed", 
                "error": str(e)
            }
            logger.error(f"❌ LangExtract Bridge failed: {str(e)}")
    
    async def test_linac_extractor(self):
        """Test LINAC Extractor"""
        
        logger.info("Testing LINAC Extractor...")
        
        try:
            # Check API key
            api_key = os.getenv('LANGEXTRACT_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if not api_key:
                self.test_results["linac_extractor"] = {
                    "status": "skipped",
                    "reason": "No API key found"
                }
                logger.warning("⚠️ LINAC Extractor test skipped - no API key")
                return
            
            # Quick test configuration
            config = LinacExtractionConfig(
                extraction_passes=1,
                max_workers=3,
                enable_hierarchical_extraction=False,  # Simplified for testing
                save_intermediate_results=False,
                generate_visualizations=False,
                create_ontology=False
            )
            
            extractor = LinacExtractor(config, api_key)
            
            # Test with shortened content
            test_content = self.sample_linac_content[:1000]  # Limit for testing
            
            result = await extractor.extract_from_service_manual(
                test_content,
                "Test Manual",
                save_results=False
            )
            
            # Get statistics
            stats = {}
            if "consolidated_entities" in result:
                consolidated = result["consolidated_entities"]
                stats = consolidated.get("statistics", {})
            
            self.test_results["linac_extractor"] = {
                "status": "passed",
                "extraction_stages": len(result.get("stages", {})),
                "statistics": stats
            }
            
            logger.info(f"✅ LINAC Extractor: {stats.get('total_entities', 0)} total entities")
            
        except Exception as e:
            self.test_results["linac_extractor"] = {
                "status": "failed",
                "error": str(e)
            }
            logger.error(f"❌ LINAC Extractor failed: {str(e)}")
    
    async def test_grounding_visualizer(self):
        """Test Grounding Visualizer"""
        
        logger.info("Testing Grounding Visualizer...")
        
        try:
            visualizer = GroundingVisualizer()
            
            # Create sample results
            sample_results = {
                "consolidated_entities": {
                    "error_codes": [
                        {
                            "code": "7002",
                            "text": "7002",
                            "confidence": 0.95,
                            "attributes": {
                                "message": "MOVEMENT",
                                "description": "Leaf movement direction mismatch",
                                "category": "Mechanical"
                            },
                            "source_location": {
                                "start_char": 50,
                                "end_char": 54,
                                "context": "Error Code 7002: MOVEMENT"
                            }
                        }
                    ],
                    "components": [
                        {
                            "name": "gantry rotation motor",
                            "text": "gantry rotation motor",
                            "confidence": 0.88,
                            "attributes": {
                                "type": "motor",
                                "function": "precise angular positioning"
                            },
                            "source_location": {
                                "start_char": 200,
                                "end_char": 221,
                                "context": "The gantry rotation motor provides precise positioning"
                            }
                        }
                    ]
                },
                "extraction_metadata": {
                    "model": "gemini-2.5-flash",
                    "extraction_passes": 1,
                    "examples_used": 4
                }
            }
            
            sample_text = """
LINAC Service Manual Test

Error Code 7002: MOVEMENT
Description: Leaf movement direction mismatch.

The gantry rotation motor provides precise angular positioning for the treatment head.
"""
            
            # Test visualization creation
            output_file = visualizer.create_grounded_visualization(
                sample_results,
                sample_text,
                "test_visualization.html",
                "Test LINAC Visualization"
            )
            
            # Check if file was created
            if Path(output_file).exists():
                file_size = Path(output_file).stat().st_size
                self.test_results["grounding_visualizer"] = {
                    "status": "passed",
                    "output_file": output_file,
                    "file_size_bytes": file_size
                }
                logger.info(f"✅ Grounding Visualizer: Created {output_file} ({file_size} bytes)")
            else:
                raise Exception("Visualization file not created")
            
        except Exception as e:
            self.test_results["grounding_visualizer"] = {
                "status": "failed",
                "error": str(e)
            }
            logger.error(f"❌ Grounding Visualizer failed: {str(e)}")
    
    async def test_end_to_end_integration(self):
        """Test complete end-to-end integration"""
        
        logger.info("Testing End-to-End Integration...")
        
        try:
            # Check API key
            api_key = os.getenv('LANGEXTRACT_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if not api_key:
                self.test_results["end_to_end"] = {
                    "status": "skipped",
                    "reason": "No API key found"
                }
                logger.warning("⚠️ End-to-End test skipped - no API key")
                return
            
            # Full integration test with minimal configuration
            config = LinacExtractionConfig(
                extraction_passes=1,
                max_workers=3,
                enable_hierarchical_extraction=True,
                enable_relationship_extraction=False,  # Skip for testing
                save_intermediate_results=True,
                generate_visualizations=True,
                create_ontology=False  # Skip for testing
            )
            
            extractor = LinacExtractor(config, api_key)
            
            # Use first part of sample content
            test_content = self.sample_linac_content[:2000]
            
            # Run full extraction
            result = await extractor.extract_from_service_manual(
                test_content,
                "End_to_End_Test_Manual",
                save_results=True
            )
            
            # Get comprehensive statistics
            stats = extractor.get_extraction_statistics(result)
            
            self.test_results["end_to_end"] = {
                "status": "passed",
                "statistics": stats,
                "visualization_created": "visualization_file" in result,
                "files_saved": result.get("stages", {}) is not None
            }
            
            logger.info(f"✅ End-to-End Integration: {stats.get('total_entities', 0)} entities, {stats.get('extraction_stages', 0)} stages")
            
        except Exception as e:
            self.test_results["end_to_end"] = {
                "status": "failed",
                "error": str(e)
            }
            logger.error(f"❌ End-to-End Integration failed: {str(e)}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        
        report = {
            "test_suite": "LangExtract Integration",
            "timestamp": str(Path(__file__).stat().st_mtime),
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results.values() if r.get("status") == "passed"),
                "failed": sum(1 for r in self.test_results.values() if r.get("status") == "failed"),
                "skipped": sum(1 for r in self.test_results.values() if r.get("status") == "skipped")
            },
            "detailed_results": self.test_results
        }
        
        # Save report
        report_file = Path("test_langextract_integration_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        # Print summary
        print("\n" + "="*60)
        print("🧪 LANGEXTRACT INTEGRATION TEST REPORT")
        print("="*60)
        print(f"📊 Total Tests: {report['summary']['total_tests']}")
        print(f"✅ Passed: {report['summary']['passed']}")
        print(f"❌ Failed: {report['summary']['failed']}")
        print(f"⚠️ Skipped: {report['summary']['skipped']}")
        print(f"📄 Full report: {report_file}")
        
        # Print individual test results
        for test_name, result in self.test_results.items():
            status_icon = {"passed": "✅", "failed": "❌", "skipped": "⚠️"}.get(result["status"], "❓")
            print(f"   {status_icon} {test_name}: {result['status']}")
            if result.get("error"):
                print(f"      Error: {result['error']}")
        
        print("="*60)


async def main():
    """Run the integration test suite"""
    
    # Check if API key is available
    api_key = os.getenv('LANGEXTRACT_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("⚠️ Warning: No API key found. Set LANGEXTRACT_API_KEY or GOOGLE_API_KEY environment variable.")
        print("Some tests will be skipped.")
        print()
    
    # Run tests
    test_suite = LangExtractIntegrationTest()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())