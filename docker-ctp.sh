#!/bin/bash
set -euo pipefail

# Script Description: This script builds, tags, and pushes a Docker image to Docker Hub or GitHub Container Registry.
# Author: elvee
# Version: 0.2.0
# License: MIT
# Creation Date: 29-07-2024
# Last Modified: 28-08-2024
# Usage: docker-ctp.sh [OPTIONS]

# Constants
DEFAULT_DOCKER_USERNAME="your-docker-username"
DEFAULT_GITHUB_USERNAME="admin@example.com"
DEFAULT_REPO_NAME="repo_name"
DEFAULT_IMAGE_NAME=$(basename "$PWD")
DEFAULT_TAG="latest"
DEFAULT_DOCKERFILE_DIR="."
DEFAULT_REGISTRY="docker"  # Options: "docker" or "github"

# ASCII Art
print_ascii_art() {
    echo "

 ██████╗██████╗ ███████╗ █████╗ ████████╗███████╗   
██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔════╝   
██║     ██████╔╝█████╗  ███████║   ██║   █████╗     
██║     ██╔══██╗██╔══╝  ██╔══██║   ██║   ██╔══╝     
╚██████╗██║  ██║███████╗██║  ██║   ██║   ███████╗   
 ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚══════╝   
                                                    
           ████████╗ █████╗  ██████╗               
           ╚══██╔══╝██╔══██╗██╔════╝               
              ██║   ███████║██║  ███╗              
              ██║   ██╔══██║██║   ██║              
              ██║   ██║  ██║╚██████╔╝              
              ╚═╝   ╚═╝  ╚═╝ ╚═════╝               
                                                    
██████╗ ██╗   ██╗██████╗ ██╗     ██╗███████╗██╗  ██╗
██╔══██╗██║   ██║██╔══██╗██║     ██║██╔════╝██║  ██║
██████╔╝██║   ██║██████╔╝██║     ██║███████╗███████║
██╔═══╝ ██║   ██║██╔══██╗██║     ██║╚════██║██╔══██║
██║     ╚██████╔╝██████╔╝███████╗██║███████║██║  ██║
╚═╝      ╚═════╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚═╝  ╚═╝
                                                    
  Create, tag and publish Docker images to Docker Hub or GitHub Container Registry
    "
}

# Function to display help
show_help() {
    echo "
Usage: ${0##*/} [OPTIONS]

Options:
  -u, --username         Docker Hub or GitHub username (default: Docker Hub username: $DEFAULT_DOCKER_USERNAME, GitHub username: $DEFAULT_GITHUB_USERNAME)
  -r, --repository-name  Repository name (default: $DEFAULT_REPO_NAME)
  -i, --image-name       Docker image name (default: $DEFAULT_IMAGE_NAME)
  -t, --image-tag        Docker image tag (default: $DEFAULT_TAG)
  -d, --dockerfile-dir   Path to Dockerfile folder (default: $DEFAULT_DOCKERFILE_DIR)
  -g, --registry         Target registry ("docker" for Docker Hub, "github" for GitHub Container Registry; default: $DEFAULT_REGISTRY)
  -h, --help             Display this help message

Examples:
  ${0##*/} -g docker -u your-docker-username -r your-repo/image -i image -t tag -d /path/to/dockerfile
  ${0##*/} -g github -u your-github-username -r your-org/repo/image -i image -t tag -d /path/to/dockerfile
"
}

# Function for error handling
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Function to parse command-line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--username)
                USERNAME="$2"
                shift 2
                ;;
            -r|--repository-name)
                REPO_NAME="$2"
                shift 2
                ;;
            -i|--image-name)
                IMAGE_NAME="$2"
                shift 2
                ;;
            -t|--image-tag)
                TAG="$2"
                shift 2
                ;;
            -d|--dockerfile-dir)
                DOCKERFILE_DIR="$2"
                shift 2
                ;;
            -g|--registry)
                REGISTRY="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error_exit "Unknown option: $1"
                ;;
        esac
    done
}

# Function to prompt for a password or token
prompt_for_credentials() {
    if [[ "$REGISTRY" == "docker" ]]; then
        echo "Please enter your Docker Hub password:"
        read -s CREDENTIALS
    elif [[ "$REGISTRY" == "github" ]]; then
        echo "Please enter your GitHub Personal Access Token (PAT):"
        read -s CREDENTIALS
    else
        error_exit "Unknown registry: $REGISTRY"
    fi
}

# Function to login to the selected registry
login_to_registry() {
    if [[ "$REGISTRY" == "docker" ]]; then
        echo $CREDENTIALS | docker login -u $USERNAME --password-stdin
    elif [[ "$REGISTRY" == "github" ]]; then
        echo $CREDENTIALS | docker login ghcr.io -u $USERNAME --password-stdin
    fi

    if [[ $? -ne 0 ]]; then
        error_exit "Failed to login to $REGISTRY registry"
    fi
}

# Function to build the Docker image
build_docker_image() {
    docker build -t $IMAGE_NAME:$TAG $DOCKERFILE_DIR
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to build Docker image"
    fi
}

# Function to tag the Docker image
tag_docker_image() {
    if [[ "$REGISTRY" == "docker" ]]; then
        docker tag $IMAGE_NAME:$TAG $USERNAME/$REPO_NAME:$TAG
    elif [[ "$REGISTRY" == "github" ]]; then
        docker tag $IMAGE_NAME:$TAG ghcr.io/$REPO_NAME:$TAG
    fi
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to tag Docker image"
    fi
}

# Function to push the Docker image
push_docker_image() {
    if [[ "$REGISTRY" == "docker" ]]; then
        docker push $USERNAME/$REPO_NAME:$TAG
    elif [[ "$REGISTRY" == "github" ]]; then
        docker push ghcr.io/$REPO_NAME:$TAG
    fi
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to push Docker image to $REGISTRY"
    fi
}

# Main function to encapsulate script logic
main() {
    # Default values
    USERNAME=$DEFAULT_DOCKER_USERNAME
    REPO_NAME=$DEFAULT_REPO_NAME
    IMAGE_NAME=$DEFAULT_IMAGE_NAME
    TAG=$DEFAULT_TAG
    DOCKERFILE_DIR=$DEFAULT_DOCKERFILE_DIR
    REGISTRY=$DEFAULT_REGISTRY

    # Parse command-line options
    parse_arguments "$@"
    prompt_for_credentials
    login_to_registry
    build_docker_image
    tag_docker_image
    push_docker_image

    echo "Docker image successfully pushed to $REGISTRY registry"
}

# Print ASCII Art
print_ascii_art

# Execute the main function
main "$@"