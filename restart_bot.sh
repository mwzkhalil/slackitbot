#!/bin/bash
# Quick restart script with proper environment

echo "🔄 Restarting E. Alex bot..."
echo ""

# Kill any running instances
pkill -f "python -m src.main" || true
pkill -f "uvicorn src.main" || true
sleep 2

# Activate virtual environment and start server
cd /home/mahwiz/Mahwiz/slackitbot
source venv/bin/activate

echo "✓ Starting server on port 5001..."
nohup python -m src.main > server.log 2>&1 &

sleep 3
echo ""
echo "✓ Server started! Logs are in server.log"
echo ""
echo "To view logs:"
echo "  tail -f server.log"
echo ""
echo "To stop:"
echo "  pkill -f 'python -m src.main'"
echo ""
