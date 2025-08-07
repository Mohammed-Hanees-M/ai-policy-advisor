#!/bin/bash

# Purpose: Sets up the local development environment for the project.
# Usage: ./scripts/setup_env.sh

echo "🚀 Starting local environment setup..."

# --- Python Virtual Environment ---

# 1. Create a virtual environment directory named '.venv'
# This isolates the project's dependencies from the global Python environment.
echo "🐍 Creating Python virtual environment..."
python3 -m venv .venv

# 2. Activate the virtual environment
# This modifies the shell's PATH to use the python and pip from the .venv directory.
source .venv/bin/activate
echo "Virtual environment activated."


# --- Install Dependencies ---

# 1. Upgrade pip to the latest version
echo "📦 Upgrading pip..."
pip install --upgrade pip

# 2. Install all required Python packages from requirements.txt
echo "📦 Installing project dependencies..."
pip install -r requirements.txt
echo "Dependencies installed."


# --- Create Required Directories ---

echo "📁 Creating necessary directories..."
# Create cache directory for embeddings to speed up re-runs
mkdir -p .cache/embeddings

# Create directory for storing chat history files
mkdir -p .chat_memory

# Create directory for caching generated audio files
mkdir -p static/audio
echo "Directories created."


# --- Install Tesseract for OCR ---

echo "🔍 Installing Tesseract OCR (requires sudo/brew)..."
# Tesseract is used for extracting text from images.
# The installation command depends on the operating system.

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # For Debian/Ubuntu-based Linux
    echo "Detected Linux. Attempting to install with apt-get..."
    sudo apt-get update && sudo apt-get install -y tesseract-ocr
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # For macOS with Homebrew installed
    echo "Detected macOS. Attempting to install with Homebrew..."
    brew install tesseract
else
    echo "⚠️ Unsupported OS for automatic Tesseract installation."
    echo "Please install Tesseract manually: https://tesseract-ocr.github.io/tessdoc/Installation.html"
fi

echo "✅ Environment setup complete!"
echo "To start the application, run: streamlit run src/app.py"
