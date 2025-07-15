#!/usr/bin/env bash
# Render build script for GPUOptimizer

set -o errexit  # exit on error

echo "🚀 Starting GPUOptimizer build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p reports
mkdir -p temp

# Set up database (SQLite for now, can upgrade to PostgreSQL later)
echo "🗄️ Setting up database..."
python -c "
import sqlite3
import os

# Create database directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Initialize database
conn = sqlite3.connect('data/gpuoptimizer.db')
cursor = conn.cursor()

# Create tables (basic setup)
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    tier TEXT DEFAULT 'free',
    api_key TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_payment TIMESTAMP,
    gpu_count INTEGER DEFAULT 0,
    monthly_savings REAL DEFAULT 0.0
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS gpu_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_email TEXT,
    instance_id TEXT,
    provider TEXT,
    instance_type TEXT,
    region TEXT,
    cost_per_hour REAL,
    utilization REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_email) REFERENCES customers (email)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS payment_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_email TEXT,
    payment_id TEXT UNIQUE,
    payment_gateway TEXT,
    amount REAL,
    currency TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
)
''')

conn.commit()
conn.close()
print('✅ Database initialized successfully')
"

echo "✅ Build completed successfully!"
echo "🚀 GPUOptimizer is ready for deployment!"
