#!/bin/bash

# MAOS - Multi-Agent Orchestration System
# Automated Setup Script

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${BLUE}"
cat << "EOF"
 __  __    _    ___  ____  
|  \/  |  / \  / _ \/ ___| 
| |\/| | / _ \| | | \___ \ 
| |  | |/ ___ \ |_| |___) |
|_|  |_/_/   \_\___/|____/ 
                           
Multi-Agent Orchestration System
EOF
echo -e "${NC}"

echo "Welcome to MAOS Setup!"
echo "======================"
echo ""

# Function to print colored messages
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    print_status "Detected OS: $OS"
}

# Check Python version
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 11 ]; then
            PYTHON_CMD="python3"
        else
            print_error "Python 3.11+ required, found Python $PYTHON_VERSION"
            echo "Please install Python 3.11 or higher:"
            echo "  - macOS: brew install python@3.11"
            echo "  - Ubuntu: sudo apt install python3.11"
            echo "  - Windows: choco install python311"
            exit 1
        fi
    else
        print_error "Python not found. Please install Python 3.11+"
        exit 1
    fi
    
    print_success "Python $(${PYTHON_CMD} --version 2>&1 | awk '{print $2}') found"
}

# Check Docker
check_docker() {
    print_status "Checking Docker..."
    
    if command -v docker &> /dev/null; then
        if docker ps &> /dev/null; then
            print_success "Docker is installed and running"
            return 0
        else
            print_warning "Docker is installed but not running"
            echo "Please start Docker Desktop or Docker daemon"
            read -p "Press Enter when Docker is running, or 's' to skip Redis setup: " response
            if [[ "$response" != "s" ]]; then
                if docker ps &> /dev/null; then
                    print_success "Docker is now running"
                    return 0
                else
                    print_error "Docker still not running"
                    return 1
                fi
            else
                return 1
            fi
        fi
    else
        print_warning "Docker not found"
        echo "Docker is recommended for Redis. Install from: https://docker.com"
        read -p "Continue without Docker? (y/n): " response
        if [[ "$response" != "y" ]]; then
            exit 1
        fi
        return 1
    fi
}

# Check Redis
check_redis() {
    print_status "Checking Redis..."
    
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping &> /dev/null; then
            print_success "Redis is running locally"
            USE_LOCAL_REDIS=true
            return 0
        fi
    fi
    
    if [ "$DOCKER_AVAILABLE" = true ]; then
        if docker ps | grep -q maos-redis; then
            print_success "Redis container is running"
            return 0
        else
            print_status "Starting Redis container..."
            docker run -d --name maos-redis -p 6379:6379 --restart unless-stopped redis:7-alpine
            sleep 2
            if docker ps | grep -q maos-redis; then
                print_success "Redis container started"
                return 0
            else
                print_error "Failed to start Redis container"
                return 1
            fi
        fi
    else
        print_error "Redis not available. Please install Redis or Docker"
        echo "  - macOS: brew install redis"
        echo "  - Ubuntu: sudo apt install redis-server"
        echo "  - Or install Docker: https://docker.com"
        exit 1
    fi
}

# Setup virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Delete and recreate? (y/n): " response
        if [[ "$response" == "y" ]]; then
            rm -rf venv
        else
            source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
            print_success "Using existing virtual environment"
            return
        fi
    fi
    
    ${PYTHON_CMD} -m venv venv
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    
    print_success "Virtual environment created and activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    pip install --quiet --upgrade pip
    pip install --quiet -r requirements.txt
    
    print_success "Dependencies installed"
}

# Install MAOS
install_maos() {
    print_status "Installing MAOS..."
    
    pip install --quiet -e .
    
    print_success "MAOS installed"
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ -f ".env" ]; then
        print_warning ".env file already exists"
        read -p "Overwrite with defaults? (y/n): " response
        if [[ "$response" != "y" ]]; then
            print_status "Keeping existing .env file"
            return
        fi
    fi
    
    cp .env.example .env
    
    # Generate secure keys
    if command -v openssl &> /dev/null; then
        JWT_SECRET=$(openssl rand -hex 32)
        API_SECRET=$(openssl rand -hex 32)
        
        # Update .env file based on OS
        if [[ "$OS" == "macos" ]]; then
            sed -i '' "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env
            sed -i '' "s/API_KEY_SECRET=.*/API_KEY_SECRET=$API_SECRET/" .env
        else
            sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$JWT_SECRET/" .env
            sed -i "s/API_KEY_SECRET=.*/API_KEY_SECRET=$API_SECRET/" .env
        fi
        
        print_success "Generated secure keys"
    else
        print_warning "OpenSSL not found, using default keys (not secure for production)"
    fi
    
    print_success "Environment configured"
}

# Run tests
run_tests() {
    print_status "Running installation tests..."
    
    if python scripts/test_maos.py; then
        print_success "All tests passed!"
        return 0
    else
        print_error "Some tests failed"
        print_warning "Check the error messages above for troubleshooting"
        return 1
    fi
}

# Main installation flow
main() {
    echo ""
    print_status "Starting MAOS installation..."
    echo ""
    
    # Check prerequisites
    detect_os
    check_python
    
    # Check Docker and Redis
    DOCKER_AVAILABLE=false
    if check_docker; then
        DOCKER_AVAILABLE=true
    fi
    
    check_redis
    
    # Setup Python environment
    setup_venv
    
    # Install MAOS
    install_dependencies
    install_maos
    setup_env
    
    echo ""
    print_status "Running verification tests..."
    echo ""
    
    # Run tests
    if run_tests; then
        echo ""
        echo "=========================================="
        print_success "MAOS Installation Complete! 🎉"
        echo "=========================================="
        echo ""
        echo "Next steps:"
        echo "  1. Activate virtual environment:"
        echo "     source venv/bin/activate"
        echo ""
        echo "  2. Start MAOS:"
        echo "     maos start"
        echo ""
        echo "  3. Create your first task:"
        echo "     maos task create 'Hello World'"
        echo ""
        echo "  4. Run the demo:"
        echo "     python scripts/demo.py"
        echo ""
        echo "Documentation: docs/quickstart.md"
        echo "=========================================="
    else
        echo ""
        print_warning "Installation completed with warnings"
        echo "Please check the test output above"
        echo ""
        echo "Common fixes:"
        echo "  - Ensure Redis is running"
        echo "  - Check Claude Code CLI is installed"
        echo "  - Review .env configuration"
        echo ""
        echo "For help, see: docs/troubleshooting.md"
    fi
}

# Handle script interruption
trap 'echo ""; print_error "Installation interrupted"; exit 1' INT

# Run main installation
main