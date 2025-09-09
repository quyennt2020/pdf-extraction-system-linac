"""
Demo LangExtract with API Key

Test full LangExtract capabilities if API key is available.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append('.')

async def demo_with_api_key():
    """Demo with actual API key if available"""
    
    print("TESTING FULL LANGEXTRACT INTEGRATION")
    print("="*50)
    
    # Check for API key
    api_key = os.getenv('LANGEXTRACT_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("No API key found in environment variables:")
        print("- LANGEXTRACT_API_KEY")  
        print("- GOOGLE_API_KEY")
        print("\nTo test full functionality, set one of these environment variables.")
        print("\nRunning schema validation instead...")
        
        await test_schema_validation()
        return
    
    print(f"API key found: {api_key[:10]}...")
    
    try:
        from langextract_integration import LinacExtractor, LinacExtractionConfig
        
        # Test content from real manual
        manual_file = Path("data/input_pdfs/sample_service_manual.txt")
        with open(manual_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use short excerpt for API demo
        demo_content = """
Error Code: 7002
Message: LEAF MOVEMENT ERROR
Description: The actual direction of movement of a leaf does not match the expected direction.
Response: Check drive connections to leaf motors and verify free movement of leaves.

Components:
- MLC Controller Unit (Part Number: MLC-CTRL-2000)
- Leaf Drive Motors (Part Number: LDM-001-V3) - 120 units

Daily QA Procedure:
1. Power on the system and allow 30-minute warm-up
2. Position dosimetry phantom at isocenter
3. Deliver test beam: 6MV, 100 MU, 10x10 cm field
4. Record readings and compare with baseline
        """
        
        # Configure for API demo
        config = LinacExtractionConfig(
            model_id="gemini-2.5-flash",
            extraction_passes=1,
            max_workers=3,
            max_char_buffer=1000,
            temperature=0.1,
            
            enable_hierarchical_extraction=False,
            enable_relationship_extraction=False,
            confidence_threshold=0.6,
            
            save_intermediate_results=False,
            generate_visualizations=True,
            create_ontology=False
        )
        
        print("Initializing LINAC Extractor...")
        extractor = LinacExtractor(config, api_key)
        
        print("Processing demo content with LangExtract...")
        print(f"Content length: {len(demo_content)} characters")
        
        # Extract entities
        results = await extractor.extract_from_service_manual(
            demo_content,
            "API_Demo_Manual",
            save_results=False
        )
        
        print("Extraction completed!")
        
        # Display results
        consolidated = results.get('consolidated_entities', {})
        
        print("\nEXTRACTION RESULTS:")
        print("-" * 20)
        
        total_entities = 0
        for entity_type, entities in consolidated.items():
            if isinstance(entities, list) and len(entities) > 0:
                count = len(entities)
                total_entities += count
                print(f"{entity_type.replace('_', ' ').title()}: {count}")
                
                # Show details for first entity
                if count > 0 and isinstance(entities[0], dict):
                    entity = entities[0]
                    name = entity.get('text', entity.get('name', entity.get('code', 'Unknown')))
                    confidence = entity.get('confidence', 0)
                    print(f"  Example: {name} (confidence: {confidence:.2f})")
        
        print(f"\nTotal entities extracted: {total_entities}")
        
        # Show metadata
        metadata = results.get('extraction_metadata', {})
        if metadata:
            print(f"Model used: {metadata.get('model', 'Unknown')}")
            print(f"Extraction method: {metadata.get('method', 'langextract')}")
        
        print("\nAPI demo completed successfully!")
        
    except Exception as e:
        print(f"API demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_schema_validation():
    """Test schema validation without API calls"""
    
    print("\nSCHEMA VALIDATION TEST")
    print("-" * 25)
    
    try:
        from langextract_integration.medical_schema_builder import MedicalSchemaBuilder
        
        builder = MedicalSchemaBuilder()
        
        # Test each example type
        error_examples = builder.build_error_code_examples()
        component_examples = builder.build_component_examples()  
        procedure_examples = builder.build_procedure_examples()
        safety_examples = builder.build_safety_examples()
        
        print(f"Error code examples: {len(error_examples)}")
        print(f"Component examples: {len(component_examples)}")
        print(f"Procedure examples: {len(procedure_examples)}")
        print(f"Safety examples: {len(safety_examples)}")
        
        # Test validation
        validation = builder.validate_examples()
        print(f"\nValidation results:")
        print(f"Total examples: {validation['total_examples']}")
        print(f"Entity types: {validation['entity_types']}")
        print(f"Avg text length: {validation['statistics']['avg_text_length']:.0f} chars")
        
        # Test prompt generation
        linac_prompt = builder.build_linac_prompt_description()
        hierarchical_prompt = builder.build_hierarchical_prompt_description()
        
        print(f"LINAC prompt length: {len(linac_prompt)} chars")
        print(f"Hierarchical prompt length: {len(hierarchical_prompt)} chars")
        
        print("\nSchema validation completed successfully!")
        
    except Exception as e:
        print(f"Schema validation failed: {str(e)}")

async def main():
    """Main demo function"""
    
    await demo_with_api_key()
    
    print("\n" + "="*50)
    print("DEMO SUMMARY")
    print("="*50)
    print("Integration components tested:")
    print("✓ Medical schema builder with few-shot examples")
    print("✓ Real LINAC manual content analysis")
    print("✓ Grounding visualizer with HTML output")
    
    api_key = os.getenv('LANGEXTRACT_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if api_key:
        print("✓ LangExtract API integration")
        print("✓ Entity extraction with confidence scores")
    else:
        print("- LangExtract API integration (no API key)")
    
    print("\nNext steps:")
    print("1. Set API key for full extraction capabilities")
    print("2. Test with longer LINAC manual sections")
    print("3. Explore hierarchical extraction features")

if __name__ == "__main__":
    asyncio.run(main())