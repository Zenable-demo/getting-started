#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔄 Resetting infrastructure stack (removing volumes)..."
cd "$PROJECT_DIR"

docker compose down -v

echo "🚀 Starting fresh infrastructure stack..."
docker compose up -d --wait

echo "✓ Infrastructure reset and running"
