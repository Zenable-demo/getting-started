#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting infrastructure stack..."
cd "$PROJECT_DIR"

docker compose up -d --wait

echo "✓ Infrastructure is up and healthy"
echo ""
echo "Services available at:"
echo "  - API: http://localhost:8000"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - RabbitMQ: http://localhost:15672 (guest:guest)"
