#!/usr/bin/env python3
"""
Verify that the import UI is working properly
"""

import requests
import json

def test_ui_functionality():
    """Test if the import UI is accessible"""
    print("🔍 Verifying Import UI Functionality")
    print("=" * 40)
    
    # Test 1: Check if dashboard loads
    try:
        response = requests.get("http://localhost:9000", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard page loads successfully")
            
            # Check if import modal HTML is present
            if 'importDataModal' in response.text:
                print("✅ Import modal HTML is present")
            else:
                print("❌ Import modal HTML not found")
                return False
                
            # Check if import button is present
            if 'showImportModal()' in response.text:
                print("✅ Import button with showImportModal() found")
            else:
                print("❌ Import button not found")
                return False
                
        else:
            print(f"❌ Dashboard page failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading dashboard: {e}")
        return False
    
    # Test 2: Check if JavaScript file loads
    try:
        response = requests.get("http://localhost:9000/static/js/dashboard.js", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard JavaScript loads successfully")
            
            # Check if import functions are present
            js_content = response.text
            if 'function showImportModal()' in js_content:
                print("✅ showImportModal function found in JavaScript")
            else:
                print("❌ showImportModal function not found in JavaScript")
                return False
                
            if 'function handleFileSelect(' in js_content:
                print("✅ handleFileSelect function found in JavaScript")
            else:
                print("❌ handleFileSelect function not found in JavaScript")
                return False
                
            if 'function performImport(' in js_content:
                print("✅ performImport function found in JavaScript")
            else:
                print("❌ performImport function not found in JavaScript")
                return False
                
        else:
            print(f"❌ JavaScript file failed to load: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading JavaScript: {e}")
        return False
    
    # Test 3: Check current dashboard data
    try:
        response = requests.get("http://localhost:9000/api/expert-review/dashboard/overview", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard API working - {data.get('total_entities', 0)} entities loaded")
        else:
            print(f"❌ Dashboard API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking dashboard API: {e}")
        return False
    
    return True

def main():
    """Main verification function"""
    
    if test_ui_functionality():
        print(f"\n🎉 Import UI is ready for testing!")
        print(f"\n📋 Manual Test Steps:")
        print(f"   1. Open http://localhost:9000 in your browser")
        print(f"   2. Clear browser cache (Ctrl+F5)")
        print(f"   3. Click 'Import Data' button")
        print(f"   4. Upload 'sample_import_for_ui_test.json'")
        print(f"   5. Test validation and import")
        
        print(f"\n📁 Test Files Available:")
        print(f"   - sample_import_for_ui_test.json (10 entities)")
        print(f"   - sample_import_data.json (5 entities)")
        print(f"   - data/sample_extraction_results/sample_entities.json (21 entities)")
        
        print(f"\n🔧 If Import Button Doesn't Work:")
        print(f"   1. Open browser Developer Tools (F12)")
        print(f"   2. Check Console for JavaScript errors")
        print(f"   3. Try: typeof showImportModal (should return 'function')")
        print(f"   4. Try: showImportModal() (should open modal)")
        
    else:
        print(f"\n❌ Import UI verification failed")
        print(f"   Please check the dashboard and JavaScript files")

if __name__ == "__main__":
    main()