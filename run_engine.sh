#!/bin/bash
# Wrapper to run state_engine.py using the correct virtual environment

# Ensure we are in the script's directory
cd "$(dirname "$0")"

# Execute using the venv python
./venv_stable/bin/python3 state_engine.py
