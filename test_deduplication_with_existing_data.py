"""
Test deduplication with existing PDF results
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def analyze_duplicates():
    """Analyze duplicates in existing PDF results"""
    
    print("🔍 Analyzing Duplicates in Existing PDF Results")
    print("=" * 60)
    
    try:
        # Load the latest results
        results_dir = Path("data/real_pdf_results")
        entities_files = list(results_dir.glob("*_entities_*.json"))
        
        if not entities_files:
            print("❌ No PDF results found")
            return
        
        # Get the most recent file
        latest_file = max(entities_files, key=lambda f: f.stat().st_mtime)
        print(f"📄 Analyzing: {latest_file.name}")
        
        # Load entities
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entities = data.get('entities', [])
        print(f"📊 Total entities: {len(entities)}")
        
        # Group by content to find duplicates
        content_groups = defaultdict(list)
        
        for entity in entities:
            # Generate content key
            if 'code' in entity and entity.get('code'):
                key = f"error_code:{entity['code']}:{entity.get('message', '')}"
            elif 'name' in entity:
                key = f"component:{entity['name']}:{entity.get('component_type', '')}"
            else:
                desc = entity.get('description', '')[:50]
                key = f"other:{desc}"
            
            content_groups[key.lower()].append(entity)
        
        # Analyze duplicates
        duplicates_found = 0
        total_duplicates = 0
        
        print(f"\n🔍 Duplicate Analysis:")
        
        for content_key, group in content_groups.items():
            if len(group) > 1:
                duplicates_found += 1
                total_duplicates += len(group) - 1
                
                print(f"\n   🔄 {content_key}:")
                print(f"      Found {len(group)} instances:")
                
                for i, entity in enumerate(group, 1):
                    page = entity.get('source_page', 'unknown')
                    conf = entity.get('confidence', 0)
                    desc_preview = entity.get('description', '')[:30] + "..." if len(entity.get('description', '')) > 30 else entity.get('description', '')
                    print(f"         {i}. Page {page}, Confidence: {conf:.2f}, Desc: {desc_preview}")
        
        print(f"\n📊 Summary:")
        print(f"   - Unique content groups: {len(content_groups)}")
        print(f"   - Groups with duplicates: {duplicates_found}")
        print(f"   - Total duplicate instances: {total_duplicates}")
        print(f"   - Potential reduction: {total_duplicates} entities ({(total_duplicates/len(entities)*100):.1f}%)")
        
        # Show most common duplicates
        if duplicates_found > 0:
            print(f"\n🔝 Most Duplicated Entities:")
            sorted_groups = sorted(content_groups.items(), key=lambda x: len(x[1]), reverse=True)
            
            for content_key, group in sorted_groups[:5]:
                if len(group) > 1:
                    print(f"   - {content_key}: {len(group)} instances")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_duplicates()