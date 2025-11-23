#!/bin/bash
# Script to run Nova2FA tests with proper Django configuration

# Set up environment
export DJANGO_SETTINGS_MODULE=example_project.settings
export PYTHONPATH=/home/Nova/Desktop/Projects/Nova2FA-main/example_project:$PYTHONPATH

# Activate virtual environment if not already active
if [ -z "$VIRTUAL_ENV" ]; then
    source /home/Nova/Desktop/Projects/Nova2FA-main/.venv/bin/activate
fi

# Run pytest
cd /home/Nova/Desktop/Projects/Nova2FA-main
.venv/bin/python -m pytest tests/ "$@"
