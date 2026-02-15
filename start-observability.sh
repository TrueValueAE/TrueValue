#!/bin/bash

echo "🚀 Starting Dubai Estate AI Observability Stack"
echo "================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your API keys before continuing."
    echo "   Then run this script again."
    exit 1
fi

echo "✅ Docker is running"
echo "✅ .env file found"
echo ""

# Build and start containers
echo "🏗️  Building containers..."
docker-compose build

echo ""
echo "🚀 Starting all services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "📊 Service Status:"
echo "=================="
docker-compose ps

echo ""
echo "✅ All services started!"
echo ""
echo "🌐 Access URLs:"
echo "==============="
echo "  Grafana:    http://localhost:3000 (admin/admin)"
echo "  Prometheus: http://localhost:9090"
echo "  Loki:       http://localhost:3100"
echo "  Tempo:      http://localhost:3200"
echo "  Bot API:    http://localhost:8000"
echo ""
echo "📊 Dashboards:"
echo "============="
echo "  Go to Grafana → Dashboards → Browse → Dubai Estate AI"
echo ""
echo "  Available dashboards:"
echo "    1. 🚀 Mission Control"
echo "    2. 👥 User Analytics & Business Metrics"
echo "    3. 🤖 AI & Cost Analytics"
echo ""
echo "📜 View logs:"
echo "============"
echo "  docker-compose logs -f app      # Application logs"
echo "  docker-compose logs -f grafana  # Grafana logs"
echo ""
echo "🛑 Stop all services:"
echo "===================="
echo "  ./stop-observability.sh"
echo "  or"
echo "  docker-compose down"
echo ""
echo "🎉 Setup complete! Send a query to your Telegram bot to see metrics!"
