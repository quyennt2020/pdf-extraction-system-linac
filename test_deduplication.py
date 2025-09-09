"""
Test entity deduplication functionality
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from run_with_real_pdf import RealPDFProcessor

async def test_deduplication():
    """Test the deduplication functionality"""
    
    print("🧪 Testing Entity Deduplication")
    print("=" * 50)
    
    try:
        # Initialize processor
        processor = RealPDFProcessor()
        
        # Process PDF with deduplication
        print("🔄 Processing PDF with deduplication enabled...")
        result = await processor.process_service_manual(
            pdf_path="data/input_pdfs/test.pdf",
            device_type="linear_accelerator",
            max_pages=5,  # Test with 5 pages
            output_dir="data/dedup_test_results"
        )
        
        if 'error' not in result:
            print("✅ Processing completed successfully!")
            
            # Show deduplication statistics
            stats = result.get('processing_stats', {})
            
            print(f"\n📊 Deduplication Results:")
            print(f"   - Total entities extracted: {stats.get('total_entities', 0)}")
            print(f"   - After deduplication: {stats.get('deduplicated_entities', 0)}")
            print(f"   - Duplicates removed: {stats.get('duplicates_removed', 0)}")
            
            if stats.get('duplicates_removed', 0) > 0:
                reduction_percent = (stats.get('duplicates_removed', 0) / stats.get('total_entities', 1)) * 100
                print(f"   - Reduction: {reduction_percent:.1f}%")
            
            # Show entity breakdown
            if 'entity_summary' in result:
                print(f"\n📈 Final entity breakdown:")
                for entity_type, count in result['entity_summary'].items():
                    print(f"   - {entity_type}: {count}")
        else:
            print(f"❌ Processing failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_deduplication())