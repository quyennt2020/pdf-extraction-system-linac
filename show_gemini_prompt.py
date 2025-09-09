"""
Show the Gemini prompt being used for entity extraction
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.ai_extraction.prompt_templates import MedicalDevicePrompts

def show_prompt():
    """Display the Gemini extraction prompt"""
    
    # Sample content
    sample_content = """
    MLCi and MLCi2 control subsystem
    System description
    4513 370 2102 03
    Elekta Digital Linear Accelerator
    
    Error Code 7002: MOVEMENT - The actual direction of movement of a leaf does not match 
    the expected direction. Check the drive to the leaf motors.
    """
    
    # Create prompt builder
    prompt_builder = MedicalDevicePrompts()
    
    print("🔍 Current Gemini Extraction Prompt")
    print("=" * 60)
    
    # Show regular prompt
    print("\n📝 REGULAR EXTRACTION PROMPT:")
    print("-" * 40)
    regular_prompt = prompt_builder.build_extraction_prompt(
        page_content=sample_content,
        device_type="linear_accelerator",
        manual_type="service_manual",
        extraction_focus=["error_codes", "components", "procedures", "safety_protocols"]
    )
    print(regular_prompt)
    
    print("\n" + "=" * 60)
    
    # Show hierarchical prompt
    print("\n📝 HIERARCHICAL EXTRACTION PROMPT:")
    print("-" * 40)
    hierarchical_prompt = prompt_builder.build_hierarchical_extraction_prompt(
        page_content=sample_content,
        device_type="linear_accelerator"
    )
    print(hierarchical_prompt)

if __name__ == "__main__":
    show_prompt()