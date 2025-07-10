#!/bin/bash

# Lataupe Bunker Tech - Startup Script
# This script helps manage the Flask application

set -e

PROJECT_DIR="/home/kevin/Documents/Github/lataupe-bunker-tech"
VENV_DIR="$PROJECT_DIR/.venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_info() {
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

# Check if we're in the right directory
if [ ! -f "$PROJECT_DIR/main.py" ]; then
    print_error "main.py not found in $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    print_error "Virtual environment not found at $VENV_DIR"
    print_info "Creating virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    print_warning "Dependencies not found. Installing..."
    pip install -r requirements.txt
    print_success "Dependencies installed"
fi

# Function to start the application
start_app() {
    print_info "Starting Lataupe Bunker Tech..."
    print_info "🏠 Bunker Tech will be available at: http://localhost:5001"
    print_info "Press Ctrl+C to stop the server"
    python main.py
}

# Function to test the application
test_app() {
    print_info "Testing application components..."
    
    # Test imports
    if python -c "from src.main import app; print('✅ Flask app import successful')"; then
        print_success "Application imports working"
    else
        print_error "Application import failed"
        return 1
    fi
    
    # Test database
    if python -c "from src.main import app; from src.models.user import db; print('✅ Database models import successful')"; then
        print_success "Database models working"
    else
        print_error "Database models failed"
        return 1
    fi
    
    print_success "All tests passed!"
}

# Function to check status
check_status() {
    print_info "Checking application status..."
    
    if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
        print_success "Application is running at http://localhost:5001"
    else
        print_warning "Application is not running"
    fi
}

# Function to show help
show_help() {
    echo "Lataupe Bunker Tech - Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the application (default)"
    echo "  test      Test application components"
    echo "  status    Check if application is running"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Start the application"
    echo "  $0 start        # Start the application"
    echo "  $0 test         # Test the application"
    echo "  $0 status       # Check application status"
}

# Main script logic
case "${1:-start}" in
    "start")
        test_app && start_app
        ;;
    "test")
        test_app
        ;;
    "status")
        check_status
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
