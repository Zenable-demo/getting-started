#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📦 Initializing frontend dependencies..."
cd "$PROJECT_DIR/frontend"

if ! command -v npm &> /dev/null; then
  echo "❌ npm is not installed. Please install Node.js and npm."
  exit 1
fi

npm ci

echo "✓ Frontend dependencies installed"
echo ""
echo "To start the development server, run:"
echo "  npm --prefix frontend run dev"
