#!/bin/bash
#
# FragDenStaat Monitoring Wrapper Script
#
# This script wraps the Python monitoring script with proper environment setup.
# It ensures the virtual environment is activated and handles errors gracefully.
#

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
VENV_DIR="$REPO_ROOT/.venv"
PYTHON_SCRIPT="$SCRIPT_DIR/monitor_fragdenstaat.py"
LOG_FILE="$REPO_ROOT/monitoring.log"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "ERROR: Virtual environment not found at $VENV_DIR" | tee -a "$LOG_FILE"
    echo "Please create it with: cd $REPO_ROOT && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" | tee -a "$LOG_FILE"
    exit 1
fi

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "ERROR: Python script not found at $PYTHON_SCRIPT" | tee -a "$LOG_FILE"
    exit 1
fi

# Activate virtual environment and run the monitoring script
echo "====================================================================" >> "$LOG_FILE"
echo "Starting FragDenStaat monitoring at $(date)" >> "$LOG_FILE"
echo "====================================================================" >> "$LOG_FILE"

# Run with virtual environment Python
"$VENV_DIR/bin/python" "$PYTHON_SCRIPT"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Monitoring completed successfully at $(date)" >> "$LOG_FILE"
else
    echo "Monitoring failed with exit code $EXIT_CODE at $(date)" >> "$LOG_FILE"
fi

exit $EXIT_CODE
