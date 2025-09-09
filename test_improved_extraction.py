"""
Test improved entity extraction with hierarchical mode
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.ai_extraction.gemini_client import GeminiClient

async def test_extraction():
    """Test improved extraction with sample content"""
    
    # Sample content from the PDF
    sample_content = """
    MLCi and MLCi2 control subsystem
    System description
    4513 370 2102 03
    Elekta Digital Linear Accelerator
    Corrective Maintenance Manual – MLCi and MLCi2
    
    The control system is shown schematically in Figure 3.1 for an MLCi fitted with the RTU 
    assembly and in Figure 3.2 for MLCi/MLCi2 fitted with the BLD electronic assembly.
    
    The MLC system consists of:
    - Leaf motor assemblies (120 individual motors)
    - Position feedback sensors
    - MLC controller board
    - Power supply unit
    - Safety interlock system
    
    Error Code 7002: MOVEMENT - The actual direction of movement of a leaf does not match 
    the expected direction. Check the drive to the leaf motors and the leaves for free movement.
    
    Calibration Procedure:
    1. Check calibration files are present
    2. Verify video line calibration  
    3. Confirm correct spacing
    """
    
    try:
        # Initialize Gemini client
        gemini_client = GeminiClient()
        
        print("🧪 Testing improved entity extraction...")
        print("=" * 50)
        
        # Test with hierarchical mode
        print("\n🔄 Testing hierarchical extraction...")
        result = await gemini_client.extract_medical_entities(
            page_content=sample_content,
            device_type="linear_accelerator",
            manual_type="service_manual",
            extraction_focus=["systems", "subsystems", "components", "spare_parts", "error_codes", "procedures"],
            hierarchical_mode=True
        )
        
        print("\n📊 Extraction Results:")
        for entity_type, entities in result.items():
            if entity_type != "extraction_metadata" and entities:
                print(f"\n{entity_type.upper()}:")
                for i, entity in enumerate(entities[:3]):  # Show first 3
                    print(f"  {i+1}. {entity}")
                if len(entities) > 3:
                    print(f"  ... and {len(entities) - 3} more")
        
        # Count entities by type
        print(f"\n📈 Entity Counts:")
        for entity_type, entities in result.items():
            if entity_type != "extraction_metadata":
                count = len(entities) if isinstance(entities, list) else 0
                print(f"  - {entity_type}: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_extraction())