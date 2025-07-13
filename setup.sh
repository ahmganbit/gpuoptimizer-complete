#!/bin/bash

# =============================================================================
# GPUOptimizer Revenue System - Quick Setup Script
# Automated setup for development and production environments
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to generate random string
generate_random_string() {
    openssl rand -hex 32
}

# Main setup function
main() {
    print_status "Starting GPUOptimizer Revenue System setup..."
    
    # Check system requirements
    check_requirements
    
    # Setup environment
    setup_environment
    
    # Install dependencies
    install_dependencies
    
    # Initialize databases
    initialize_databases
    
    # Setup systemd service (if on Linux)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        setup_systemd_service
    fi
    
    # Final instructions
    print_final_instructions
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python version
    if command_exists python3.11; then
        PYTHON_CMD="python3.11"
    elif command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 1 ]]; then
            PYTHON_CMD="python3"
        else
            print_error "Python 3.8+ is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3.8+ is required but not found."
        exit 1
    fi
    
    print_success "Python check passed: $($PYTHON_CMD --version)"
    
    # Check pip
    if ! command_exists pip3; then
        print_error "pip3 is required but not found."
        exit 1
    fi
    
    # Check git
    if ! command_exists git; then
        print_warning "Git not found. Some features may not work."
    fi
    
    # Check Docker (optional)
    if command_exists docker; then
        print_success "Docker found: $(docker --version)"
    else
        print_warning "Docker not found. Container deployment will not be available."
    fi
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp .env.example .env
        
        # Generate random secrets
        SECRET_KEY=$(generate_random_string)
        JWT_SECRET_KEY=$(generate_random_string)
        
        # Update .env with generated secrets
        sed -i "s/your_flask_secret_key_here_make_it_long_and_random/$SECRET_KEY/" .env
        sed -i "s/your_jwt_secret_for_api_auth/$JWT_SECRET_KEY/" .env
        
        print_warning "Please edit .env file with your API keys and configuration!"
        print_warning "Required: FLUTTERWAVE_SECRET_KEY, NOWPAYMENTS_API_KEY, SENDER_EMAIL, SENDER_PASSWORD"
    fi
    
    # Create necessary directories
    mkdir -p data logs static
    
    print_success "Environment setup completed"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Dependencies installed successfully"
}

# Initialize databases
initialize_databases() {
    print_status "Initializing databases..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Initialize databases using Python
    $PYTHON_CMD -c "
from gpu_optimizer_system import RevenueManager
from autonomous_acquisition import AutonomousAcquisition

# Initialize revenue database
revenue_manager = RevenueManager()
revenue_manager.init_database()
print('Revenue database initialized')

# Initialize acquisition database
acquisition = AutonomousAcquisition(revenue_manager)
print('Acquisition database initialized')
"
    
    print_success "Databases initialized successfully"
}

# Setup systemd service
setup_systemd_service() {
    print_status "Setting up systemd service..."
    
    # Check if running as root or with sudo
    if [ "$EUID" -ne 0 ]; then
        print_warning "Systemd service setup requires sudo privileges. Skipping..."
        return
    fi
    
    # Create systemd service file
    cat > /etc/systemd/system/gpu-optimizer.service << EOF
[Unit]
Description=GPUOptimizer Revenue System
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 gpu_optimizer_system:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable gpu-optimizer
    
    print_success "Systemd service created and enabled"
}

# Print final instructions
print_final_instructions() {
    print_success "GPUOptimizer Revenue System setup completed!"
    echo
    print_status "Next steps:"
    echo "1. Edit .env file with your API keys and configuration"
    echo "2. Start the application:"
    echo "   Development: source venv/bin/activate && python gpu_optimizer_system.py"
    echo "   Production:  source venv/bin/activate && gunicorn --bind 0.0.0.0:5000 gpu_optimizer_system:app"
    echo "3. Access the application at http://localhost:5000"
    echo
    print_status "For Docker deployment:"
    echo "1. Ensure .env file is configured"
    echo "2. Run: docker-compose up -d"
    echo
    print_status "For GPU monitoring setup:"
    echo "1. Install NVIDIA drivers on target machines"
    echo "2. Copy gpu_optimizer_agent.py to target machines"
    echo "3. Set GPU_OPTIMIZER_API_KEY environment variable"
    echo "4. Run: python gpu_optimizer_agent.py"
    echo
    print_warning "Remember to:"
    echo "- Configure payment gateway webhooks"
    echo "- Set up SSL certificates for production"
    echo "- Configure email SMTP settings"
    echo "- Test all integrations before going live"
}

# Run main function
main "$@"

