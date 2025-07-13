#!/bin/bash

# GPUOptimizer Deployment Script
# Automated deployment to cloud platforms

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="gpuoptimizer"
DOCKER_IMAGE="ghcr.io/ahmganbit/gpuoptimizer"
DOMAIN="gpuoptimizer.ai"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    local deps=("docker" "docker-compose" "kubectl" "terraform" "aws" "git")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install the missing dependencies and try again."
        exit 1
    fi
    
    log_success "All dependencies are installed"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        log_info "Creating .env file from template..."
        cp .env.example .env
        log_warning "Please update the .env file with your actual values"
    fi
    
    # Load environment variables
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    log_success "Environment setup complete"
}

build_application() {
    log_info "Building application..."
    
    # Build frontend
    log_info "Building React frontend..."
    cd frontend
    npm ci
    npm run build
    cd ..
    
    # Build Docker image
    log_info "Building Docker image..."
    docker build -t "${DOCKER_IMAGE}:latest" .
    
    log_success "Application built successfully"
}

deploy_local() {
    log_info "Deploying locally with Docker Compose..."
    
    # Stop existing containers
    docker-compose down
    
    # Start new containers
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Health check
    if curl -f http://localhost:5000/api/health > /dev/null 2>&1; then
        log_success "Local deployment successful!"
        log_info "Application is running at http://localhost:5000"
    else
        log_error "Health check failed"
        exit 1
    fi
}

deploy_aws() {
    log_info "Deploying to AWS..."
    
    # Check AWS credentials
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        log_error "AWS credentials not configured"
        exit 1
    fi
    
    # Deploy infrastructure with Terraform
    log_info "Deploying infrastructure..."
    cd infrastructure/terraform
    terraform init
    terraform plan -var-file="environments/${ENVIRONMENT}.tfvars"
    terraform apply -var-file="environments/${ENVIRONMENT}.tfvars" -auto-approve
    cd ../..
    
    # Push Docker image to ECR
    log_info "Pushing Docker image to ECR..."
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com"
    docker tag "${DOCKER_IMAGE}:latest" "${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${PROJECT_NAME}:latest"
    docker push "${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${PROJECT_NAME}:latest"
    
    # Update ECS service
    log_info "Updating ECS service..."
    aws ecs update-service \
        --cluster "${PROJECT_NAME}-${ENVIRONMENT}" \
        --service "${PROJECT_NAME}-app" \
        --force-new-deployment
    
    # Wait for deployment to complete
    log_info "Waiting for deployment to complete..."
    aws ecs wait services-stable \
        --cluster "${PROJECT_NAME}-${ENVIRONMENT}" \
        --services "${PROJECT_NAME}-app"
    
    log_success "AWS deployment successful!"
}

deploy_kubernetes() {
    log_info "Deploying to Kubernetes..."
    
    # Check kubectl connection
    if ! kubectl cluster-info > /dev/null 2>&1; then
        log_error "kubectl not connected to a cluster"
        exit 1
    fi
    
    # Apply Kubernetes manifests
    log_info "Applying Kubernetes manifests..."
    kubectl apply -f deployment/k8s/
    
    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/gpuoptimizer-app -n gpuoptimizer
    
    # Get service URL
    SERVICE_URL=$(kubectl get service gpuoptimizer-service -n gpuoptimizer -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    
    log_success "Kubernetes deployment successful!"
    log_info "Application is available at: http://${SERVICE_URL}"
}

run_tests() {
    log_info "Running tests..."
    
    # Run test suite
    python run_tests.py all
    
    # Run security scan
    log_info "Running security scan..."
    bandit -r . -f json -o bandit-report.json || true
    safety check --json --output safety-report.json || true
    
    log_success "Tests completed"
}

setup_monitoring() {
    log_info "Setting up monitoring..."
    
    case $DEPLOYMENT_TARGET in
        "aws")
            # Setup CloudWatch monitoring
            log_info "Setting up CloudWatch monitoring..."
            ;;
        "kubernetes")
            # Setup Prometheus/Grafana
            log_info "Setting up Prometheus/Grafana monitoring..."
            kubectl apply -f deployment/monitoring/
            ;;
        "local")
            # Setup local monitoring
            log_info "Starting monitoring stack..."
            docker-compose -f docker-compose.monitoring.yml up -d
            ;;
    esac
    
    log_success "Monitoring setup complete"
}

setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    case $DEPLOYMENT_TARGET in
        "aws")
            log_info "SSL certificates managed by AWS Certificate Manager"
            ;;
        "kubernetes")
            log_info "Setting up cert-manager for SSL..."
            kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml
            kubectl apply -f deployment/k8s/cert-manager/
            ;;
        "local")
            log_info "Using self-signed certificates for local development"
            ;;
    esac
    
    log_success "SSL setup complete"
}

backup_database() {
    log_info "Creating database backup..."
    
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    
    case $DEPLOYMENT_TARGET in
        "aws")
            # Create RDS snapshot
            aws rds create-db-snapshot \
                --db-instance-identifier "${PROJECT_NAME}-${ENVIRONMENT}" \
                --db-snapshot-identifier "${PROJECT_NAME}-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"
            ;;
        "kubernetes"|"local")
            # Create database dump
            kubectl exec -n gpuoptimizer deployment/postgres -- pg_dump -U gpuopt gpuoptimizer > "$BACKUP_FILE"
            ;;
    esac
    
    log_success "Database backup created: $BACKUP_FILE"
}

show_help() {
    echo "GPUOptimizer Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  build       Build the application"
    echo "  deploy      Deploy the application"
    echo "  test        Run tests"
    echo "  backup      Create database backup"
    echo "  monitor     Setup monitoring"
    echo "  ssl         Setup SSL certificates"
    echo "  help        Show this help message"
    echo ""
    echo "Options:"
    echo "  -e, --env       Environment (local, staging, production)"
    echo "  -t, --target    Deployment target (local, aws, kubernetes)"
    echo "  -v, --verbose   Verbose output"
    echo ""
    echo "Examples:"
    echo "  $0 -e local -t local deploy"
    echo "  $0 -e production -t aws deploy"
    echo "  $0 -e staging -t kubernetes deploy"
}

# Parse command line arguments
ENVIRONMENT="local"
DEPLOYMENT_TARGET="local"
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -t|--target)
            DEPLOYMENT_TARGET="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            COMMAND="$1"
            shift
            ;;
    esac
done

# Enable verbose mode if requested
if [ "$VERBOSE" = true ]; then
    set -x
fi

# Main execution
log_info "Starting GPUOptimizer deployment..."
log_info "Environment: $ENVIRONMENT"
log_info "Target: $DEPLOYMENT_TARGET"

check_dependencies
setup_environment

case $COMMAND in
    "build")
        build_application
        ;;
    "deploy")
        build_application
        case $DEPLOYMENT_TARGET in
            "local")
                deploy_local
                ;;
            "aws")
                deploy_aws
                ;;
            "kubernetes")
                deploy_kubernetes
                ;;
            *)
                log_error "Unknown deployment target: $DEPLOYMENT_TARGET"
                exit 1
                ;;
        esac
        setup_monitoring
        setup_ssl
        ;;
    "test")
        run_tests
        ;;
    "backup")
        backup_database
        ;;
    "monitor")
        setup_monitoring
        ;;
    "ssl")
        setup_ssl
        ;;
    "help"|"")
        show_help
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac

log_success "Deployment script completed successfully!"
