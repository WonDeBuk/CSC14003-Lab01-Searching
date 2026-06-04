#!/bin/bash
echo "============================================"
echo "  AI Search Algorithm Visualizer"
echo "  Starting server..."
echo "============================================"
echo ""

cd "$(dirname "$0")/backend"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed."
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install deps
echo "[SETUP] Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "============================================"
echo "  Server running at: http://localhost:8000"
echo "  Press Ctrl+C to stop"
echo "============================================"
echo ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
