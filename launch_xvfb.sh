#!/bin/bash
# Launch Astronomical Watch with virtual X server (Xvfb)
# Usage: ./launch_xvfb.sh

set -e

echo "🚀 Starting Astronomical Watch Mobile..."

# Kill any existing instances
pkill -9 Xvfb 2>/dev/null || true
pkill -9 python 2>/dev/null || true
sleep 1

# Start Xvfb virtual display
echo "📺 Starting virtual display (Xvfb)..."
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
XVFB_PID=$!
export DISPLAY=:99

# Wait for Xvfb to be ready
sleep 2

# Show current astronomical time
echo ""
echo "⏰ Current Astronomical Time:"
poetry run python -c "
from astronomical_watch.core.timeframe import astronomical_time
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
dies, milidies = astronomical_time(now)
print(f'   Dies: {dies}')
print(f'   miliDies: {milidies:03d}')
print(f'   Standard: {now.strftime(\"%Y-%m-%d %H:%M:%S UTC\")}')
"

echo ""
echo "🌌 Starting Kivy application..."
echo "   Display: :99 (1024x768)"
echo "   Press Ctrl+C to stop"
echo ""

# Run the app
poetry run python main.py

# Cleanup on exit
echo ""
echo "🛑 Stopping..."
kill $XVFB_PID 2>/dev/null || true
echo "✅ Done"
