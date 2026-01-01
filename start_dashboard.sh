#!/bin/bash
# Check if python3 is available
if command -v python3 &>/dev/null; then
    echo "Starting Dashboard Server on port 8000..."
    echo "Opening http://localhost:8000 in your browser..."
    # Open browser after 1 second
    (sleep 1 && open "http://localhost:8000") &
    # Start server
    python3 -m http.server 8000
else
    echo "Error: Python 3 is not installed."
fi
