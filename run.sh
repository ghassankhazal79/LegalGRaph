#!/usr/bin/env bash
set -e
echo "Installing requirements..."
pip install -r requirements.txt
echo "Starting Flask app..."
python app/app.py
