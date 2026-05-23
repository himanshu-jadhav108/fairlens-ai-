#!/usr/bin/env bash
# FairLens AI — Backend quick start script
# Usage: bash run_backend.sh

set -e

echo "⚖️  FairLens AI — Backend Startup"
echo "=================================="

# Check python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 not found. Install from https://python.org"
    exit 1
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install deps
echo "📥 Installing dependencies..."
pip install -r requirements.txt -q

# Run server
echo "🚀 Starting FastAPI on http://localhost:8000"
echo "📖 Swagger docs: http://localhost:8000/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
