#!/usr/bin/env bash
# Render start script for GPUOptimizer

set -o errexit  # exit on error

echo "🚀 Starting GPUOptimizer production server..."

# Set default port if not provided
export PORT=${PORT:-10000}

# Set production environment
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:."

# Create logs directory
mkdir -p logs

# Start the application
echo "🌐 Starting server on port $PORT..."
python gpu_optimizer_system.py
