#!/bin/bash
# BARAKA AI - Setup Script

set -e

echo "🚀 Setting up BARAKA AI Trading Platform..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Create necessary directories
mkdir -p data models logs

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose up -d --build

echo "✅ Setup complete!"
echo ""
echo "📊 Services:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/api/docs"
echo ""
echo "📝 Logs: docker-compose logs -f"
