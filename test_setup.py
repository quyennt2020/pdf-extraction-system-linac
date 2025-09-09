"""
Test Setup Script
Verifies that all components are properly installed and configured
"""

import sys
import os
from pathlib import Path
import asyncio

def test_imports():
    """Test that all required modules can be imported"""
    
    print("🔍 Testing imports...")
    
    try:
        # Core dependencies
        import fastapi
        import uvicorn
        import jinja2
        print("   ✅ Web framework dependencies")
        
        # AI dependencies
        import google.generativeai as genai
        print("   ✅ Google Generative AI")
        
        # PDF processing
        import PyPDF2
        print("   ✅ PDF processing libraries")
        
        # Data processing
        import pandas as pd
        import numpy as np
        print("   ✅ Data processing libraries")
        
        # Logging
        from loguru import logger
        print("   ✅ Logging utilities")
        
        # Project modules
        sys.path.append(str(Path(__file__).parent))
        
        from backend.ai_extraction.gemini_client import GeminiClient
        from backend.ai_extraction.entity_parser import MedicalEntityParser
        from backend.core.pdf_processor import MedicalDevicePDFProcessor
        from backend.models.entity import Entity, EntityType
        from backend.models.ontology_models import MechatronicSystem
        print("   ✅ Project modules")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_directories():
    """Test that required directories exist or can be created"""
    
    print("\n📁 Testing directories...")
    
    required_dirs = [
        "data/input_pdfs",
        "data/real_pdf_results", 
        "logs",
        "backend/ai_extraction",
        "backend/models",
        "frontend/templates",
        "frontend/static"
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            if os.path.exists(dir_path):
                print(f"   ✅ {dir_path}")
            else:
                print(f"   ❌ Failed to create {dir_path}")
                all_good = False
        except Exception as e:
            print(f"   ❌ Error with {dir_path}: {e}")
            all_good = False
    
    return all_good

def test_api_key():
    """Test API key configuration"""
    
    print("\n🔑 Testing API key...")
    
    # Try to load from config first, then environment
    try:
        from config import config
        api_key = config.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
    except:
        api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        if len(api_key) > 20:  # Basic validation
            print("   ✅ Gemini API key found and appears valid")
            return True
        else:
            print("   ⚠️ Gemini API key found but seems too short")
            return False
    else:
        print("   ⚠️ Gemini API key not found in environment")
        print("   💡 Set GEMINI_API_KEY environment variable")
        print("   💡 Get your key from: https://makersuite.google.com/app/apikey")
        return False

async def test_gemini_connection():
    """Test connection to Gemini API"""
    
    print("\n🤖 Testing Gemini API connection...")
    
    # Try to load from config first, then environment
    try:
        from config import config
        api_key = config.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
    except:
        api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("   ⚠️ Skipping - no API key configured")
        return False
    
    try:
        from backend.ai_extraction.gemini_client import GeminiClient
        
        client = GeminiClient(api_key=api_key)
        
        # Test with simple text
        test_text = "Error Code 7002: MLC leaf motor failure. Check motor connections."
        
        result = await client.extract_medical_entities(
            page_content=test_text,
            device_type="linear_accelerator",
            manual_type="service_manual"
        )
        
        if result:
            print("   ✅ Gemini API connection successful")
            print(f"   📊 Test extraction returned: {type(result)}")
            return True
        else:
            print("   ❌ Gemini API returned empty result")
            return False
            
    except Exception as e:
        print(f"   ❌ Gemini API connection failed: {e}")
        return False

def test_pdf_processing():
    """Test PDF processing capabilities"""
    
    print("\n📄 Testing PDF processing...")
    
    try:
        from backend.core.pdf_processor import MedicalDevicePDFProcessor
        
        processor = MedicalDevicePDFProcessor()
        print("   ✅ PDF processor initialized")
        
        # Check if we have a test PDF
        test_pdfs = [
            "data/input_pdfs/test.pdf",
            "data/medical_manuals/test.pdf",
            "test.pdf"
        ]
        
        test_pdf = None
        for pdf_path in test_pdfs:
            if os.path.exists(pdf_path):
                test_pdf = pdf_path
                break
        
        if test_pdf:
            print(f"   📄 Found test PDF: {test_pdf}")
            try:
                doc = processor.process_pdf(test_pdf)
                print(f"   ✅ PDF processed successfully: {doc.total_pages} pages")
                return True
            except Exception as e:
                print(f"   ❌ PDF processing failed: {e}")
                return False
        else:
            print("   ⚠️ No test PDF found - place a PDF in data/input_pdfs/ for testing")
            return True  # Not a failure, just no test file
            
    except Exception as e:
        print(f"   ❌ PDF processor error: {e}")
        return False

def test_dashboard():
    """Test dashboard components"""
    
    print("\n🖥️ Testing dashboard components...")
    
    try:
        # Test template files
        template_files = [
            "frontend/templates/dashboard.html",
            "frontend/templates/entity_forms.html",
            "frontend/templates/relationship_editor.html"
        ]
        
        for template in template_files:
            if os.path.exists(template):
                print(f"   ✅ {template}")
            else:
                print(f"   ❌ Missing: {template}")
                return False
        
        # Test static files
        static_files = [
            "frontend/static/css/dashboard.css",
            "frontend/static/js/dashboard.js",
            "frontend/static/js/entity_validation.js",
            "frontend/static/js/relationship_editor.js"
        ]
        
        for static_file in static_files:
            if os.path.exists(static_file):
                print(f"   ✅ {static_file}")
            else:
                print(f"   ❌ Missing: {static_file}")
                return False
        
        # Test API
        from backend.api.main import app
        print("   ✅ FastAPI app can be imported")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Dashboard test failed: {e}")
        return False

async def main():
    """Run all tests"""
    
    print("🧪 Testing Ontology Extraction System Setup")
    print("=" * 50)
    
    tests = [
        ("Import Dependencies", test_imports()),
        ("Directory Structure", test_directories()),
        ("API Key Configuration", test_api_key()),
        ("Gemini API Connection", await test_gemini_connection()),
        ("PDF Processing", test_pdf_processing()),
        ("Dashboard Components", test_dashboard())
    ]
    
    print(f"\n📊 Test Results:")
    print("-" * 30)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-" * 30)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 All tests passed! System is ready for use.")
        print(f"\n🚀 Next steps:")
        print(f"   1. Place your service manual PDF in data/input_pdfs/")
        print(f"   2. Run: python run_with_real_pdf.py 'data/input_pdfs/your_manual.pdf'")
        print(f"   3. Or start with dashboard: python test_expert_dashboard.py")
    else:
        print(f"\n⚠️ Some tests failed. Please fix the issues above before proceeding.")
        
        if not os.getenv('GEMINI_API_KEY'):
            print(f"\n💡 Quick fix for API key:")
            print(f"   Windows: set GEMINI_API_KEY=your_api_key_here")
            print(f"   Linux/Mac: export GEMINI_API_KEY=your_api_key_here")

if __name__ == "__main__":
    asyncio.run(main())