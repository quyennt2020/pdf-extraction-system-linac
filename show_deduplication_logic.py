"""
Show how the deduplication logic works
"""

def demonstrate_deduplication():
    """Demonstrate the deduplication logic with examples"""
    
    print("🔍 Entity Deduplication Logic")
    print("=" * 50)
    
    # Example duplicate entities
    sample_entities = [
        {
            "id": "entity_1",
            "code": "4513",
            "message": "MOVEMENT",
            "description": "Leaf movement error",
            "source_page": 3,
            "confidence": 0.8
        },
        {
            "id": "entity_2", 
            "code": "4513",
            "message": "MOVEMENT", 
            "description": "The actual direction of movement does not match expected",
            "source_page": 7,
            "confidence": 0.9
        },
        {
            "id": "entity_3",
            "code": "7002",
            "message": "CALIBRATION",
            "description": "Calibration check failed",
            "source_page": 5,
            "confidence": 0.85
        },
        {
            "id": "entity_4",
            "name": "MLC Controller",
            "component_type": "Controller",
            "description": "Multi-leaf collimator controller",
            "source_page": 4,
            "confidence": 0.92
        },
        {
            "id": "entity_5",
            "name": "MLC Controller", 
            "component_type": "Controller",
            "description": "Controls individual leaf positions",
            "source_page": 8,
            "confidence": 0.88
        }
    ]
    
    print("📋 Original Entities:")
    for i, entity in enumerate(sample_entities, 1):
        entity_type = "error_code" if "code" in entity else "component"
        key = f"{entity.get('code', entity.get('name', 'unknown'))}:{entity.get('message', entity.get('component_type', ''))}"
        print(f"   {i}. [{entity_type}] {key} (Page {entity['source_page']}, Confidence: {entity['confidence']})")
    
    print(f"\n🔄 Deduplication Process:")
    
    # Group by content key
    groups = {}
    for entity in sample_entities:
        if 'code' in entity:
            key = f"error_code:{entity['code']}:{entity['message']}".lower()
        else:
            key = f"component:{entity['name']}:{entity['component_type']}".lower()
        
        if key not in groups:
            groups[key] = []
        groups[key].append(entity)
    
    deduplicated = []
    for group_key, group_entities in groups.items():
        if len(group_entities) == 1:
            print(f"   ✅ {group_key}: No duplicates")
            deduplicated.append(group_entities[0])
        else:
            print(f"   🔄 {group_key}: Merging {len(group_entities)} duplicates")
            
            # Find best entity (highest confidence)
            best = max(group_entities, key=lambda e: e['confidence'])
            
            # Merge descriptions (take longest)
            for entity in group_entities:
                if len(entity.get('description', '')) > len(best.get('description', '')):
                    best['description'] = entity['description']
            
            # Collect source pages
            pages = [e['source_page'] for e in group_entities]
            best['source_pages'] = sorted(set(pages))
            
            print(f"      → Best confidence: {best['confidence']}")
            print(f"      → Merged description: {best['description'][:50]}...")
            print(f"      → Source pages: {best['source_pages']}")
            
            deduplicated.append(best)
    
    print(f"\n📊 Results:")
    print(f"   - Original entities: {len(sample_entities)}")
    print(f"   - After deduplication: {len(deduplicated)}")
    print(f"   - Duplicates removed: {len(sample_entities) - len(deduplicated)}")
    
    print(f"\n✅ Final Deduplicated Entities:")
    for i, entity in enumerate(deduplicated, 1):
        entity_type = "error_code" if "code" in entity else "component"
        key = f"{entity.get('code', entity.get('name', 'unknown'))}:{entity.get('message', entity.get('component_type', ''))}"
        pages = entity.get('source_pages', [entity.get('source_page')])
        print(f"   {i}. [{entity_type}] {key} (Pages: {pages}, Confidence: {entity['confidence']})")

if __name__ == "__main__":
    demonstrate_deduplication()