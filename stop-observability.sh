#!/bin/bash

echo "🛑 Stopping Dubai Estate AI Observability Stack"
echo "==============================================="
echo ""

docker-compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "💾 Data is preserved in Docker volumes:"
echo "  - prometheus_data"
echo "  - loki_data"
echo "  - tempo_data"
echo "  - grafana_data"
echo ""
echo "🗑️  To completely remove all data:"
echo "   docker-compose down -v"
echo ""
echo "🚀 To start again:"
echo "   ./start-observability.sh"
