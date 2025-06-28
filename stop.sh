#!/bin/bash

# RSS Reader Stop Script
# Stops the Streamlit application

echo "🛑 Stopping RSS Reader..."

# Find and kill streamlit processes
PIDS=$(pgrep -f "streamlit run app.py" || true)

if [ -z "$PIDS" ]; then
    echo "ℹ️  No RSS Reader processes found running"
else
    echo "🔄 Stopping processes: $PIDS"
    kill $PIDS
    sleep 2
    
    # Force kill if still running
    PIDS=$(pgrep -f "streamlit run app.py" || true)
    if [ ! -z "$PIDS" ]; then
        echo "⚠️  Force stopping processes: $PIDS"
        kill -9 $PIDS
    fi
    
    echo "✅ RSS Reader stopped successfully"
fi