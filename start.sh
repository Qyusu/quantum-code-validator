#!/bin/bash

echo "🔧 Running setup.py to fetch files from GCS..."
python -m scripts.setup

echo "🚀 Starting main server..."
python server.py
