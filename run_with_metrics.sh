#!/bin/bash

echo "🚀 Starting Dubai Estate AI with Observability"
echo "=============================================="

# Clean up old Prometheus multiprocess metrics
echo "🧹 Cleaning up old metrics..."
rm -rf prometheus_multiproc_dir/*.db 2>/dev/null || true

# Start FastAPI in background for /metrics endpoint
echo "📊 Starting metrics server..."
uvicorn main:app --host 0.0.0.0 --port 8000 > fastapi.log 2>&1 &
FASTAPI_PID=$!

# Give FastAPI time to start
sleep 3

# Check if FastAPI started successfully
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Metrics endpoint running on http://localhost:8000/metrics"
else
    echo "⚠️  Warning: Metrics endpoint may not be ready yet"
fi

# Start Telegram bot
echo "🤖 Starting Telegram bot..."
python run.py

# Cleanup on exit
trap "kill $FASTAPI_PID 2>/dev/null" EXIT
