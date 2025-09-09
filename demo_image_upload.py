#!/usr/bin/env python3
"""
Demo Image Upload Functionality
Shows how to use the image upload feature
"""

import requests
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

API_BASE = "http://localhost:3000/api/expert-review"

def create_demo_image(entity_label, filename):
    """Create a demo image for an entity"""
    # Create a 200x150 image
    img = Image.new('RGB', (200, 150), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([5, 5, 195, 145], outline='darkblue', width=3)
    
    # Add entity label
    try:
        # Try to use a nice font
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Calculate text position (centered)
    text_bbox = draw.textbbox((0, 0), entity_label, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (200 - text_width) // 2
    y = (150 - text_height) // 2
    
    # Draw text with shadow
    draw.text((x+1, y+1), entity_label, fill='black', font=font)
    draw.text((x, y), entity_label, fill='white', font=font)
    
    # Add some decorative elements
    draw.ellipse([10, 10, 30, 30], fill='yellow', outline='orange', width=2)
    draw.ellipse([170, 10, 190, 30], fill='green', outline='darkgreen', width=2)
    draw.ellipse([10, 120, 30, 140], fill='red', outline='darkred', width=2)
    draw.ellipse([170, 120, 190, 140], fill='purple', outline='indigo', width=2)
    
    img.save(filename, 'PNG')
    return filename

def demo_image_upload():
    """Demonstrate image upload functionality"""
    
    print("🖼️  Image Upload Demo")
    print("=" * 40)
    
    # Load entities
    print("1. Loading entities...")
    try:
        response = requests.post(f"{API_BASE}/load-pdf-results")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Loaded {result.get('entities_loaded', 0)} entities")
        else:
            print(f"   ❌ Failed to load entities")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Get entities
    print("2. Getting entity list...")
    try:
        response = requests.get(f"{API_BASE}/entities")
        if response.status_code == 200:
            entities_data = response.json()
            entities = entities_data.get('entities', [])
            if not entities:
                print("   ❌ No entities found")
                return
            
            print(f"   ✅ Found {len(entities)} entities")
        else:
            print(f"   ❌ Failed to get entities")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Upload images for all entities
    uploaded_images = []
    
    for i, entity in enumerate(entities):
        entity_id = entity['id']
        entity_label = entity['label']
        
        print(f"3.{i+1} Creating and uploading image for: {entity_label}")
        
        # Create demo image
        image_filename = f"demo_image_{i+1}.png"
        try:
            create_demo_image(entity_label, image_filename)
            print(f"     ✅ Created image: {image_filename}")
        except Exception as e:
            print(f"     ❌ Error creating image: {e}")
            continue
        
        # Upload image
        try:
            with open(image_filename, 'rb') as f:
                files = {'file': (image_filename, f, 'image/png')}
                response = requests.post(f"{API_BASE}/entities/{entity_id}/upload-image", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    image_url = result.get('image_url')
                    print(f"     ✅ Uploaded: {image_url}")
                    uploaded_images.append((entity_id, entity_label, image_url))
                else:
                    print(f"     ❌ Upload failed: {result.get('message')}")
            else:
                print(f"     ❌ Upload request failed: {response.status_code}")
                
        except Exception as e:
            print(f"     ❌ Error uploading: {e}")
        
        # Clean up local file
        try:
            Path(image_filename).unlink()
        except:
            pass
    
    # Show results
    print(f"\n4. Upload Summary:")
    print(f"   📊 Total entities: {len(entities)}")
    print(f"   🖼️  Images uploaded: {len(uploaded_images)}")
    
    if uploaded_images:
        print(f"\n5. Uploaded Images:")
        for entity_id, label, image_url in uploaded_images:
            print(f"   • {label}: {image_url}")
        
        print(f"\n🌐 View in Dashboard:")
        print(f"   Open: http://localhost:9000")
        print(f"   Navigate to 'Entities' tab to see images")
        print(f"   Click thumbnails to view full-size images")
        print(f"   Use 'Edit' button to manage images")

def main():
    """Main demo function"""
    try:
        demo_image_upload()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    main()