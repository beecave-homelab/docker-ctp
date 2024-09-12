#!/bin/bash
set -euo pipefail

# Script Description: This script builds, tags, and pushes a Docker image to Docker Hub or GitHub Container Registry.
# Author: elvee
# Version: 0.3.1
# License: MIT
# Creation Date: 29-07-2024
# Last Modified: 11-09-2024
# Usage: docker-ctp.sh [OPTIONS]

# Constants (These will act as defaults if no .env file or arguments are provided)
DEFAULT_DOCKER_USERNAME="${USER}"
DEFAULT_GITHUB_USERNAME="${USER}"
DEFAULT_IMAGE_NAME="$(basename "$PWD")"
DEFAULT_DOCKERFILE_DIR="."
DEFAULT_REGISTRY="docker"  # Options: "docker" or "github"
USE_CACHE=true  # Default to using cache for the build

# Default tags if not provided in .env or command line
DEFAULT_DOCKERHUB_TAG="latest"
DEFAULT_GITHUB_TAG="main"

# Function to dynamically set the default tag based on the selected registry
set_default_tag() {
    if [[ "$REGISTRY" == "docker" ]]; then
        TAG=${DOCKERHUB_DEFAULT_TAG:-$DEFAULT_DOCKERHUB_TAG}
    elif [[ "$REGISTRY" == "github" ]]; then
        TAG=${GITHUB_DEFAULT_TAG:-$DEFAULT_GITHUB_TAG}
    else
        error_exit "Unknown registry: $REGISTRY"
    fi
}

# ASCII Art
print_ascii_art() {
    echo "
 
██████   ██████   ██████ ██   ██ ███████ ██████  
██   ██ ██    ██ ██      ██  ██  ██      ██   ██ 
██   ██ ██    ██ ██      █████   █████   ██████  
██   ██ ██    ██ ██      ██  ██  ██      ██   ██ 
██████   ██████   ██████ ██   ██ ███████ ██   ██ 
                                                 
                                                 
             ██████ ████████ ██████                  
            ██         ██    ██   ██                 
            ██         ██    ██████                  
            ██         ██    ██                      
             ██████    ██    ██                      
                                                 
                                                 
    "
}

# Function to display help with syntax highlighting
# Display the usage and examples using dynamic and .env file values with colors

show_help() {
    echo -e "
\033[33mUsage:\033[0m ${0##*/} [OPTIONS]

\033[33mOptions:\033[0m
  \033[33m-u, --username\033[0m         Docker Hub or GitHub username (default: Docker Hub: $DOCKER_USERNAME, GitHub: $GITHUB_USERNAME)
  \033[33m-i, --image-name\033[0m       Docker image name (default: $IMAGE_NAME)
  \033[33m-t, --image-tag\033[0m        Docker image tag (default: 'latest' for Docker, 'main' for GitHub)
  \033[33m-d, --dockerfile-dir\033[0m   Path to Dockerfile folder (default: $DOCKERFILE_DIR)
  \033[33m-g, --registry\033[0m         Target registry (default: $REGISTRY; 'docker' for Docker Hub, 'github' for GitHub)
  \033[33m--no-cache\033[0m             Disable Docker cache and force a clean build (default: use cache)
  \033[33m-h, --help\033[0m             Display this help message

\033[33mExamples:\033[0m

  \033[32m# Example: Push to Docker Hub with default values (tag: latest)\033[0m
  ${0##*/} -g docker -u $DOCKER_USERNAME -i $IMAGE_NAME -d $DOCKERFILE_DIR
  
  \033[32m# Example: Push to GitHub Container Registry with default values (tag: main)\033[0m
  ${0##*/} -g github -u $GITHUB_USERNAME -i $IMAGE_NAME -d $DOCKERFILE_DIR

  \033[32m# Example: Force a clean build without cache and push to Docker Hub\033[0m
  ${0##*/} --no-cache -g docker -u $DOCKER_USERNAME -i $IMAGE_NAME -d $DOCKERFILE_DIR

  \033[32m# Example: Push to Docker Hub with a custom tag 'v1.0.0'\033[0m
  ${0##*/} -g docker -u $DOCKER_USERNAME -i $IMAGE_NAME -t v1.0.0 -d $DOCKERFILE_DIR

  \033[32m# Example: Push to GitHub Container Registry with a custom tag 'v1.0.0'\033[0m
  ${0##*/} -g github -u $GITHUB_USERNAME -i $IMAGE_NAME -t v1.0.0 -d $DOCKERFILE_DIR
"
}

# Function for error handling
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Function to check and load the .env file
load_env_file() {
    # Check if the .env file exists in the home directory
    ENV_FILE="$HOME/.config/docker-ctp/.env"
    if [[ -f "$ENV_FILE" ]]; then
        echo "Loading configuration from $ENV_FILE (home directory)"
        # shellcheck source=/dev/null
        source "$ENV_FILE"
    else
        echo "No .env file found in current directory or home directory"
    fi
}

# Function to parse command-line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -u|--username)
                USERNAME="$2"
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
            --no-cache)
                USE_CACHE=false
                shift 1
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

# Function to ensure required values are provided
validate_arguments() {
    if [[ -z "$USERNAME" || -z "$IMAGE_NAME" || -z "$DOCKERFILE_DIR" || -z "$REGISTRY" ]]; then
        error_exit "Required values are missing. Ensure that they are provided via arguments."
    fi
}

# Function to dynamically set repository names based on directory
set_dynamic_repos() {
    IMAGE_NAME="$(basename "$PWD")"
    DOCKERHUB_REPO="${DOCKER_USERNAME}/$IMAGE_NAME"
    GITHUB_REPO="${GITHUB_USERNAME}/$IMAGE_NAME"
    echo "Using IMAGE_NAME: $IMAGE_NAME, DOCKERHUB_REPO: $DOCKERHUB_REPO, GITHUB_REPO: $GITHUB_REPO"
}

# Function to prompt for a Personal Access Token (PAT)
prompt_for_pat() {
    if [[ "$REGISTRY" == "docker" ]]; then
        echo "Please enter your Docker Hub Personal Access Token (PAT):"
    elif [[ "$REGISTRY" == "github" ]]; then
        echo "Please enter your GitHub Personal Access Token (PAT):"
    else
        error_exit "Unknown registry: $REGISTRY"
    fi
    read -s PAT
}

# Function to login to the selected registry
login_to_registry() {
    if [[ "$REGISTRY" == "docker" ]]; then
        echo $PAT | docker login -u $USERNAME --password-stdin
    elif [[ "$REGISTRY" == "github" ]]; then
        echo $PAT | docker login ghcr.io -u $USERNAME --password-stdin
    fi

    if [[ $? -ne 0 ]]; then
        error_exit "Failed to login to $REGISTRY registry"
    fi
}

# Function to build the Docker image
build_docker_image() {
    if $USE_CACHE; then
        docker build -t $IMAGE_NAME:$TAG $DOCKERFILE_DIR
    else
        docker build --no-cache -t $IMAGE_NAME:$TAG $DOCKERFILE_DIR
    fi

    if [[ $? -ne 0 ]]; then
        error_exit "Failed to build Docker image"
    fi
}

# Function to tag the Docker image
tag_docker_image() {
    if [[ "$REGISTRY" == "docker" ]]; then
        docker tag $IMAGE_NAME:$TAG $DOCKERHUB_REPO:$TAG
    elif [[ "$REGISTRY" == "github" ]]; then
        docker tag $IMAGE_NAME:$TAG ghcr.io/$GITHUB_REPO:$TAG
    fi
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to tag Docker image"
    fi
}

# Function to push the Docker image
push_docker_image() {
    if [[ "$REGISTRY" == "docker" ]]; then
        docker push $DOCKERHUB_REPO:$TAG
    elif [[ "$REGISTRY" == "github" ]]; then
        docker push ghcr.io/$GITHUB_REPO:$TAG
    fi
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to push Docker image to $REGISTRY"
    fi
}

# Main function to encapsulate script logic
main() {
    # Load environment variables if .env exists
    load_env_file

    # Set dynamic values for repositories and image name based on the current directory
    set_dynamic_repos

    # Default values from .env or fallback to constants
    USERNAME=${DOCKER_USERNAME:-$DEFAULT_DOCKER_USERNAME}
    DOCKERFILE_DIR=${DOCKERFILE_DIR:-$DEFAULT_DOCKERFILE_DIR}
    REGISTRY=${REGISTRY:-$DEFAULT_REGISTRY}

    # Parse command-line options
    parse_arguments "$@"

    # Ensure all necessary arguments are provided
    validate_arguments

    # Dynamically set the default tag based on the registry
    set_default_tag

    # If no tag is provided, use the dynamically determined default
    TAG=${TAG:-$DEFAULT_TAG}

    # Main execution
    prompt_for_pat
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