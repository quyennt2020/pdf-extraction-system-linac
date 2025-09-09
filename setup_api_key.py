"""
API Key Setup Helper
Helps you configure your Gemini API key in the .env file
"""

import os
from pathlib import Path

def setup_api_key():
    """Interactive setup for API key"""
    
    print("🔑 API Key Setup")
    print("=" * 30)
    
    # Check if .env file exists
    env_file = Path('.env')
    
    if env_file.exists():
        print("✅ Found .env file")
        
        # Read current content
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check if API key is already set
        if 'GEMINI_API_KEY=' in content and 'your_api_key_here' not in content:
            print("✅ API key appears to be already configured")
            
            # Ask if user wants to update
            update = input("\nDo you want to update the API key? (y/n): ").lower().strip()
            if update != 'y':
                print("✅ Keeping existing API key")
                return
    else:
        print("📝 Creating .env file...")
    
    print("\n📋 To get your Gemini API key:")
    print("   1. Go to: https://makersuite.google.com/app/apikey")
    print("   2. Click 'Create API Key'")
    print("   3. Copy the generated key")
    
    # Get API key from user
    api_key = input("\n🔑 Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return
    
    if len(api_key) < 20:
        print("⚠️ Warning: API key seems too short. Please verify it's correct.")
        confirm = input("Continue anyway? (y/n): ").lower().strip()
        if confirm != 'y':
            print("❌ Setup cancelled.")
            return
    
    # Update .env file
    try:
        if env_file.exists():
            # Read existing content
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Update or add API key line
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('GEMINI_API_KEY='):
                    lines[i] = f'GEMINI_API_KEY={api_key}\n'
                    updated = True
                    break
            
            if not updated:
                lines.append(f'GEMINI_API_KEY={api_key}\n')
            
            # Write back
            with open(env_file, 'w') as f:
                f.writelines(lines)
        else:
            # Create new .env file
            env_content = f"""# Environment Configuration File
# Add your API keys and configuration here

# Google Gemini API Key
GEMINI_API_KEY={api_key}

# Processing Configuration
DEFAULT_DEVICE_TYPE=linear_accelerator
DEFAULT_MAX_PAGES=20
DEFAULT_OUTPUT_DIR=data/real_pdf_results

# Dashboard Configuration
DASHBOARD_HOST=localhost
DASHBOARD_PORT=8000
"""
            with open(env_file, 'w') as f:
                f.write(env_content)
        
        print("✅ API key saved to .env file")
        
        # Test the configuration
        print("\n🧪 Testing configuration...")
        
        try:
            from config import config
            
            if config.GEMINI_API_KEY == api_key:
                print("✅ Configuration loaded successfully")
                
                # Test API connection
                test_api = input("\nDo you want to test the API connection? (y/n): ").lower().strip()
                if test_api == 'y':
                    test_gemini_api(api_key)
            else:
                print("❌ Configuration test failed")
        
        except Exception as e:
            print(f"❌ Configuration test error: {e}")
    
    except Exception as e:
        print(f"❌ Error saving API key: {e}")

def test_gemini_api(api_key):
    """Test Gemini API connection"""
    
    print("🔄 Testing Gemini API connection...")
    
    try:
        import google.generativeai as genai
        
        # Configure API
        genai.configure(api_key=api_key)
        
        # Test with simple request
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, this is a test. Please respond with 'API test successful'.")
        
        if response and response.text:
            print("✅ API connection successful!")
            print(f"📝 Response: {response.text.strip()}")
        else:
            print("⚠️ API responded but with empty content")
    
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("💡 This might be due to:")
        print("   - Invalid API key")
        print("   - Network connectivity issues")
        print("   - API quota exceeded")

def main():
    """Main setup function"""
    
    print("🏥 Medical Device Ontology Extraction System")
    print("🔧 API Key Setup Helper")
    print()
    
    setup_api_key()
    
    print("\n🎯 Next Steps:")
    print("   1. Run: python test_setup.py")
    print("   2. Place your PDF in: data/input_pdfs/")
    print("   3. Run: python run_with_real_pdf.py \"data/input_pdfs/your_file.pdf\"")

if __name__ == "__main__":
    main()