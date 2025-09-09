"""
Demo Real LINAC Manual Processing

Simple demo without Unicode characters to test LangExtract integration
with real LINAC service manual content.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path  
sys.path.append('.')

async def demo_real_linac_processing():
    """Demo processing with real LINAC manual"""
    
    print("="*60)
    print("TESTING LANGEXTRACT WITH REAL LINAC MANUAL")
    print("="*60)
    
    try:
        # Read real LINAC manual content
        manual_file = Path("data/input_pdfs/sample_service_manual.txt")
        
        if not manual_file.exists():
            print(f"Manual file not found: {manual_file}")
            return
        
        print(f"Reading LINAC manual: {manual_file}")
        
        with open(manual_file, 'r', encoding='utf-8') as f:
            manual_content = f.read()
        
        print(f"Manual content: {len(manual_content):,} characters")
        
        # Check for API key
        api_key = os.getenv('LANGEXTRACT_API_KEY') or os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            print("No API key found - running local analysis only")
            await analyze_manual_content(manual_content)
            await create_mock_visualization(manual_content)
            return
        
        print(f"API key found: {api_key[:10]}...")
        
        # Run actual LangExtract processing
        await run_langextract_demo(manual_content, api_key)
        
    except Exception as e:
        print(f"Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def analyze_manual_content(content: str):
    """Analyze the manual content structure"""
    
    print("\nMANUAL CONTENT ANALYSIS")
    print("-" * 30)
    
    lines = content.split('\n')
    
    # Find error codes
    error_codes = []
    components = []
    procedures = []
    
    for line in lines:
        line_clean = line.strip()
        
        if line_clean.startswith("Error Code:"):
            error_codes.append(line_clean)
        elif "Part Number:" in line_clean:
            components.append(line_clean)
        elif line_clean.startswith(("1.", "2.", "3.", "4.", "5.")) and len(line_clean) > 15:
            procedures.append(line_clean)
    
    print(f"Error codes found: {len(error_codes)}")
    for code in error_codes:
        print(f"  - {code}")
    
    print(f"\nComponents with part numbers: {len(components)}")
    for comp in components:
        print(f"  - {comp}")
    
    print(f"\nProcedure steps: {len(procedures)}")
    for proc in procedures[:5]:  # Show first 5
        print(f"  - {proc}")
    
    print(f"\nTotal: {len(content):,} chars, {len(lines)} lines")

async def create_mock_visualization(content: str):
    """Create visualization with mock extraction results"""
    
    print("\nCREATING MOCK VISUALIZATION")
    print("-" * 30)
    
    try:
        from langextract_integration.grounding_visualizer import GroundingVisualizer
        
        visualizer = GroundingVisualizer()
        
        # Create mock results based on manual analysis
        mock_results = {
            "consolidated_entities": {
                "error_codes": [
                    {
                        "code": "7002",
                        "text": "7002",
                        "confidence": 0.95,
                        "attributes": {
                            "message": "LEAF MOVEMENT ERROR",
                            "description": "Leaf direction mismatch or stationary leaf moved",
                            "category": "Mechanical"
                        },
                        "source_location": {
                            "start_char": content.find("Error Code: 7002"),
                            "end_char": content.find("Error Code: 7002") + 4,
                            "context": "Error Code: 7002"
                        }
                    },
                    {
                        "code": "7003",
                        "text": "7003",
                        "confidence": 0.92,
                        "attributes": {
                            "message": "LEAF POSITION TIMEOUT",
                            "description": "Leaf not reached position in time",
                            "category": "Mechanical"
                        },
                        "source_location": {
                            "start_char": content.find("Error Code: 7003"),
                            "end_char": content.find("Error Code: 7003") + 4,
                            "context": "Error Code: 7003"
                        }
                    }
                ],
                "components": [
                    {
                        "name": "MLC Controller Unit",
                        "text": "MLC Controller Unit",
                        "confidence": 0.88,
                        "attributes": {
                            "part_number": "MLC-CTRL-2000",
                            "type": "controller",
                            "function": "Controls MLC leaf positioning"
                        },
                        "source_location": {
                            "start_char": content.find("MLC Controller Unit"),
                            "end_char": content.find("MLC Controller Unit") + 19,
                            "context": "MLC Controller Unit (Part Number: MLC-CTRL-2000)"
                        }
                    },
                    {
                        "name": "Leaf Drive Motors",
                        "text": "Leaf Drive Motors", 
                        "confidence": 0.90,
                        "attributes": {
                            "part_number": "LDM-001-V3",
                            "type": "actuator",
                            "quantity": "120 units"
                        },
                        "source_location": {
                            "start_char": content.find("Leaf Drive Motors"),
                            "end_char": content.find("Leaf Drive Motors") + 17,
                            "context": "Leaf Drive Motors (Part Number: LDM-001-V3)"
                        }
                    }
                ]
            },
            "extraction_metadata": {
                "model": "mock_processing",
                "method": "local_analysis",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Create visualization
        viz_file = visualizer.create_grounded_visualization(
            mock_results,
            content[:2000],  # Use first 2000 chars for demo
            "demo_real_linac_visualization.html",
            "Real LINAC Manual Demo"
        )
        
        print(f"Visualization created: {viz_file}")
        
        # Show some statistics
        print(f"\nMock extraction results:")
        print(f"  Error codes: {len(mock_results['consolidated_entities']['error_codes'])}")
        print(f"  Components: {len(mock_results['consolidated_entities']['components'])}")
        
    except Exception as e:
        print(f"Visualization creation failed: {str(e)}")

async def run_langextract_demo(content: str, api_key: str):
    """Run actual LangExtract processing (if API key available)"""
    
    print("\nRUNNING LANGEXTRACT PROCESSING")
    print("-" * 30)
    
    try:
        from langextract_integration import (
            LinacExtractor, 
            LinacExtractionConfig
        )
        
        # Configure for demo
        config = LinacExtractionConfig(
            model_id="gemini-2.5-flash",
            extraction_passes=1,  # Single pass for demo
            max_workers=5,
            max_char_buffer=1500,
            temperature=0.1,
            
            enable_hierarchical_extraction=False,  # Simplified for demo
            enable_relationship_extraction=False,
            confidence_threshold=0.6,
            
            save_intermediate_results=True,
            generate_visualizations=True,
            create_ontology=False  # Skip for demo
        )
        
        extractor = LinacExtractor(config, api_key)
        
        # Process first 2000 characters for demo
        demo_content = content[:2000]
        print(f"Processing {len(demo_content)} characters...")
        
        start_time = datetime.now()
        
        results = await extractor.extract_from_service_manual(
            demo_content,
            "Real_LINAC_Demo",
            save_results=True
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"Processing completed in {processing_time:.2f} seconds")
        
        # Show results
        await show_extraction_results(results)
        
    except Exception as e:
        print(f"LangExtract processing failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def show_extraction_results(results: dict):
    """Display extraction results"""
    
    print("\nEXTRACTION RESULTS")
    print("-" * 20)
    
    consolidated = results.get('consolidated_entities', {})
    
    for entity_type, entities in consolidated.items():
        if isinstance(entities, list) and len(entities) > 0:
            print(f"\n{entity_type.replace('_', ' ').title()}: {len(entities)}")
            
            for i, entity in enumerate(entities[:2]):  # Show first 2
                if isinstance(entity, dict):
                    name = entity.get('text', entity.get('name', entity.get('code', 'Unknown')))
                    confidence = entity.get('confidence', 0)
                    print(f"  {i+1}. {name} (confidence: {confidence:.2f})")
                    
                    # Show key attributes
                    attrs = entity.get('attributes', {})
                    for key, value in list(attrs.items())[:2]:  # Show first 2 attributes
                        if isinstance(value, str) and len(value) < 80:
                            print(f"     {key}: {value}")
    
    # Show metadata
    metadata = results.get('extraction_metadata', {})
    if metadata:
        print(f"\nProcessing info:")
        print(f"  Model: {metadata.get('model', 'Unknown')}")
        print(f"  Method: {metadata.get('method', 'Unknown')}")

async def main():
    """Main demo function"""
    
    await demo_real_linac_processing()
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60)
    print("Files created:")
    print("- demo_real_linac_visualization.html")
    print("- Any LangExtract result files in data/langextract_results/")
    print("\nOpen the HTML file in your browser to see entity highlighting!")

if __name__ == "__main__":
    asyncio.run(main())