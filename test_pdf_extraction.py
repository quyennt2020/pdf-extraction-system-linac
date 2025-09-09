"""
Test PDF extraction with improved prompts
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from run_with_real_pdf import RealPDFProcessor

async def test_pdf_extraction():
    """Test PDF extraction with improved settings"""
    
    print("🧪 Testing PDF Extraction with Improved Prompts")
    print("=" * 60)
    
    try:
        # Initialize processor
        processor = RealPDFProcessor()
        
        # Process a few pages with improved settings
        result = await processor.process_service_manual(
            pdf_path="data/input_pdfs/test.pdf",
            device_type="linear_accelerator",
            max_pages=3,  # Just test 3 pages
            output_dir="data/test_results"
        )
        
        if 'error' not in result:
            print("✅ Processing completed successfully!")
            print(f"📊 Results: {result.get('entities_extracted', 0)} entities from {result.get('pages_processed', 0)} pages")
            
            # Show entity breakdown
            if 'entity_summary' in result:
                print("\n📈 Entity breakdown:")
                for entity_type, count in result['entity_summary'].items():
                    print(f"   - {entity_type}: {count}")
        else:
            print(f"❌ Processing failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_pdf_extraction())