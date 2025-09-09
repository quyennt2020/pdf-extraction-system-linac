"""
Configuration Management
Loads API keys and settings from .env file or environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

class Config:
    """Configuration class for the ontology extraction system"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Processing Settings
    DEFAULT_DEVICE_TYPE = os.getenv('DEFAULT_DEVICE_TYPE', 'linear_accelerator')
    DEFAULT_MAX_PAGES = int(os.getenv('DEFAULT_MAX_PAGES', '20'))
    DEFAULT_OUTPUT_DIR = os.getenv('DEFAULT_OUTPUT_DIR', 'data/real_pdf_results')
    
    # Dashboard Settings
    DASHBOARD_HOST = os.getenv('DASHBOARD_HOST', 'localhost')
    DASHBOARD_PORT = int(os.getenv('DASHBOARD_PORT', '8000'))
    
    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', '7'))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required")
        
        if cls.GEMINI_API_KEY and len(cls.GEMINI_API_KEY) < 20:
            errors.append("GEMINI_API_KEY appears to be invalid (too short)")
        
        return errors
    
    @classmethod
    def print_config(cls):
        """Print current configuration (without sensitive data)"""
        print("📋 Current Configuration:")
        print(f"   Device Type: {cls.DEFAULT_DEVICE_TYPE}")
        print(f"   Max Pages: {cls.DEFAULT_MAX_PAGES}")
        print(f"   Output Dir: {cls.DEFAULT_OUTPUT_DIR}")
        print(f"   Dashboard: {cls.DASHBOARD_HOST}:{cls.DASHBOARD_PORT}")
        print(f"   API Key: {'✅ Set' if cls.GEMINI_API_KEY else '❌ Not Set'}")

# Create global config instance
config = Config()

if __name__ == "__main__":
    # Test configuration
    config.print_config()
    
    errors = config.validate()
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("\n✅ Configuration is valid!")