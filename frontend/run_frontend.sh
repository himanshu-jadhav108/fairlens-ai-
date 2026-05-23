#!/usr/bin/env bash
set -e

echo "FairLens AI Frontend Startup"
echo "============================"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is not installed or not in PATH"
  exit 1
fi

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

echo "Starting frontend at http://localhost:5173"
npm run dev
#!/usr/bin/env bash
# FairLens AI — Frontend quick start script
# Usage: bash run_frontend.sh

set -e

echo "⚖️  FairLens AI — Frontend Startup"
echo "===================================="

# Check node
if ! command -v node &>/dev/null; then
    echo "❌ Node.js not found. Install from https://nodejs.org"
    exit 1
fi

NODE_VER=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VER" -lt 18 ]; then
    echo "⚠️  Node.js 18+ required (found: $(node -v))"
    exit 1
fi

# Install deps if needed
if [ ! -d "node_modules" ]; then
    echo "📥 Installing npm packages..."
    npm install
fi

echo "🚀 Starting React dev server on http://localhost:5173"
echo ""
npm run dev
