"""
Quick Start Script for PDF Processing
Automatically detects PDF files and runs processing
"""

import os
import sys
import subprocess
import glob
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def run_setup_test():
    """Run the setup test"""
    print("\n🧪 Running setup test...")
    
    try:
        result = subprocess.run([sys.executable, "test_setup.py"], 
                              capture_output=True, text=True, check=False)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running setup test: {e}")
        return False

def find_pdf_files():
    """Find PDF files in the input directory"""
    pdf_pattern = "data/input_pdfs/*.pdf"
    pdf_files = glob.glob(pdf_pattern)
    return pdf_files

def process_pdf(pdf_path, max_pages=5, start_dashboard=False):
    """Process a PDF file"""
    print(f"\n🔄 Processing: {os.path.basename(pdf_path)}")
    
    cmd = [sys.executable, "run_with_real_pdf.py", pdf_path, "--max-pages", str(max_pages)]
    
    if start_dashboard:
        cmd.append("--start-dashboard")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return False

def main():
    """Main function"""
    print("🏥 Medical Device PDF Processing - Quick Start")
    print("=" * 50)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please run manually:")
        print("   pip install python-dotenv")
        print("   pip install -r requirements.txt")
        return
    
    # Step 2: Run setup test
    setup_ok = run_setup_test()
    if not setup_ok:
        print("⚠️ Setup test had issues, but continuing...")
    
    # Step 3: Find PDF files
    pdf_files = find_pdf_files()
    
    if not pdf_files:
        print("\n❌ No PDF files found in data/input_pdfs/")
        print("📁 Please place your PDF file in: data/input_pdfs/")
        print("💡 Then run this script again")
        input("Press Enter to exit...")
        return
    
    print(f"\n📄 Found {len(pdf_files)} PDF file(s):")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"   {i}. {os.path.basename(pdf_file)}")
    
    # Step 4: Choose processing option
    print(f"\n🎯 Processing Options:")
    print("1. Quick test (5 pages)")
    print("2. Test with dashboard (10 pages)")
    print("3. Full processing (20 pages)")
    print("4. Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "4":
            print("👋 Goodbye!")
            return
        
        # Choose PDF file
        if len(pdf_files) == 1:
            selected_pdf = pdf_files[0]
            print(f"\n📄 Processing: {os.path.basename(selected_pdf)}")
        else:
            try:
                pdf_choice = int(input(f"\nSelect PDF file (1-{len(pdf_files)}): ")) - 1
                if 0 <= pdf_choice < len(pdf_files):
                    selected_pdf = pdf_files[pdf_choice]
                else:
                    print("❌ Invalid choice")
                    return
            except ValueError:
                print("❌ Invalid input")
                return
        
        # Process based on choice
        if choice == "1":
            success = process_pdf(selected_pdf, max_pages=5, start_dashboard=False)
        elif choice == "2":
            success = process_pdf(selected_pdf, max_pages=10, start_dashboard=True)
        elif choice == "3":
            success = process_pdf(selected_pdf, max_pages=20, start_dashboard=True)
        else:
            print("❌ Invalid choice")
            return
        
        if success:
            print("\n✅ Processing completed!")
            print("📁 Check results in: data/real_pdf_results/")
            
            if choice in ["2", "3"]:
                print("🌐 Dashboard available at: http://localhost:8000")
        else:
            print("\n❌ Processing failed. Check the output above for errors.")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()