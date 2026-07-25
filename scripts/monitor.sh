#!/bin/bash
# Monitoring script

echo "GLS Warehouse Safety - Monitoring Script"
echo "=========================================="

SOURCE=${1:-0}
SAVE=${2:-""}

if [ "$SAVE" == "--save" ]; then
    echo "Monitoring with video output..."
    python -m src.main monitor --source $SOURCE --save-video
else
    echo "Monitoring without video output..."
    python -m src.main monitor --source $SOURCE
fi

echo "Monitoring complete!"
