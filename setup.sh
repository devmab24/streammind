#!/bin/bash

# StreamMind Setup Script
echo "🚀 StreamMind Setup Script"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python 3.9+ is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 9 ]; then
            print_status "Python $PYTHON_VERSION found"
            return 0
        else
            print_error "Python 3.9+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Check if Docker is installed
check_docker() {
    if command -v docker &> /dev/null; then
        print_status "Docker found"
        return 0
    else
        print_warning "Docker not found - will use local Redis"
        return 1
    fi
}

# Create project structure
create_structure() {
    print_info "Creating project structure..."
    
    # Create directories
    mkdir -p app/{models,services,api,utils,static/{js,css},templates}
    mkdir -p data/{sample_content,embeddings,logs}
    mkdir -p tests
    mkdir -p docs
    mkdir -p scripts
    mkdir -p config

    # Create __init__.py files
    touch app/__init__.py
    touch app/models/__init__.py
    touch app/services/__init__.py
    touch app/api/__init__.py
    touch app/utils/__init__.py
    touch tests/__init__.py

    print_status "Project structure created"
}

# Setup Python virtual environment
setup_venv() {
    print_info "Setting up Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_status "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_status "Pip upgraded"
}

# Install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found!"
        print_info "Please ensure all project files are in place"
        exit 1
    fi
    
    # Install requirements
    pip install -r requirements.txt
    print_status "Dependencies installed"
}

# Setup environment file
setup_env() {
    print_info "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.template" ]; then
            cp .env.template .env
            print_status "Environment file created from template"
            print_warning "Please edit .env file with your API keys if needed"
        else
            # Create basic .env file
            cat > .env << EOF
# StreamMind Environment Configuration
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
DEMO_MODE=true
MOCK_DATA=true
EOF
            print_status "Basic environment file created"
        fi
    else
        print_warning "Environment file already exists"
    fi
}

# Start Redis (Docker or local)
start_redis() {
    print_info "Starting Redis..."
    
    if command -v docker &> /dev/null && [ -f "docker-compose.yml" ]; then
        print_info "Starting Redis with Docker..."
        docker-compose up -d redis
        
        # Wait for Redis to be ready
        print_info "Waiting for Redis to be ready..."
        for i in {1..30}; do
            if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
                print_status "Redis is ready"
                return 0
            fi
            sleep 1
        done
        print_error "Redis failed to start"
        return 1
    else
        print_warning "Docker not available or docker-compose.yml missing"
        print_info "Please ensure Redis is running locally on port 6379"
        return 0
    fi
}

# Test the application
test_app() {
    print_info "Testing application..."
    
    # Activate venv if not already active
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    # Run a simple test
    python3 -c "
import sys
sys.path.append('.')
try:
    from app.main import app
    print('✅ Application imports successfully')
except Exception as e:
    print(f'❌ Application import failed: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_status "Application test passed"
        return 0
    else
        print_error "Application test failed"
        return 1
    fi
}

# Main setup function
main() {
    echo
    print_info "Starting StreamMind setup..."
    echo
    
    # Check prerequisites
    if ! check_python; then
        print_error "Python 3.9+ is required. Please install it first."
        exit 1
    fi
    
    check_docker
    
    # Setup steps
    create_structure
    setup_venv
    install_dependencies
    setup_env
    start_redis
    
    # Test the application
    if test_app; then
        echo
        print_status "🎉 StreamMind setup completed successfully!"
        echo
        print_info "Next steps:"
        echo "  1. Edit .env file with your API keys (optional for demo)"
        echo "  2. Run: source venv/bin/activate"
        echo "  3. Run: python -m uvicorn app.main:app --reload"
        echo "  4. Open: http://localhost:8000"
        echo
        print_info "For production deployment:"
        echo "  - Use: docker-compose up -d"
        echo "  - Or deploy to cloud platform"
        echo
    else
        print_error "Setup completed with errors. Please check the logs above."
        exit 1
    fi
}

# Run main function
main "$@"