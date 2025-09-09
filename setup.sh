#!/bin/bash

# PDF Knowledge Graph Extraction System - Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up PDF Knowledge Graph Extraction System..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✅ Python version $python_version is compatible"
else
    echo "❌ Python version $python_version is not compatible. Required: >= $required_version"
    exit 1
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Download spaCy models
echo "🧠 Downloading NLP models..."
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p uploads
mkdir -p data/{graphs,ontologies,temp}
mkdir -p logs
mkdir -p tests
mkdir -p docs

# Create placeholder files
touch uploads/.gitkeep
touch data/graphs/.gitkeep
touch data/ontologies/.gitkeep
touch data/temp/.gitkeep
touch logs/.gitkeep

# Set permissions
echo "🔐 Setting file permissions..."
chmod -R 755 backend/
chmod -R 755 frontend/
chmod 755 setup.sh

echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the server: make run"
echo "3. Open browser: http://localhost:8000"
echo ""
echo "📖 For more information, see README.md"
