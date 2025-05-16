#!/bin/bash

echo "🔧 Running setup.py to fetch files from GCS..."
python setup.py

echo "🚀 Starting main server..."
python server.py
