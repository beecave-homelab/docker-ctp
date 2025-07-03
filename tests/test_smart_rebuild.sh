#!/bin/bash

# Test script to demonstrate smart rebuild optimization
set -euo pipefail

# Source the main script to get the functions
source ./docker-ctp.sh

# Override main function to skip login/push for testing
test_smart_rebuild() {
    IMAGE_NAME="test-smart-rebuild"
    TAG="v1.0"
    DOCKERFILE_DIR="."
    FORCE_REBUILD=false
    LOG_LEVEL="verbose"
    DRY_RUN=false
    
    echo "=== TEST 1: Smart Rebuild Optimization (Image Exists) ==="
    echo "Testing with existing image: $IMAGE_NAME:$TAG"
    
    # Test the smart rebuild logic directly
    build_docker_image
    
    echo ""
    echo "=== TEST 2: Force Rebuild (Override Optimization) ==="
    echo "Testing with --force-rebuild flag enabled"
    FORCE_REBUILD=true
    
    build_docker_image
}

# Initialize required variables
init_variables
DOCKER_USERNAME="testuser"
GITHUB_USERNAME="testuser"

# Run the test
test_smart_rebuild 