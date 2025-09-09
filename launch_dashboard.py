"""
Launch Expert Review Dashboard
Starts the dashboard without populating sample data
"""

import uvicorn
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def main():
    """Main function to start the dashboard server"""
    
    print("🏥 Expert Review Dashboard")
    print("=" * 50)
    print("📊 Dashboard will be available at: http://localhost:12345")
    print("🔧 API endpoints available at: http://localhost:12345/api/expert-review/")
    print("\n💡 Use the 'Load PDF Results' button to load extracted entities")
    print("⚠️  Note: Dashboard starts empty - load PDF results or use test data")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Import and run the FastAPI app
    try:
        from backend.api.main import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=12345,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("💡 Make sure you have installed the required dependencies:")
        print("   pip install fastapi uvicorn jinja2 python-multipart")

if __name__ == "__main__":
    main()