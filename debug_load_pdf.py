#!/usr/bin/env python3
"""
Debug Load PDF Results
"""

import json
import glob
from pathlib import Path

def debug_load_pdf():
    """Debug the PDF loading process"""
    
    print("🔍 Debugging PDF Load Process")
    print("=" * 40)
    
    # Check if results directory exists
    results_dir = Path("data/real_pdf_results")
    print(f"1. Results directory exists: {results_dir.exists()}")
    
    if not results_dir.exists():
        print("   ❌ Results directory not found!")
        return
    
    # Find entities files
    entities_files = glob.glob(str(results_dir / "*_entities_*.json"))
    print(f"2. Entities files found: {len(entities_files)}")
    
    if not entities_files:
        print("   ❌ No entities files found!")
        return
    
    # Get the most recent file
    import os
    latest_entities_file = max(entities_files, key=os.path.getctime)
    print(f"3. Latest entities file: {Path(latest_entities_file).name}")
    
    # Try to load the file
    try:
        with open(latest_entities_file, 'r', encoding='utf-8') as f:
            entities_data = json.load(f)
        
        print("4. File loaded successfully!")
        
        # Check structure
        entities = entities_data.get('entities', [])
        print(f"5. Entities in file: {len(entities)}")
        
        if entities:
            print("6. Sample entity:")
            sample = entities[0]
            print(f"   ID: {sample.get('id')}")
            print(f"   Label: {sample.get('label', sample.get('name', 'No label'))}")
            print(f"   Type: {sample.get('type', 'No type')}")
            print(f"   Description: {sample.get('description', 'No description')[:50]}...")
        
        # Test the loading logic
        print("\n7. Testing loading logic...")
        
        loaded_entity_ids = set()
        loaded_entity_content = set()
        processed_count = 0
        
        for entity_data in entities:
            try:
                # Skip if we've already loaded this entity
                entity_id = entity_data.get('id')
                if entity_id in loaded_entity_ids:
                    continue
                
                # Generate content key for deduplication
                content_key = _generate_content_key(entity_data)
                if content_key in loaded_entity_content:
                    continue
                
                loaded_entity_ids.add(entity_id)
                loaded_entity_content.add(content_key)
                processed_count += 1
                
            except Exception as e:
                print(f"   Error processing entity: {e}")
        
        print(f"   Entities that would be loaded: {processed_count}")
        
    except Exception as e:
        print(f"   ❌ Error loading file: {e}")

def _generate_content_key(entity_data: dict) -> str:
    """Generate a content-based key for deduplication"""
    
    # For error codes, use code + message
    if 'code' in entity_data and entity_data.get('code'):
        code = entity_data.get('code', '').strip()
        message = entity_data.get('message', '').strip()
        return f"error_code:{code}:{message}".lower()
    
    # For components, use name + type
    elif 'name' in entity_data:
        name = entity_data.get('name', '').strip()
        comp_type = entity_data.get('component_type', '').strip()
        return f"component:{name}:{comp_type}".lower()
    
    # For other entities, use description
    else:
        description = entity_data.get('description', '')[:100].strip()
        return f"other:{description}".lower()

def main():
    debug_load_pdf()

if __name__ == "__main__":
    main()