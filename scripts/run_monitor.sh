#!/bin/bash

# Activate the virtual environment
source ../.venv/bin/activate

# Run the monitor script
python ../edge_monitoring/monitor.py

# Optional: deactivate the virtual environment after running
deactivate
