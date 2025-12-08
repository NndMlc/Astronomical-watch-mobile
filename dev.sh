#!/bin/bash
# Development runner with hot reload support

echo "=================================="
echo "  Astronomical Watch - Dev Mode"
echo "=================================="
echo ""

# Check if running in Codespaces or remote environment
if [ -n "$CODESPACES" ] || [ -n "$REMOTE_CONTAINERS" ]; then
    echo "⚠️  Running in remote environment (Codespaces/Remote Container)"
    echo "   Kivy requires display output - GUI won't be visible"
    echo "   Use X11 forwarding or VNC for display"
    echo ""
    
    # Check if DISPLAY is set
    if [ -z "$DISPLAY" ]; then
        echo "❌ DISPLAY variable not set"
        echo "   To enable display:"
        echo "   1. Install VNC: sudo apt-get install -y x11vnc xvfb"
        echo "   2. Start Xvfb: Xvfb :99 -screen 0 1024x768x24 &"
        echo "   3. Set DISPLAY: export DISPLAY=:99"
        echo ""
        exit 1
    fi
fi

# Activate poetry environment
echo "🔧 Activating Poetry environment..."
export KIVY_NO_CONSOLELOG=1

# Run with poetry
echo "🚀 Starting Astronomical Watch..."
echo ""
poetry run python main.py

echo ""
echo "✋ App stopped"
