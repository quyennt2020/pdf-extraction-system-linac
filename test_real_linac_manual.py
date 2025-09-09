"""
Test Real LINAC Manual with LangExtract Integration

This script demonstrates the complete LangExtract integration using real
LINAC service manual content from the data/input_pdfs directory.
"""

import asyncio
import os
import json
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append('.')

# Import our integration modules
from langextract_integration import (
    LinacExtractor,
    LinacExtractionConfig,
    GroundingVisualizer
)


async def test_with_real_linac_manual():
    """Test LangExtract integration with real LINAC manual content"""
    
    print("="*80)
    print("🏥 TESTING LANGEXTRACT INTEGRATION WITH REAL LINAC MANUAL")
    print("="*80)
    
    try:
        # Read the real LINAC manual content
        manual_file = Path("data/input_pdfs/sample_service_manual.txt")
        
        if not manual_file.exists():
            print(f"❌ Manual file not found: {manual_file}")
            return
        
        print(f"📖 Reading LINAC manual: {manual_file}")
        
        with open(manual_file, 'r', encoding='utf-8') as f:
            manual_content = f.read()
        
        content_length = len(manual_content)
        print(f"📊 Manual content: {content_length:,} characters")
        
        # Check API key
        api_key = os.getenv('LANGEXTRACT_API_KEY') or os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            print("⚠️  No API key found - running local processing only")
            await test_local_processing(manual_content)
            return
        
        print(f"🔑 API key found: {api_key[:10]}...")
        
        # Configure for real manual processing
        config = LinacExtractionConfig(
            model_id="gemini-2.5-flash",
            extraction_passes=2,  # Multi-pass for better accuracy
            max_workers=8,
            max_char_buffer=2000,  # Larger buffer for complex content
            temperature=0.1,  # Lower temperature for consistency
            
            # LINAC specific settings
            enable_hierarchical_extraction=True,
            enable_relationship_extraction=True,
            confidence_threshold=0.6,  # Lower threshold for real data
            
            # Output settings
            save_intermediate_results=True,
            generate_visualizations=True,
            create_ontology=True
        )
        
        print("🚀 Initializing LINAC Extractor...")
        extractor = LinacExtractor(config, api_key)
        
        # Process the manual in chunks for demo (full content might be expensive)
        print("📝 Processing manual content with LangExtract...")
        
        # Use first 5000 characters for demo
        demo_content = manual_content[:5000]
        print(f"🔍 Processing first {len(demo_content)} characters for demo...")
        
        # Extract entities
        start_time = datetime.now()
        
        results = await extractor.extract_from_service_manual(
            demo_content,
            "TrueBeam_STx_Manual_Demo",
            save_results=True
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"⏱️  Processing completed in {processing_time:.2f} seconds")
        
        # Display results
        await display_extraction_results(results, demo_content, extractor)
        
        # Create comprehensive visualization
        await create_demo_visualization(results, demo_content)
        
        print("✅ Real LINAC manual test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_local_processing(manual_content: str):
    """Test local processing without API calls"""
    
    print("\n🔧 TESTING LOCAL PROCESSING (NO API)")
    print("-" * 50)
    
    try:
        # Test medical schema builder
        from langextract_integration.medical_schema_builder import MedicalSchemaBuilder
        
        builder = MedicalSchemaBuilder()
        
        # Get all examples
        examples = builder.get_all_examples()
        validation = builder.validate_examples()
        
        print(f"✅ Medical Schema Builder: {len(examples)} examples created")
        print(f"   📊 Entity types: {validation['entity_types']}")
        print(f"   📝 Avg text length: {validation['statistics']['avg_text_length']:.0f} chars")
        
        # Test grounding visualizer with mock data
        visualizer = GroundingVisualizer()
        
        mock_results = create_mock_extraction_results()
        sample_text = manual_content[:1000]
        
        viz_file = visualizer.create_grounded_visualization(
            mock_results,
            sample_text,
            "local_test_visualization.html",
            "Local Processing Demo"
        )
        
        print(f"✅ Grounding Visualizer: Created {viz_file}")
        
        # Analyze manual content structure
        analyze_manual_structure(manual_content)
        
    except Exception as e:
        print(f"❌ Local processing failed: {str(e)}")


def create_mock_extraction_results():
    """Create mock extraction results for local testing"""
    
    return {
        "consolidated_entities": {
            "error_codes": [
                {
                    "code": "7002",
                    "text": "7002",
                    "confidence": 0.95,
                    "attributes": {
                        "message": "LEAF MOVEMENT ERROR",
                        "description": "Leaf direction mismatch or stationary leaf moved",
                        "category": "Mechanical",
                        "severity": "High"
                    },
                    "source_location": {
                        "start_char": 450,
                        "end_char": 454,
                        "context": "Error Code: 7002"
                    }
                },
                {
                    "code": "7003",
                    "text": "7003", 
                    "confidence": 0.92,
                    "attributes": {
                        "message": "LEAF POSITION TIMEOUT",
                        "description": "Leaf not reached commanded position in time",
                        "category": "Mechanical",
                        "severity": "Medium"
                    },
                    "source_location": {
                        "start_char": 680,
                        "end_char": 684,
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
                        "function": "Controls MLC leaf positioning",
                        "parent_system": "Multi-Leaf Collimator"
                    },
                    "source_location": {
                        "start_char": 280,
                        "end_char": 299,
                        "context": "- MLC Controller Unit (Part Number: MLC-CTRL-2000)"
                    }
                },
                {
                    "name": "Leaf Drive Motors",
                    "text": "Leaf Drive Motors",
                    "confidence": 0.90,
                    "attributes": {
                        "part_number": "LDM-001-V3",
                        "type": "actuator",
                        "function": "Drive individual leaf movement",
                        "quantity": "120 units"
                    },
                    "source_location": {
                        "start_char": 320,
                        "end_char": 337,
                        "context": "- Leaf Drive Motors (Part Number: LDM-001-V3) - 120 units"
                    }
                }
            ],
            "safety_protocols": [
                {
                    "name": "MLC INTERLOCK FAILURE",
                    "text": "MLC INTERLOCK FAILURE",
                    "confidence": 0.85,
                    "attributes": {
                        "type": "CRITICAL",
                        "description": "Safety interlock system detected unsafe condition",
                        "response_steps": [
                            "Check all safety interlocks",
                            "Verify door positions",
                            "Reset after clearing condition"
                        ]
                    },
                    "source_location": {
                        "start_char": 900,
                        "end_char": 921,
                        "context": "Message: MLC INTERLOCK FAILURE"
                    }
                }
            ]
        },
        "extraction_metadata": {
            "model": "local_processing",
            "extraction_passes": 1,
            "method": "mock_data",
            "timestamp": datetime.now().isoformat()
        }
    }


def analyze_manual_structure(content: str):
    """Analyze the structure of the LINAC manual"""
    
    print(f"\n📋 MANUAL STRUCTURE ANALYSIS")
    print("-" * 30)
    
    lines = content.split('\n')
    
    # Count different types of content
    error_codes = []
    components = []
    procedures = []
    
    for line in lines:
        line = line.strip()
        
        if line.startswith("Error Code:"):
            error_codes.append(line)
        elif "Part Number:" in line:
            components.append(line)
        elif line.startswith(("1.", "2.", "3.", "4.", "5.")) and len(line) > 10:
            procedures.append(line)
    
    print(f"🔴 Error codes found: {len(error_codes)}")
    for code in error_codes[:3]:
        print(f"   • {code}")
    
    print(f"🔧 Components found: {len(components)}")
    for comp in components[:3]:
        print(f"   • {comp}")
    
    print(f"📝 Procedure steps found: {len(procedures)}")
    for proc in procedures[:3]:
        print(f"   • {proc}")
    
    print(f"📊 Total content: {len(content):,} characters, {len(lines)} lines")


async def display_extraction_results(results: dict, content: str, extractor):
    """Display comprehensive extraction results"""
    
    print(f"\n🎯 EXTRACTION RESULTS")
    print("-" * 40)
    
    # Get statistics
    stats = extractor.get_extraction_statistics(results)
    
    print(f"📖 Manual: {stats.get('manual_title', 'Unknown')}")
    print(f"🔄 Extraction stages: {stats.get('extraction_stages', 0)}")
    print(f"📊 Total entities: {stats.get('total_entities', 0)}")
    
    # Entity breakdown
    entity_counts = stats.get('entity_counts', {})
    for entity_type, count in entity_counts.items():
        if count > 0:
            type_name = entity_type.replace('_', ' ').title()
            print(f"   • {type_name}: {count}")
    
    # Confidence distribution
    confidence_dist = stats.get('confidence_distribution', {})
    if confidence_dist:
        print(f"🎯 Confidence distribution:")
        print(f"   • High (≥0.8): {confidence_dist.get('high', 0)}")
        print(f"   • Medium (0.6-0.8): {confidence_dist.get('medium', 0)}")
        print(f"   • Low (<0.6): {confidence_dist.get('low', 0)}")
    
    # Sample entities
    consolidated = results.get('consolidated_entities', {})
    
    print(f"\n🔍 SAMPLE EXTRACTED ENTITIES")
    print("-" * 30)
    
    # Show error codes
    error_codes = consolidated.get('error_codes', [])
    if error_codes:
        print(f"🔴 Error Codes ({len(error_codes)}):")
        for i, error in enumerate(error_codes[:2]):  # Show first 2
            attrs = error.get('attributes', {})
            print(f"   {i+1}. Code {error.get('code', 'N/A')}: {attrs.get('message', 'N/A')}")
            print(f"      Description: {attrs.get('description', 'N/A')[:80]}...")
            print(f"      Confidence: {error.get('confidence', 0):.2f}")
    
    # Show components
    components = consolidated.get('components', [])
    if components:
        print(f"\n🔧 Components ({len(components)}):")
        for i, comp in enumerate(components[:2]):  # Show first 2
            attrs = comp.get('attributes', {})
            print(f"   {i+1}. {comp.get('name', 'N/A')}")
            print(f"      Type: {attrs.get('type', 'N/A')}, Part#: {attrs.get('part_number', 'N/A')}")
            print(f"      Function: {attrs.get('function', 'N/A')[:60]}...")
            print(f"      Confidence: {comp.get('confidence', 0):.2f}")
    
    # Show processing info
    if 'ontology' in results:
        ontology_info = results['ontology']
        print(f"\n🏗️  Ontology created: {ontology_info.get('entities_added', 0)} entities")
        validation = ontology_info.get('validation', {})
        if validation.get('is_valid'):
            print("   ✅ Ontology validation passed")
        else:
            print("   ⚠️  Ontology validation warnings")


async def create_demo_visualization(results: dict, content: str):
    """Create demonstration visualization"""
    
    print(f"\n🎨 CREATING INTERACTIVE VISUALIZATION")
    print("-" * 40)
    
    try:
        visualizer = GroundingVisualizer()
        
        viz_file = visualizer.create_grounded_visualization(
            results,
            content,
            "real_linac_manual_visualization.html",
            "Real LINAC Manual - LangExtract Demo"
        )
        
        viz_path = Path(viz_file)
        if viz_path.exists():
            file_size = viz_path.stat().st_size
            print(f"✅ Interactive visualization created:")
            print(f"   📄 File: {viz_file}")
            print(f"   📊 Size: {file_size:,} bytes")
            print(f"   🌐 Open in browser to view entity highlighting")
        else:
            print("❌ Visualization file not created")
    
    except Exception as e:
        print(f"❌ Visualization creation failed: {str(e)}")


async def main():
    """Main test function"""
    
    # Set up environment
    os.environ.setdefault('LANGEXTRACT_API_KEY', os.getenv('GOOGLE_API_KEY', ''))
    
    await test_with_real_linac_manual()
    
    print("\n" + "="*80)
    print("🎉 REAL LINAC MANUAL TEST COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. 🌐 Open the visualization HTML files in your browser")
    print("2. 📊 Review extracted entities and confidence scores")
    print("3. 🔍 Check source grounding accuracy")
    print("4. 🏗️  Examine generated ontology structure")


if __name__ == "__main__":
    asyncio.run(main())