#!/bin/bash

# Adobe Hackathon Challenge 1b - Build and Run Script
# Complete setup and deployment script

set -e  # Exit on any error

echo "🚀 Adobe Hackathon Challenge 1b - Build and Run"
echo "================================================"

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

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is available and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose not found, using docker compose (newer version)"
        DOCKER_COMPOSE="docker compose"
    else
        DOCKER_COMPOSE="docker-compose"
    fi
    print_success "Docker Compose command: $DOCKER_COMPOSE"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p input
    mkdir -p output
    mkdir -p cache
    mkdir -p logs
    mkdir -p web
    
    print_success "Directories created"
}

# Build Docker image
build_image() {
    print_status "Building Docker image..."
    
    if docker build -t adobe-hackathon-1b .; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Run with Docker Compose
run_with_compose() {
    print_status "Starting services with Docker Compose..."
    
    if $DOCKER_COMPOSE up -d; then
        print_success "Services started successfully"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Run with Docker directly
run_with_docker() {
    print_status "Starting container with Docker..."
    
    if docker run -d \
        --name adobe-hackathon-1b \
        -p 8000:8000 \
        -v "$(pwd)/input:/app/input" \
        -v "$(pwd)/output:/app/output" \
        -v "$(pwd)/cache:/app/cache" \
        -v "$(pwd)/logs:/app/logs" \
        --memory=4g \
        --cpus=2.0 \
        adobe-hackathon-1b; then
        print_success "Container started successfully"
    else
        print_error "Failed to start container"
        exit 1
    fi
}

# Wait for service to be ready
wait_for_service() {
    print_status "Waiting for service to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            print_success "Service is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - Service not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Service failed to start within expected time"
    return 1
}

# Show service information
show_service_info() {
    echo ""
    echo "🎉 Adobe Hackathon Challenge 1b is now running!"
    echo "================================================"
    echo ""
    echo "📊 Service Information:"
    echo "  • API Endpoint: http://localhost:8000"
    echo "  • Health Check: http://localhost:8000/health"
    echo "  • Web Interface: http://localhost:8080"
    echo ""
    echo "📁 Directory Structure:"
    echo "  • Input files: ./input/"
    echo "  • Output files: ./output/"
    echo "  • Cache: ./cache/"
    echo "  • Logs: ./logs/"
    echo ""
    echo "🔧 Quick Commands:"
    echo "  • Check health: curl http://localhost:8000/health"
    echo "  • List personas: curl http://localhost:8000/personas"
    echo "  • Process PDF: curl -X POST http://localhost:8000/process-single -F 'file=@your_file.pdf'"
    echo ""
    echo "📖 Documentation:"
    echo "  • See README.md for detailed usage instructions"
    echo "  • Check logs: docker logs adobe-hackathon-1b"
    echo ""
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    if [ -f "scripts/run_tests.sh" ]; then
        chmod +x scripts/run_tests.sh
        if scripts/run_tests.sh; then
            print_success "Tests passed"
        else
            print_warning "Some tests failed"
        fi
    else
        print_warning "Test script not found, skipping tests"
    fi
}

# Main execution
main() {
    echo ""
    print_status "Starting Adobe Hackathon Challenge 1b deployment..."
    echo ""
    
    # Pre-flight checks
    check_docker
    check_docker_compose
    create_directories
    
    # Build and run
    build_image
    
    # Choose deployment method
    if [ -f "docker-compose.yml" ]; then
        print_status "Using Docker Compose for deployment"
        run_with_compose
    else
        print_status "Using Docker directly for deployment"
        run_with_docker
    fi
    
    # Wait for service
    if wait_for_service; then
        show_service_info
        run_tests
    else
        print_error "Deployment failed"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "build")
        print_status "Building only..."
        check_docker
        build_image
        print_success "Build completed"
        ;;
    "run")
        print_status "Running only..."
        check_docker
        check_docker_compose
        if [ -f "docker-compose.yml" ]; then
            run_with_compose
        else
            run_with_docker
        fi
        wait_for_service
        show_service_info
        ;;
    "test")
        print_status "Running tests only..."
        run_tests
        ;;
    "stop")
        print_status "Stopping services..."
        if [ -f "docker-compose.yml" ]; then
            $DOCKER_COMPOSE down
        else
            docker stop adobe-hackathon-1b 2>/dev/null || true
            docker rm adobe-hackathon-1b 2>/dev/null || true
        fi
        print_success "Services stopped"
        ;;
    "clean")
        print_status "Cleaning up..."
        if [ -f "docker-compose.yml" ]; then
            $DOCKER_COMPOSE down -v
        else
            docker stop adobe-hackathon-1b 2>/dev/null || true
            docker rm adobe-hackathon-1b 2>/dev/null || true
        fi
        docker rmi adobe-hackathon-1b 2>/dev/null || true
        print_success "Cleanup completed"
        ;;
    "help"|"-h"|"--help")
        echo "Adobe Hackathon Challenge 1b - Build and Run Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  build    Build Docker image only"
        echo "  run      Run services only (assumes image is built)"
        echo "  test     Run tests only"
        echo "  stop     Stop running services"
        echo "  clean    Stop services and remove images"
        echo "  help     Show this help message"
        echo ""
        echo "Default: Build and run complete deployment"
        ;;
    *)
        main
        ;;
esac 