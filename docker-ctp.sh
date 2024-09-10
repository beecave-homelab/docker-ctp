#!/bin/bash
set -euo pipefail

# Script Description: This script builds, tags, and pushes a Docker image to Docker Hub or GitHub Container Registry.
# Author: elvee
# Version: 0.2.9
# License: MIT
# Creation Date: 29-07-2024
# Last Modified: 10-09-2024
# Usage: docker-ctp.sh [OPTIONS]

# Constants (These will act as defaults if no .env file or arguments are provided)
DEFAULT_DOCKER_USERNAME="${USER}"
DEFAULT_GITHUB_USERNAME="${USER}"
DEFAULT_IMAGE_NAME="basename ${PWD}"
DEFAULT_DOCKERFILE_DIR="."
DEFAULT_REGISTRY="docker"  # Options: "docker" or "github"
USE_CACHE=true  # Default to using cache for the build

# Default repositories if not provided in .env or command line
DEFAULT_DOCKERHUB_REPO="dockerhub-user/static-repository-name"
DEFAULT_GITHUB_REPO="github-user/static-repository-name"

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
    # (omitted for brevity)
    "
}

# Function to display help
show_help() {
    echo "
Usage: ${0##*/} [OPTIONS]

Options:
  -u, --username         Docker Hub or GitHub username (default: from .env or Docker Hub username: $DEFAULT_DOCKER_USERNAME, GitHub username: $DEFAULT_GITHUB_USERNAME)
  -i, --image-name       Docker image name (default: from .env or dynamically set based on directory name if DYNAMIC_VALUES=true)
  -t, --image-tag        Docker image tag (default: 'latest' for Docker, 'main' for GitHub)
  -d, --dockerfile-dir   Path to Dockerfile folder (default: from .env or $DEFAULT_DOCKERFILE_DIR)
  -g, --registry         Target registry ("docker" for Docker Hub, "github" for GitHub Container Registry; default: from .env or $DEFAULT_REGISTRY)
  --no-cache             Disable Docker cache and force a clean build (default: use cache)
  -h, --help             Display this help message

Environment File:
  The script will automatically look for an .env file in ~/.config/docker-ctp/.env to load default values for the required options.
  The .env file should contain the following variables:
    - DOCKER_USERNAME: Your Docker Hub username
    - GITHUB_USERNAME: Your GitHub username
    - DOCKERHUB_REPO: DockerHub repository (if DYNAMIC_VALUES=false)
    - GITHUB_REPO: GitHub repository (if DYNAMIC_VALUES=false)
    - IMAGE_NAME: The name of the Docker image (if DYNAMIC_VALUES=false)
    - DYNAMIC_VALUES: Set to "true" to dynamically set repository names and image name based on the current directory
    - DOCKERFILE_DIR: Path to Dockerfile directory
    - REGISTRY: Target registry ("docker" or "github")
    - DOCKERHUB_DEFAULT_TAG: Default DockerHub tag (default: latest)
    - GITHUB_DEFAULT_TAG: Default GitHub tag (default: main)

Examples:
  # Push to Docker Hub (default tag: latest):
  ${0##*/} -g docker -u your-docker-username -r your-dockerhub-username/repo -i image -d /path/to/dockerfile

  # Push to GitHub Container Registry (default tag: main):
  ${0##*/} -g github -u your-github-username -r your-org/repo -i image -d /path/to/dockerfile

  # Force a clean build with no cache:
  ${0##*/} --no-cache -g docker -u your-docker-username -r your-repo -i image -d /path/to/dockerfile
"
}

# Function for error handling
error_exit() {
    echo "Error: $1" >&2
    exit 1
}

# Function to check and load the .env file
load_env_file() {
    ENV_FILE="$HOME/.config/docker-ctp/.env"
    if [[ -f "$ENV_FILE" ]]; then
        echo "Loading configuration from $ENV_FILE"
        # shellcheck source=/dev/null
        source "$ENV_FILE"
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
        error_exit "Required values are missing. Ensure that they are provided via the .env file or arguments."
    fi
}

# Function to dynamically set repository names and image name based on directory if DYNAMIC_VALUES=true
set_dynamic_values() {
    if [[ "${DYNAMIC_VALUES:-false}" == "true" ]]; then
        IMAGE_NAME="$(basename "$PWD")"
        DOCKERHUB_REPO="${DOCKER_USERNAME}/$IMAGE_NAME"
        GITHUB_REPO="${GITHUB_USERNAME}/$IMAGE_NAME"
        echo "Dynamic values enabled. Using IMAGE_NAME: $IMAGE_NAME, DOCKERHUB_REPO: $DOCKERHUB_REPO, GITHUB_REPO: $GITHUB_REPO"
    fi
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

    # Set dynamic values if DYNAMIC_VALUES=true
    set_dynamic_values

    # Default values from .env or fallback to constants
    USERNAME=${DOCKER_USERNAME:-$DEFAULT_DOCKER_USERNAME}
    IMAGE_NAME=${IMAGE_NAME:-$DEFAULT_IMAGE_NAME}
    DOCKERFILE_DIR=${DOCKERFILE_DIR:-$DEFAULT_DOCKERFILE_DIR}
    REGISTRY=${REGISTRY:-$DEFAULT_REGISTRY}
    DOCKERHUB_REPO=${DOCKERHUB_REPO:-$DEFAULT_DOCKERHUB_REPO}
    GITHUB_REPO=${GITHUB_REPO:-$DEFAULT_GITHUB_REPO}

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