#!/bin/bash
# Launch Astronomical Watch with VNC viewer in VS Code Simple Browser
# Usage: ./launch_vnc.sh

set -e

echo "🚀 Starting Astronomical Watch Mobile with VNC viewer..."
echo ""

# Kill any existing instances
echo "🧹 Cleaning up old processes..."
pkill -9 python 2>/dev/null || true
pkill -9 Xvfb 2>/dev/null || true
pkill -9 x11vnc 2>/dev/null || true
pkill -9 websockify 2>/dev/null || true
sleep 2

# Start Xvfb virtual display
echo "📺 Starting Xvfb (virtual display :99)..."
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
XVFB_PID=$!
export DISPLAY=:99
sleep 2

# Start x11vnc server
echo "🖥️  Starting VNC server..."
x11vnc -display :99 -nopw -listen localhost -xkb -forever -shared > /tmp/x11vnc.log 2>&1 &
X11VNC_PID=$!
sleep 2

# Start websockify + noVNC
echo "🌐 Starting noVNC web interface..."
websockify --web=/usr/share/novnc/ 6080 localhost:5900 > /tmp/websockify.log 2>&1 &
WEBSOCKIFY_PID=$!
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

# Start Kivy app
echo ""
echo "📱 Starting Kivy application..."
poetry run python main.py > /tmp/kivy.log 2>&1 &
KIVY_PID=$!
sleep 3

# Verify all processes
echo ""
echo "✅ All services running:"
echo "   📺 Xvfb: :99 (1024x768) - PID $XVFB_PID"
echo "   🖥️  x11vnc: localhost:5900 - PID $X11VNC_PID"
echo "   🌐 noVNC: http://localhost:6080/vnc.html - PID $WEBSOCKIFY_PID"
echo "   📱 Kivy app - PID $KIVY_PID"
echo ""
echo "🎨 Open in VS Code:"
echo "   1. Press Ctrl+Shift+P (or Cmd+Shift+P on Mac)"
echo "   2. Type: Simple Browser: Show"
echo "   3. URL: http://localhost:6080/vnc.html"
echo "   4. Click 'Connect' button"
echo ""
echo "💡 Or click this link in VS Code terminal:"
echo "   http://localhost:6080/vnc.html"
echo ""
echo "🛑 To stop all services:"
echo "   pkill -9 python; pkill -9 Xvfb; pkill -9 x11vnc; pkill -9 websockify"
echo ""
echo "📋 View logs:"
echo "   Kivy: tail -f /tmp/kivy.log"
echo "   VNC: tail -f /tmp/x11vnc.log"
echo "   noVNC: tail -f /tmp/websockify.log"
echo ""
echo "⌨️  Press Ctrl+C to keep services running in background, or wait..."

# Wait for user interrupt (optional)
sleep infinity
