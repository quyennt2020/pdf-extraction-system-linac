"""
Setup and installation script for Medical Device Ontology Extraction System
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("⚠️ Please install Python 3.8 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def create_directories():
    """Create necessary project directories"""
    directories = [
        "data/medical_manuals",
        "data/extracted_entities",
        "data/reviewed_data", 
        "data/ontologies",
        "data/knowledge_graphs",
        "data/temp",
        "logs",
        "uploads"
    ]
    
    print("📁 Creating project directories...")
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # Create .gitkeep file
        gitkeep_path = os.path.join(directory, ".gitkeep")
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, "w") as f:
                f.write("# Keep this directory in git\n")
    
    print("✅ Directories created successfully")


def install_dependencies():
    """Install Python dependencies"""
    
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -r requirements.txt", "Installing Python packages")
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    
    return True


def download_nlp_models():
    """Download required NLP models"""
    
    commands = [
        ("python -m spacy download en_core_web_sm", "Downloading spaCy small model"),
        # ("python -m spacy download en_core_web_lg", "Downloading spaCy large model")  # Optional for now
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print(f"⚠️ {description} failed - continuing anyway")
    
    return True


def create_env_file():
    """Create .env file from template if it doesn't exist"""
    
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    
    # Read current .env content as template
    try:
        with open(".env", "r") as f:
            env_content = f.read()
        
        # You might want to prompt for actual API key here
        print("⚠️ Please update the GOOGLE_API_KEY in .env file with your actual API key")
        return True
        
    except FileNotFoundError:
        print("❌ .env template file not found")
        return False


def test_installation():
    """Test the installation by running quick test"""
    
    print("🧪 Testing installation...")
    
    # First test imports
    try:
        import google.generativeai as genai
        print("✅ Google AI (Gemini) package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Google AI package: {e}")
        return False
    
    try:
        import fitz
        print("✅ PyMuPDF (fitz) package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PyMuPDF package: {e}")
        return False
    
    try:
        import pdfplumber
        print("✅ pdfplumber package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pdfplumber package: {e}")
        return False
    
    # Test spaCy model
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load spaCy model: {e}")
        return False
    
    print("✅ All core packages imported successfully")
    return True


def main():
    """Main setup function"""
    
    print("🏥 Medical Device Ontology Extraction System - Setup")
    print("=" * 60)
    
    # Step 1: Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Install dependencies
    print("\n📦 Installing dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Step 4: Download NLP models
    print("\n🧠 Downloading NLP models...")
    download_nlp_models()
    
    # Step 5: Setup environment
    print("\n⚙️ Setting up environment...")
    create_env_file()
    
    # Step 6: Test installation
    print("\n🧪 Testing installation...")
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    # Success message
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("1. Update your Google AI API key in the .env file")
    print("2. Place a medical device PDF in data/medical_manuals/")
    print("3. Run the quick test: python quick_test.py")
    print("4. Start the server: cd backend && python -m uvicorn api.main:app --reload")
    print()
    print("📚 Documentation:")
    print("- README.md: Full system documentation")
    print("- QUICKSTART.md: Quick start guide")
    print("- logs/: Check logs for detailed information")
    print()
    print("🔧 Troubleshooting:")
    print("- If tests fail, check the API key in .env")
    print("- For PDF processing issues, verify file permissions")
    print("- Check logs/ directory for error details")


if __name__ == "__main__":
    main()
