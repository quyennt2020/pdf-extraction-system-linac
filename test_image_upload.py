#!/usr/bin/env python3
"""
Test Image Upload Functionality
Tests the image upload endpoints and functionality
"""

import requests
import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

API_BASE = "http://localhost:3000/api/expert-review"

def test_image_upload():
    """Test image upload functionality"""
    
    print("🖼️  Testing Image Upload Functionality")
    print("=" * 50)
    
    # First, load some entities to test with
    print("1. Loading PDF results...")
    try:
        response = requests.post(f"{API_BASE}/load-pdf-results")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Loaded {result.get('entities_loaded', 0)} entities")
        else:
            print(f"   ❌ Failed to load PDF results: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error loading PDF results: {e}")
        return
    
    # Get list of entities
    print("2. Getting entity list...")
    try:
        response = requests.get(f"{API_BASE}/entities")
        if response.status_code == 200:
            entities_data = response.json()
            entities = entities_data.get('entities', [])
            if not entities:
                print("   ❌ No entities found")
                return
            
            test_entity = entities[0]
            entity_id = test_entity['id']
            print(f"   ✅ Found {len(entities)} entities, testing with: {test_entity['label']}")
        else:
            print(f"   ❌ Failed to get entities: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error getting entities: {e}")
        return
    
    # Create a test image file
    print("3. Creating test image...")
    test_image_path = Path("test_entity_image.png")
    try:
        # Create a simple 100x100 PNG image
        from PIL import Image, ImageDraw
        
        # Create a simple test image
        img = Image.new('RGB', (100, 100), color='lightblue')
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 90, 90], fill='darkblue', outline='navy', width=2)
        draw.text((30, 45), "TEST", fill='white')
        
        img.save(test_image_path, 'PNG')
        print(f"   ✅ Created test image: {test_image_path}")
        
    except ImportError:
        print("   ⚠️  PIL not available, creating dummy file")
        # Create a dummy file for testing
        with open(test_image_path, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00d\x00\x00\x00d\x08\x02\x00\x00\x00\xff\x80\x02\x03')
    except Exception as e:
        print(f"   ❌ Error creating test image: {e}")
        return
    
    # Test image upload
    print("4. Testing image upload...")
    try:
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test_image.png', f, 'image/png')}
            response = requests.post(f"{API_BASE}/entities/{entity_id}/upload-image", files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                image_url = result.get('image_url')
                print(f"   ✅ Image uploaded successfully: {image_url}")
            else:
                print(f"   ❌ Upload failed: {result.get('message')}")
                return
        else:
            print(f"   ❌ Upload request failed: {response.status_code}")
            print(f"       Response: {response.text}")
            return
    except Exception as e:
        print(f"   ❌ Error uploading image: {e}")
        return
    
    # Test getting image info
    print("5. Testing image retrieval...")
    try:
        response = requests.get(f"{API_BASE}/entities/{entity_id}/image")
        if response.status_code == 200:
            result = response.json()
            if result.get('has_image'):
                print(f"   ✅ Image info retrieved: {result.get('image_url')}")
            else:
                print("   ❌ Entity shows no image")
                return
        else:
            print(f"   ❌ Failed to get image info: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error getting image info: {e}")
        return
    
    # Test entity list shows image
    print("6. Verifying entity list shows image...")
    try:
        response = requests.get(f"{API_BASE}/entities")
        if response.status_code == 200:
            entities_data = response.json()
            entities = entities_data.get('entities', [])
            
            # Find our test entity
            test_entity_updated = None
            for entity in entities:
                if entity['id'] == entity_id:
                    test_entity_updated = entity
                    break
            
            if test_entity_updated and test_entity_updated.get('image_url'):
                print(f"   ✅ Entity list shows image: {test_entity_updated['image_url']}")
            else:
                print("   ❌ Entity list doesn't show image")
                return
        else:
            print(f"   ❌ Failed to get updated entity list: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error verifying entity list: {e}")
        return
    
    # Test image deletion
    print("7. Testing image deletion...")
    try:
        response = requests.delete(f"{API_BASE}/entities/{entity_id}/image")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Image deleted successfully")
            else:
                print(f"   ❌ Delete failed: {result.get('message')}")
                return
        else:
            print(f"   ❌ Delete request failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error deleting image: {e}")
        return
    
    # Verify deletion
    print("8. Verifying image deletion...")
    try:
        response = requests.get(f"{API_BASE}/entities/{entity_id}/image")
        if response.status_code == 200:
            result = response.json()
            if not result.get('has_image'):
                print("   ✅ Image successfully removed")
            else:
                print("   ❌ Image still exists after deletion")
                return
        else:
            print(f"   ❌ Failed to verify deletion: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error verifying deletion: {e}")
        return
    
    # Cleanup
    if test_image_path.exists():
        test_image_path.unlink()
        print("   🧹 Cleaned up test image file")
    
    print("\n🎉 All image upload tests passed!")
    print("\n📋 Image Upload Features Available:")
    print("   • Upload images for entities (JPEG, PNG, GIF, WebP)")
    print("   • View images in entity list and edit modal")
    print("   • Delete entity images")
    print("   • Automatic file management and cleanup")
    print("   • Image thumbnails in entity table")

def main():
    """Main test function"""
    try:
        test_image_upload()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()