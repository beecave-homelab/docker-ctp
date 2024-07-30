#!/bin/bash
set -euo pipefail

# Script Description: This script builds, tags, and pushes a Docker image to the GitHub Container Registry.
# Author: elvee
# Version: 0.1.0
# License: MIT
# Creation Date: 29-07-2024
# Last Modified: 29-07-2024
# Usage: docker-ctp.sh [OPTIONS]

# Constants
DEFAULT_GITHUB_USERNAME="admin@example.com"
DEFAULT_REPO_NAME="github_organization/repo_name"
DEFAULT_IMAGE_NAME=${basename "$PWD"}
DEFAULT_TAG="latest"
DEFAULT_DOCKERFILE_DIR="."

# ASCII Art
print_ascii_art() {
    echo "

 ██████╗██████╗ ███████╗ █████╗ ████████╗███████╗   
██╔════╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔════╝   
██║     ██████╔╝█████╗  ███████║   ██║   █████╗     
██║     ██╔══██╗██╔══╝  ██╔══██║   ██║   ██╔══╝     
╚██████╗██║  ██║███████╗██║  ██║   ██║   ███████╗   
 ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝   
                                                    
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
                                                    
  Create, tag and publish Docker images to ghrc.io
    "
}

# Function to display help
show_help() {
    echo "
Usage: ${0##*/} [OPTIONS]

Options:
  -u, --github-username   GitHub username (default: $DEFAULT_GITHUB_USERNAME)
  -r, --repository-name   Repository name (default: $DEFAULT_REPO_NAME)
  -i, --image-name        Docker image name (default: $DEFAULT_IMAGE_NAME)
  -t, --image-tag         Docker image tag (default: $DEFAULT_TAG)
  -d, --dockerfile-folder Path to Dockerfile folder (default: $DEFAULT_DOCKERFILE_DIR)
  -h, --help              Display this help message

Examples:
  ${0##*/} -u user -r repo/image -i image -t tag -d /path/to/dockerfile
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
            -u|--github-username)
                GITHUB_USERNAME="$2"
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
            -d|--dockerfile-folder)
                DOCKERFILE_DIR="$2"
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

# Function to prompt for GitHub token
prompt_for_token() {
    echo "Please enter your GitHub Personal Access Token (PAT):"
    read -s GITHUB_TOKEN
}

# Function to login to GitHub Container Registry
login_to_github_registry() {
    echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to login to GitHub Container Registry"
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
    docker tag $IMAGE_NAME:$TAG ghcr.io/$REPO_NAME:$TAG
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to tag Docker image"
    fi
}

# Function to push the Docker image
push_docker_image() {
    docker push ghcr.io/$REPO_NAME:$TAG
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to push Docker image"
    fi
}

# Main function to encapsulate script logic
main() {
    # Default values
    GITHUB_USERNAME=$DEFAULT_GITHUB_USERNAME
    REPO_NAME=$DEFAULT_REPO_NAME
    IMAGE_NAME=$DEFAULT_IMAGE_NAME
    TAG=$DEFAULT_TAG
    DOCKERFILE_DIR=$DEFAULT_DOCKERFILE_DIR

    # Parse command-line options
    parse_arguments "$@"
    prompt_for_token
    login_to_github_registry
    build_docker_image
    tag_docker_image
    push_docker_image

    echo "Docker image successfully pushed to GitHub Packages"
}

# Print ASCII Art
print_ascii_art

# Execute the main function
main "$@"