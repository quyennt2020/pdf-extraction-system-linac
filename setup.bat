@echo off
echo 🚀 Setting up PDF Knowledge Graph Extraction System...

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
if not exist venv (
    echo 🐍 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing Python dependencies...
pip install -r requirements.txt

REM Download spaCy models
echo 🧠 Downloading NLP models...
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg

REM Create necessary directories
echo 📁 Creating project directories...
if not exist uploads mkdir uploads
if not exist data mkdir data
if not exist data\graphs mkdir data\graphs
if not exist data\ontologies mkdir data\ontologies
if not exist data\temp mkdir data\temp
if not exist logs mkdir logs
if not exist tests mkdir tests
if not exist docs mkdir docs

REM Create placeholder files
type nul > uploads\.gitkeep
type nul > data\graphs\.gitkeep
type nul > data\ontologies\.gitkeep
type nul > data\temp\.gitkeep
type nul > logs\.gitkeep

echo ✅ Setup completed successfully!
echo.
echo 🎯 Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run the server: cd backend ^&^& python -m uvicorn api.main:app --reload
echo 3. Open browser: http://localhost:8000
echo.
echo 📖 For more information, see README.md

pause
