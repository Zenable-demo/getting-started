#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📋 Streaming infrastructure logs (Ctrl+C to exit)..."
cd "$PROJECT_DIR"

docker compose logs -f
