#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🛑 Stopping infrastructure stack..."
cd "$PROJECT_DIR"

docker compose down

echo "✓ Infrastructure stopped"
