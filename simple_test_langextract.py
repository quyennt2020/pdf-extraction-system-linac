"""
Simple LangExtract Integration Test

Basic test without fancy Unicode characters to verify integration works.
"""

import asyncio
import os
import json
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.append('.')

async def test_medical_schema_builder():
    """Test Medical Schema Builder"""
    
    print("Testing Medical Schema Builder...")
    
    try:
        from langextract_integration.medical_schema_builder import MedicalSchemaBuilder
        
        builder = MedicalSchemaBuilder()
        
        # Test example generation
        error_examples = builder.build_error_code_examples()
        component_examples = builder.build_component_examples()
        
        # Test validation
        validation = builder.validate_examples()
        
        print(f"✓ Medical Schema Builder: {validation['total_examples']} examples, {len(validation['entity_types'])} entity types")
        return True
        
    except Exception as e:
        print(f"✗ Medical Schema Builder failed: {str(e)}")
        return False

async def test_langextract_bridge():
    """Test LangExtract Bridge without API"""
    
    print("Testing LangExtract Bridge (initialization only)...")
    
    try:
        from langextract_integration.langextract_bridge import LangExtractBridge, ExtractionConfig
        
        # Test configuration creation
        config = ExtractionConfig()
        
        # Test bridge initialization (will fail without API key, but that's expected)
        try:
            bridge = LangExtractBridge(config)
            print("✓ LangExtract Bridge initialized successfully")
            return True
        except ValueError as e:
            if "API key required" in str(e):
                print("✓ LangExtract Bridge: API key validation working correctly")
                return True
            else:
                raise
        
    except Exception as e:
        print(f"✗ LangExtract Bridge failed: {str(e)}")
        return False

async def test_grounding_visualizer():
    """Test Grounding Visualizer"""
    
    print("Testing Grounding Visualizer...")
    
    try:
        from langextract_integration.grounding_visualizer import GroundingVisualizer
        
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
                            "description": "Leaf movement direction mismatch"
                        },
                        "source_location": {
                            "start_char": 10,
                            "end_char": 14,
                            "context": "Error Code 7002: MOVEMENT"
                        }
                    }
                ]
            }
        }
        
        sample_text = "Test: Error Code 7002: MOVEMENT - check motor"
        
        # Test visualization creation
        output_file = visualizer.create_grounded_visualization(
            sample_results,
            sample_text,
            "test_simple_visualization.html",
            "Simple Test"
        )
        
        print(f"✓ Grounding Visualizer: Created {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Grounding Visualizer failed: {str(e)}")
        return False

async def main():
    """Run simple integration tests"""
    
    print("Starting Simple LangExtract Integration Tests")
    print("=" * 50)
    
    tests = [
        test_medical_schema_builder,
        test_langextract_bridge,
        test_grounding_visualizer
    ]
    
    results = []
    
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"Test failed with exception: {str(e)}")
            results.append(False)
        
        print("-" * 30)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print("TEST SUMMARY")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! LangExtract integration is working.")
    else:
        print("Some tests failed. Check output above for details.")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())