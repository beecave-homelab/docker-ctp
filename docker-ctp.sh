#!/bin/bash
set -euo pipefail

# Script Description: This script builds, tags, and pushes a Docker image to Docker Hub or GitHub Container Registry.
# Author: elvee
# Version: 0.4.1
# License: MIT
# Creation Date: 29-07-2024
# Last Modified: 04-06-2025
# Usage: docker-ctp.sh [OPTIONS]

# Constants (These will act as defaults if no .env file or arguments are provided)
DEFAULT_DOCKER_USERNAME="${USER}"
DEFAULT_GITHUB_USERNAME="${USER}"
DEFAULT_IMAGE_NAME="$(basename "$PWD")"
DEFAULT_DOCKERFILE_DIR="."

# Options: "docker" or "github"
DEFAULT_REGISTRY="docker"
# Default to using cache for the build
USE_CACHE=true

# Phase 2: New variables for enhanced functionality
# Dry run mode - simulate operations without execution
DRY_RUN=false
# Logging levels: quiet, normal, verbose
LOG_LEVEL="normal"
# Enable cleanup on script exit
CLEANUP_ON_EXIT=true
# Array to track built images for cleanup
BUILT_IMAGES=()

# Phase 3: Smart rebuild optimization
# Force rebuild even if image already exists
FORCE_REBUILD=false

# Default tags if not provided in .env or command line
DEFAULT_DOCKERHUB_TAG="latest"
DEFAULT_GITHUB_TAG="main"

# Phase 2: Enhanced logging system
log_info() {
    if [[ "$LOG_LEVEL" != "quiet" ]]; then
        echo "ℹ️  [INFO] $1"
    fi
}

log_verbose() {
    if [[ "$LOG_LEVEL" == "verbose" ]]; then
        echo "🔍 [VERBOSE] $1"
    fi
}

log_success() {
    if [[ "$LOG_LEVEL" != "quiet" ]]; then
        echo "✅ [SUCCESS] $1"
    fi
}

log_warning() {
    if [[ "$LOG_LEVEL" != "quiet" ]]; then
        echo "⚠️  [WARNING] $1" >&2
    fi
}

log_error() {
    echo "❌ [ERROR] $1" >&2
}

log_dry_run() {
    if [[ "$DRY_RUN" == true ]]; then
        echo "🔸 [DRY-RUN] $1"
    fi
}

# Phase 2: Progress indicator functions
show_progress() {
    local message="$1"
    local duration="${2:-3}"
    
    if [[ "$LOG_LEVEL" != "quiet" && "$DRY_RUN" != true ]]; then
        echo -n "$message"
        for ((i=1; i<=duration; i++)); do
            echo -n "."
            sleep 0.5
        done
        echo " Done!"
    fi
}

# Phase 2: Cleanup function for graceful exit
cleanup_on_exit() {
    local exit_code=$?
    
    if [[ "$CLEANUP_ON_EXIT" == true && ${#BUILT_IMAGES[@]} -gt 0 ]]; then
        log_info "Cleaning up intermediate images..."
        for image in "${BUILT_IMAGES[@]}"; do
            if docker image inspect "$image" >/dev/null 2>&1; then
                log_verbose "Removing image: $image"
                if [[ "$DRY_RUN" != true ]]; then
                    docker rmi "$image" >/dev/null 2>&1 || log_warning "Failed to remove image: $image"
                else
                    log_dry_run "Would remove image: $image"
                fi
            fi
        done
        log_success "Cleanup completed"
    fi
    
    if [[ $exit_code -ne 0 ]]; then
        log_error "Script exited with error code: $exit_code"
    fi
    
    exit $exit_code
}

# Phase 2: Dependency checking
check_dependencies() {
    log_verbose "Checking system dependencies..."
    
    local missing_deps=()
    
    # Check for Docker
    if ! command -v docker >/dev/null 2>&1; then
        missing_deps+=("docker")
    else
        # Only check if Docker daemon is running in non-dry-run mode
        if [[ "$DRY_RUN" != true ]]; then
            if ! docker info >/dev/null 2>&1; then
                log_error "Docker is installed but the Docker daemon is not running"
                log_info "Please start Docker and try again"
                exit 1
            fi
            log_verbose "✓ Docker is installed and running"
        else
            log_verbose "✓ Docker is installed (daemon check skipped in dry-run mode)"
        fi
    fi
    
    # Check for essential system tools
    local required_tools=("realpath" "basename" "grep")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_deps+=("$tool")
        else
            log_verbose "✓ $tool is available"
        fi
    done
    
    # Report missing dependencies
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_info "Please install the missing dependencies and try again"
        exit 1
    fi
    
    log_success "All dependencies are satisfied"
}

# Function to dynamically set the default tag based on the selected registry
set_default_tag() {
    if [[ -z "${TAG:-}" ]]; then
        if [[ "$REGISTRY" == "docker" ]]; then
            TAG=$DEFAULT_DOCKERHUB_TAG
        elif [[ "$REGISTRY" == "github" ]]; then
            TAG=$DEFAULT_GITHUB_TAG
        else
            error_exit "Unknown registry: $REGISTRY"
        fi
    fi
}

# ASCII Art
print_ascii_art() {
    if [[ "$LOG_LEVEL" != "quiet" ]]; then
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
    fi
    if [[ "$DRY_RUN" == true && "$LOG_LEVEL" != "quiet" ]]; then
        echo "🔸 DRY RUN MODE - No actual operations will be performed"
    fi
}

# Function to initialize variables early (before help can be called)
init_variables() {
    local init_mode="${1:-normal}" # Parameter to control behavior, e.g., for silent help init

    # Load environment variables if .env exists first
    load_env_file "$init_mode"
    
    # Initialize core username variables with safe defaults BEFORE calling set_dynamic_repos
    DOCKER_USERNAME=${DOCKER_USERNAME:-$DEFAULT_DOCKER_USERNAME}
    GITHUB_USERNAME=${GITHUB_USERNAME:-$DEFAULT_GITHUB_USERNAME}
    IMAGE_NAME=${IMAGE_NAME:-$DEFAULT_IMAGE_NAME}
    DOCKERFILE_DIR=${DOCKERFILE_DIR:-$DEFAULT_DOCKERFILE_DIR}
    REGISTRY=${REGISTRY:-$DEFAULT_REGISTRY}
    
    # Now safe to set dynamic values for repositories 
    set_dynamic_repos
    
    # Initialize USERNAME to ensure it's set. It will be populated by CLI option or later logic.
    USERNAME=""
    # Initialize remaining variables with safe defaults for help display
    TAG=${TAG:-""}
    
    # Phase 2: Set up cleanup trap
    trap cleanup_on_exit EXIT INT TERM
}

# Function to handle early argument parsing for version and help
early_arg_parse() {
    # First pass: check for log level settings
    for arg in "$@"; do
        case "$arg" in
            --quiet)
                LOG_LEVEL="quiet"
                ;;
            --verbose)
                LOG_LEVEL="verbose"
                ;;
            --dry-run)
                DRY_RUN=true
                ;;
        esac
    done
    
    # Second pass: handle version and help
    for arg in "$@"; do
        case "$arg" in
            --version)
                echo "docker-ctp.sh version 0.4.0"
                echo "Enhanced Docker Container Tag & Push Script"
                echo "Author: elvee"
                echo "License: MIT"
                exit 0
                ;;
            -h|--help)
                init_variables "silent_for_help"  # Initialize variables for help display
                show_help
                exit 0
                ;;
            --generate-config)
                generate_config_files
                exit 0
                ;;
        esac
    done
}

# Function to display help with syntax highlighting
# Display the usage and examples using dynamic and .env file values with colors
show_help() {
    echo -e "
\033[33mUsage:\033[0m ${0##*/} [OPTIONS]

\033[33mOptions:\033[0m
  \033[33m-u, --username\033[0m         Docker Hub or GitHub username (default: Docker Hub: ${DOCKER_USERNAME}, GitHub: ${GITHUB_USERNAME})
  \033[33m-i, --image-name\033[0m       Docker image name (default: ${IMAGE_NAME})
  \033[33m-t, --image-tag\033[0m        Docker image tag (default: 'latest' for Docker, 'main' for GitHub)
  \033[33m-d, --dockerfile-dir\033[0m   Path to Dockerfile folder (default: ${DOCKERFILE_DIR})
  \033[33m-g, --registry\033[0m         Target registry (default: ${REGISTRY}; 'docker' for Docker Hub, 'github' for GitHub)
  \033[33m--no-cache\033[0m             Disable Docker cache and force a clean build (default: use cache)
  \033[33m--force-rebuild\033[0m        Force rebuild even if image already exists (default: skip if exists)
  \033[33m--dry-run\033[0m              Simulate operations without executing them (default: false)
  \033[33m--verbose\033[0m              Enable verbose logging (default: normal)
  \033[33m--quiet\033[0m                Suppress non-error output (default: false)
  \033[33m--no-cleanup\033[0m           Disable cleanup of intermediate images (default: enable cleanup)
  \033[33m--generate-config\033[0m      Generate default configuration files (.env and .dockerignore)
  \033[33m--version\033[0m              Show version information
  \033[33m-h, --help\033[0m             Display this help message

\033[33mExamples:\033[0m

  \033[32m# Example: Generate default configuration files\033[0m
  ${0##*/} --generate-config

  \033[32m# Example: Test run without executing (dry run mode)\033[0m
  ${0##*/} --dry-run -g docker -u ${DOCKER_USERNAME} -i ${IMAGE_NAME}
  
  \033[32m# Example: Push to Docker Hub with verbose logging\033[0m
  ${0##*/} --verbose -g docker -u ${DOCKER_USERNAME} -i ${IMAGE_NAME} -d ${DOCKERFILE_DIR}
  
  \033[32m# Example: Push to GitHub Container Registry in quiet mode\033[0m
  ${0##*/} --quiet -g github -u ${GITHUB_USERNAME} -i ${IMAGE_NAME} -d ${DOCKERFILE_DIR}

  \033[32m# Example: Force a clean build without cache and push to Docker Hub\033[0m
  ${0##*/} --no-cache -g docker -u ${DOCKER_USERNAME} -i ${IMAGE_NAME} -d ${DOCKERFILE_DIR}

  \033[32m# Example: Force rebuild even if image exists and push to Docker Hub\033[0m
  ${0##*/} --force-rebuild -g docker -u ${DOCKER_USERNAME} -i ${IMAGE_NAME} -d ${DOCKERFILE_DIR}

  \033[32m# Example: Push to Docker Hub with a custom tag 'v1.0.0'\033[0m
  ${0##*/} -g docker -u ${DOCKER_USERNAME} -i ${IMAGE_NAME} -t v1.0.0 -d ${DOCKERFILE_DIR}

  \033[32m# Example: Push to GitHub Container Registry with a custom tag 'v1.0.0'\033[0m
  ${0##*/} -g github -u ${GITHUB_USERNAME} -i ${IMAGE_NAME} -t v1.0.0 -d ${DOCKERFILE_DIR}
"
}

# Function for error handling
error_exit() {
    log_error "$1"
    exit 1
}

# Function to check and load the .env file
load_env_file() {
    local init_mode="${1:-normal}" # Parameter from init_variables
    local env_loaded=false
    
    # Define potential locations in order of priority for attempting to load
    local paths_to_attempt_load_specifiers=()
    # Define locations as they would be listed to the user if none are found
    local paths_logged_if_not_found=()

    # 1. Current directory .env (conditional)
    local current_dir_dot_env_specifier="./.env" # Path relative to PWD
    if [[ "$(basename "$PWD")" == "docker-ctp" ]]; then
        paths_to_attempt_load_specifiers+=("$current_dir_dot_env_specifier")
        paths_logged_if_not_found+=("$current_dir_dot_env_specifier (in $PWD)")
    elif [[ "$init_mode" != "silent_for_help" ]]; then
        log_verbose "Current directory ('$(basename "$PWD")') is not 'docker-ctp'; .env file from this directory will not be loaded."
        paths_logged_if_not_found+=("$current_dir_dot_env_specifier (skipped, current directory is not 'docker-ctp')")
    fi

    # Add other standard locations
    local standard_locations_specifiers=(
        "$HOME/.config/docker-ctp/.env"
        "$HOME/.docker-ctp/.env"
        "/etc/docker-ctp/.env"
    )
    paths_to_attempt_load_specifiers+=("${standard_locations_specifiers[@]}")
    paths_logged_if_not_found+=("${standard_locations_specifiers[@]}")
    
    # Deduplicate paths_to_attempt_load_specifiers after resolving them to avoid sourcing twice
    local unique_resolved_paths_to_source=()
    local unique_original_specifiers_for_source=() # To keep original for log_info on success
    local seen_resolved_paths_for_attempt=""

    for path_specifier in "${paths_to_attempt_load_specifiers[@]}"; do
        local resolved_path
        if [[ "$path_specifier" == "./.env" ]]; then
            resolved_path=$(realpath -m "$PWD/$path_specifier" 2>/dev/null || echo "$PWD/$path_specifier")
        else
            resolved_path=$(realpath -m "$path_specifier" 2>/dev/null || echo "$path_specifier")
        fi
        
        # Check if we've already seen this resolved path (bash 3.2 compatible)
        if [[ "$seen_resolved_paths_for_attempt" != *"|$resolved_path|"* ]]; then
            seen_resolved_paths_for_attempt="$seen_resolved_paths_for_attempt|$resolved_path|"
            unique_resolved_paths_to_source+=("$resolved_path")
            unique_original_specifiers_for_source+=("$path_specifier")
        fi
    done

    # Attempt to load from the unique, resolved paths
    for i in "${!unique_resolved_paths_to_source[@]}"; do
        local env_file_to_check="${unique_resolved_paths_to_source[$i]}"
        local original_specifier_for_log="${unique_original_specifiers_for_source[$i]}"

        if [[ -f "$env_file_to_check" && -r "$env_file_to_check" ]]; then
            if [[ "$init_mode" != "silent_for_help" ]]; then
                log_info "Loading configuration from $original_specifier_for_log"
            fi
            # shellcheck source=/dev/null
            source "$env_file_to_check"
            env_loaded=true
            break # Use first found file
        fi
    done

    if [[ "$env_loaded" == false && "$init_mode" != "silent_for_help" ]]; then
        log_verbose "No .env file found or readable in the following checked locations:"
        
        # Deduplicate paths_logged_if_not_found for cleaner output for the user
        local unique_paths_for_final_log_display=()
        local seen_paths_for_final_log=""
        for log_path_display in "${paths_logged_if_not_found[@]}"; do
            # For deduplication, normalize the path string (e.g. resolve ./.env part if present)
            local normalized_key_for_dedup="$log_path_display"
            if [[ "$log_path_display" == "./.env (in $PWD)" ]]; then
                normalized_key_for_dedup=$(realpath -m "$PWD/.env" 2>/dev/null || echo "$PWD/.env")
            elif [[ "$log_path_display" == "./.env (skipped,"* ]]; then # Match prefix
                normalized_key_for_dedup="${PWD}/.env_skipped_marker"
            elif [[ "$log_path_display" == "$HOME/"* || "$log_path_display" == "/etc/"* ]]; then # For absolute-like paths
                 normalized_key_for_dedup=$(realpath -m "$log_path_display" 2>/dev/null || echo "$log_path_display")
            fi

            # Check if we've already seen this normalized path (bash 3.2 compatible)
            if [[ "$seen_paths_for_final_log" != *"|$normalized_key_for_dedup|"* ]]; then
                seen_paths_for_final_log="$seen_paths_for_final_log|$normalized_key_for_dedup|"
                unique_paths_for_final_log_display+=("$log_path_display") 
            fi
        done

        for location_display_message in "${unique_paths_for_final_log_display[@]}"; do
            log_verbose "  - $location_display_message"
        done
        log_verbose "Using default values and environment variables."
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
            --force-rebuild)
                FORCE_REBUILD=true
                shift 1
                ;;
            --dry-run)
                DRY_RUN=true
                shift 1
                ;;
            --verbose)
                LOG_LEVEL="verbose"
                shift 1
                ;;
            --quiet)
                LOG_LEVEL="quiet"
                shift 1
                ;;
            --no-cleanup)
                CLEANUP_ON_EXIT=false
                shift 1
                ;;
            *)
                error_exit "Unknown option: $1"
                ;;
        esac
    done
}

# Function to validate and sanitize input parameters
validate_and_sanitize_inputs() {
    log_verbose "Validating input parameters..."
    
    # Validate registry selection
    if [[ "$REGISTRY" != "docker" && "$REGISTRY" != "github" ]]; then
        error_exit "Invalid registry: '$REGISTRY'. Must be 'docker' or 'github'"
    fi
    
    # Validate and sanitize username
    if [[ ! "$USERNAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]{0,37}$ ]]; then
        error_exit "Invalid username: '$USERNAME'. Username must be 1-38 characters, start with alphanumeric, and contain only letters, numbers, dots, hyphens, and underscores"
    fi
    
    # Validate and sanitize image name
    if [[ ! "$IMAGE_NAME" =~ ^[a-z0-9]+([._-][a-z0-9]+)*$ ]]; then
        error_exit "Invalid image name: '$IMAGE_NAME'. Image name must be lowercase, start with alphanumeric, and contain only lowercase letters, numbers, dots, hyphens, and underscores"
    fi
    
    # Validate image name length
    if [[ ${#IMAGE_NAME} -gt 128 ]]; then
        error_exit "Image name too long: '$IMAGE_NAME'. Maximum length is 128 characters"
    fi
    
    # Validate and sanitize tag
    if [[ -n "$TAG" ]]; then
        if [[ ! "$TAG" =~ ^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$ ]]; then
            error_exit "Invalid tag: '$TAG'. Tag must be 1-128 characters, start with alphanumeric, and contain only letters, numbers, dots, hyphens, and underscores"
        fi
        # Additional tag validation - no consecutive dots or special characters
        if [[ "$TAG" =~ \.\. ]] || [[ "$TAG" =~ -- ]] || [[ "$TAG" =~ __ ]]; then
            error_exit "Invalid tag: '$TAG'. Tag cannot contain consecutive dots, hyphens, or underscores"
        fi
    fi
    
    # Validate dockerfile directory path
    if [[ ! -d "$DOCKERFILE_DIR" ]]; then
        error_exit "Dockerfile directory does not exist: '$DOCKERFILE_DIR'"
    fi
    
    # Check if dockerfile directory is readable
    if [[ ! -r "$DOCKERFILE_DIR" ]]; then
        error_exit "Dockerfile directory is not readable: '$DOCKERFILE_DIR'"
    fi
    
    # Validate Dockerfile exists
    local dockerfile_path="$DOCKERFILE_DIR/Dockerfile"
    if [[ ! -f "$dockerfile_path" ]]; then
        error_exit "Dockerfile not found: '$dockerfile_path'"
    fi
    
    # Check if Dockerfile is readable
    if [[ ! -r "$dockerfile_path" ]]; then
        error_exit "Dockerfile is not readable: '$dockerfile_path'"
    fi
    
    # Sanitize paths - remove potential directory traversal attempts
    DOCKERFILE_DIR=$(realpath "$DOCKERFILE_DIR" 2>/dev/null) || error_exit "Invalid dockerfile directory path: '$DOCKERFILE_DIR'"
    
    # Additional security check - ensure Dockerfile directory is within reasonable bounds
    if [[ "$DOCKERFILE_DIR" =~ \.\./|/\.\./|\.\.$|^\.\. ]]; then
        error_exit "Dockerfile directory path contains suspicious directory traversal patterns: '$DOCKERFILE_DIR'"
    fi
    
    log_success "All input parameters validated successfully"
}

# Function to validate and optimize build context
validate_build_context() {
    log_verbose "Validating build context and checking for optimization opportunities..."
    
    local dockerignore_path="$DOCKERFILE_DIR/.dockerignore"
    local context_warnings=0
    local optimization_suggestions=()
    
    # Check for .dockerignore file
    if [[ -f "$dockerignore_path" ]]; then
        log_verbose "✓ .dockerignore file found: $dockerignore_path"
        
        # Validate .dockerignore syntax
        if [[ -r "$dockerignore_path" ]]; then
            local invalid_lines=0
            while IFS= read -r line; do
                # Skip empty lines and comments
                [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
                
                # Check for potentially problematic patterns
                if [[ "$line" =~ ^\*\*$ ]]; then
                    log_warning ".dockerignore contains '**' which ignores everything"
                    invalid_lines=$((invalid_lines + 1))
                elif [[ "$line" =~ [\\/]$ ]]; then
                    log_verbose "Directory exclusion found: $line"
                fi
            done < "$dockerignore_path"
            
            if [[ $invalid_lines -eq 0 ]]; then
                log_verbose "✓ .dockerignore syntax appears valid"
            else
                log_warning ".dockerignore may contain problematic patterns"
                context_warnings=$((context_warnings + 1))
            fi
        else
            log_warning ".dockerignore file exists but is not readable"
            context_warnings=$((context_warnings + 1))
        fi
    else
        log_verbose "⚠ No .dockerignore file found"
        optimization_suggestions+=("Create a .dockerignore file to exclude unnecessary files from build context")
        context_warnings=$((context_warnings + 1))
    fi
    
    # Check build context size and common optimization opportunities
    log_verbose "Analyzing build context for potential optimizations..."
    
    # Check for common files that should be in .dockerignore
    local common_excludes=(
        ".git" "node_modules" "*.log" "*.tmp" ".DS_Store" 
        "Thumbs.db" "*.swp" "*.swo" ".vscode" ".idea" 
        "coverage" "test" "tests" "*.md" "README*"
    )
    
    local found_excludables=()
    for exclude_pattern in "${common_excludes[@]}"; do
        # Use find to check for existence of patterns (simplified check)
        case "$exclude_pattern" in
            ".*")
                if find "$DOCKERFILE_DIR" -maxdepth 1 -name "$exclude_pattern" -type f 2>/dev/null | head -1 | read; then
                    found_excludables+=("$exclude_pattern")
                fi
                ;;
            "node_modules"|"coverage"|"test"|"tests")
                if [[ -d "$DOCKERFILE_DIR/$exclude_pattern" ]]; then
                    found_excludables+=("$exclude_pattern")
                fi
                ;;
            "*.log"|"*.tmp"|"*.swp"|"*.swo"|"*.md")
                if find "$DOCKERFILE_DIR" -maxdepth 2 -name "$exclude_pattern" 2>/dev/null | head -1 | read; then
                    found_excludables+=("$exclude_pattern")
                fi
                ;;
            ".git"|".vscode"|".idea")
                if [[ -d "$DOCKERFILE_DIR/$exclude_pattern" ]]; then
                    found_excludables+=("$exclude_pattern")
                fi
                ;;
            "README*")
                if find "$DOCKERFILE_DIR" -maxdepth 1 -name "README*" 2>/dev/null | head -1 | read; then
                    found_excludables+=("README*")
                fi
                ;;
        esac
    done
    
    # Report optimization suggestions
    if [[ ${#found_excludables[@]} -gt 0 ]]; then
        log_warning "Found files/directories that could be excluded from build context:"
        for excludable in "${found_excludables[@]}"; do
            log_warning "  - $excludable"
        done
        optimization_suggestions+=("Add these patterns to .dockerignore: ${found_excludables[*]}")
        context_warnings=$((context_warnings + 1))
    fi
    
    # Check for very large files that might slow down build
    log_verbose "Checking for large files in build context..."
    local large_files=()
    while IFS= read -r -d '' file; do
        # Get file size in bytes
        local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
        # Flag files larger than 50MB
        if [[ $size -gt 52428800 ]]; then
            local size_mb=$((size / 1048576))
            large_files+=("$(basename "$file") (${size_mb}MB)")
        fi
    done < <(find "$DOCKERFILE_DIR" -maxdepth 2 -type f -print0 2>/dev/null)
    
    if [[ ${#large_files[@]} -gt 0 ]]; then
        log_warning "Found large files in build context:"
        for large_file in "${large_files[@]}"; do
            log_warning "  - $large_file"
        done
        optimization_suggestions+=("Consider excluding large files or using multi-stage builds")
        context_warnings=$((context_warnings + 1))
    fi
    
    # Provide summary and suggestions
    if [[ $context_warnings -eq 0 ]]; then
        log_success "Build context validation completed - no issues found"
    else
        log_warning "Build context validation completed with $context_warnings warnings"
        
        if [[ ${#optimization_suggestions[@]} -gt 0 ]]; then
            log_info "Build optimization suggestions:"
            for suggestion in "${optimization_suggestions[@]}"; do
                log_info "  💡 $suggestion"
            done
        fi
    fi
}

# Function to ensure required values are provided
validate_arguments() {
    if [[ -z "$USERNAME" || -z "$IMAGE_NAME" || -z "$DOCKERFILE_DIR" || -z "$REGISTRY" ]]; then
        error_exit "Required values are missing. Ensure that they are provided via arguments."
    fi
    
    # Perform comprehensive validation and sanitization
    validate_and_sanitize_inputs
    
    # Validate and optimize build context
    validate_build_context
}

# Function to dynamically set repository names based on directory
set_dynamic_repos() {
    DOCKERHUB_REPO="${DOCKER_USERNAME}/${IMAGE_NAME}"
    GITHUB_REPO="${GITHUB_USERNAME}/${IMAGE_NAME}"
    log_verbose "Using IMAGE_NAME: $IMAGE_NAME, DOCKERHUB_REPO: $DOCKERHUB_REPO, GITHUB_REPO: $GITHUB_REPO"
}

# Function to securely get authentication token
get_token() {
    local token=""
    
    log_verbose "Retrieving authentication token..."
    
    # Check for environment variables first (most secure for automation)
    if [[ "$REGISTRY" == "docker" ]]; then
        if [[ -n "${DOCKER_TOKEN:-}" ]]; then
            token="$DOCKER_TOKEN"
            log_verbose "Using Docker token from environment variable"
        elif [[ -n "${DOCKER_PASSWORD:-}" ]]; then
            token="$DOCKER_PASSWORD"
            log_verbose "Using Docker password from environment variable"
        fi
    elif [[ "$REGISTRY" == "github" ]]; then
        if [[ -n "${GITHUB_TOKEN:-}" ]]; then
            token="$GITHUB_TOKEN"
            log_verbose "Using GitHub token from environment variable"
        elif [[ -n "${GHCR_TOKEN:-}" ]]; then
            token="$GHCR_TOKEN"
            log_verbose "Using GHCR token from environment variable"
        fi
    fi
    
    # If no environment variable found, prompt securely (interactive mode)
    if [[ -z "$token" ]]; then
        if [[ -t 0 ]]; then  # Check if running in interactive terminal
            if [[ "$REGISTRY" == "docker" ]]; then
                log_info "Please enter your Docker Hub Personal Access Token (PAT):"
                log_info "Tip: Set DOCKER_TOKEN environment variable to avoid this prompt"
            elif [[ "$REGISTRY" == "github" ]]; then
                log_info "Please enter your GitHub Personal Access Token (PAT):"
                log_info "Tip: Set GITHUB_TOKEN environment variable to avoid this prompt"
            fi
            read -s token
        else
            error_exit "No authentication token found. Set DOCKER_TOKEN or GITHUB_TOKEN environment variable for non-interactive use."
        fi
    fi
    
    # Validate token is not empty
    if [[ -z "$token" ]]; then
        error_exit "Authentication token cannot be empty"
    fi
    
    # Return token via global variable (avoiding echo for security)
    PAT="$token"
}

# Function to login to the selected registry
login_to_registry() {
    log_info "Logging into $REGISTRY registry..."
    
    # Get authentication token securely
    get_token
    
    if [[ "$DRY_RUN" == true ]]; then
        log_dry_run "Would login to $REGISTRY registry with username: $USERNAME"
        return 0
    fi
    
    if [[ "$REGISTRY" == "docker" ]]; then
        echo "$PAT" | docker login -u "$USERNAME" --password-stdin
    elif [[ "$REGISTRY" == "github" ]]; then
        echo "$PAT" | docker login ghcr.io -u "$USERNAME" --password-stdin
    fi

    if [[ $? -ne 0 ]]; then
        error_exit "Failed to login to $REGISTRY registry. Please check your credentials."
    fi
    
    log_success "Successfully logged into $REGISTRY registry"
    
    # Clear token from memory for security
    unset PAT
}

# Function to build the Docker image
build_docker_image() {
    local image_tag="$IMAGE_NAME:$TAG"
    
    # Phase 3: Smart rebuild optimization - check if image already exists
    if [[ "$FORCE_REBUILD" != true ]]; then
        if check_image_exists "$image_tag"; then
            log_info "Image $image_tag already exists - skipping build"
            log_info "Use --force-rebuild to rebuild anyway"
            log_verbose "Smart rebuild optimization: saved build time by reusing existing image"
            return 0
        fi
    else
        log_verbose "Force rebuild enabled - building regardless of existing image"
    fi
    
    log_info "Building Docker image: $image_tag"
    
    if [[ "$DRY_RUN" == true ]]; then
        if $USE_CACHE; then
            log_dry_run "Would build: docker build -t $image_tag $DOCKERFILE_DIR"
        else
            log_dry_run "Would build: docker build --no-cache -t $image_tag $DOCKERFILE_DIR"
        fi
        return 0
    fi
    
    # Add to cleanup list
    BUILT_IMAGES+=("$image_tag")
    
    if $USE_CACHE; then
        log_verbose "Building with cache enabled..."
        show_progress "Building Docker image" 5
        docker build -t "$image_tag" "$DOCKERFILE_DIR"
    else
        log_verbose "Building without cache (clean build)..."
        show_progress "Building Docker image (no cache)" 8
        docker build --no-cache -t "$image_tag" "$DOCKERFILE_DIR"
    fi

    if [[ $? -ne 0 ]]; then
        error_exit "Failed to build Docker image: $image_tag"
    fi
    
    log_success "Docker image built successfully: $image_tag"
}

# Function to tag the Docker image
tag_docker_image() {
    local source_tag="$IMAGE_NAME:$TAG"
    local target_tag=""
    
    if [[ "$REGISTRY" == "docker" ]]; then
        target_tag="$DOCKERHUB_REPO:$TAG"
    elif [[ "$REGISTRY" == "github" ]]; then
        target_tag="ghcr.io/$GITHUB_REPO:$TAG"
    fi
    
    log_info "Tagging Docker image: $source_tag → $target_tag"
    
    if [[ "$DRY_RUN" == true ]]; then
        log_dry_run "Would tag: docker tag $source_tag $target_tag"
        return 0
    fi
    
    # Add to cleanup list
    BUILT_IMAGES+=("$target_tag")
    
    docker tag "$source_tag" "$target_tag"
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to tag Docker image: $source_tag → $target_tag"
    fi
    
    log_success "Docker image tagged successfully: $target_tag"
}

# Function to push the Docker image
push_docker_image() {
    local target_tag=""
    
    if [[ "$REGISTRY" == "docker" ]]; then
        target_tag="$DOCKERHUB_REPO:$TAG"
    elif [[ "$REGISTRY" == "github" ]]; then
        target_tag="ghcr.io/$GITHUB_REPO:$TAG"
    fi
    
    log_info "Pushing Docker image to $REGISTRY registry: $target_tag"
    
    if [[ "$DRY_RUN" == true ]]; then
        log_dry_run "Would push: docker push $target_tag"
        return 0
    fi
    
    show_progress "Pushing Docker image to $REGISTRY" 6
    docker push "$target_tag"
    if [[ $? -ne 0 ]]; then
        error_exit "Failed to push Docker image to $REGISTRY: $target_tag"
    fi
    
    log_success "Docker image successfully pushed to $REGISTRY registry: $target_tag"
}

# Phase 3: Function to check if Docker image already exists
check_image_exists() {
    local image_tag="$1"
    
    log_verbose "Checking if image already exists: $image_tag"
    
    if [[ "$DRY_RUN" == true ]]; then
        log_dry_run "Would check: docker image inspect $image_tag"
        # In dry run, assume image doesn't exist to show what would happen
        return 1
    fi
    
    if docker image inspect "$image_tag" >/dev/null 2>&1; then
        log_verbose "✓ Image exists: $image_tag"
        return 0
    else
        log_verbose "✗ Image does not exist: $image_tag"
        return 1
    fi
}

# Function to generate default configuration files
generate_config_files() {
    log_info "Generating default configuration files..."
    
    local config_locations=(
        "$HOME/.config/docker-ctp/.env"  # User config directory
    )
    
    local generated_files=()
    
    for config_path in "${config_locations[@]}"; do
        local config_dir=$(dirname "$config_path")
        
        # Create directory if it doesn't exist
        if [[ ! -d "$config_dir" ]]; then
            log_verbose "Creating configuration directory: $config_dir"
            if [[ "$DRY_RUN" != true ]]; then
                mkdir -p "$config_dir" || {
                    log_warning "Failed to create directory: $config_dir"
                    continue
                }
            else
                log_dry_run "Would create directory: $config_dir"
            fi
        fi
        
        # Check if config file already exists
        if [[ -f "$config_path" ]]; then
            log_warning "Configuration file already exists: $config_path"
            log_info "Skipping to avoid overwriting existing configuration"
            continue
        fi
        
        # Generate the configuration file
        log_info "Generating configuration file: $config_path"
        
        if [[ "$DRY_RUN" != true ]]; then
            cat > "$config_path" << 'EOF'
# Docker CTP Configuration File
# Auto-generated by docker-ctp.sh --generate-config

# Docker Hub username used for authentication
DOCKER_USERNAME="your-dockerhub-username"

# GitHub username (personal or organization account) for repository access
GITHUB_USERNAME="your-github-username"

# Directory where the Dockerfile is located (default is current directory)
DOCKERFILE_DIR="."

# Registry to which the Docker image will be pushed (either "docker" or "github")
REGISTRY="docker"

# Default tag for DockerHub images
DEFAULT_DOCKERHUB_TAG="latest"

# Default tag for GitHub images  
DEFAULT_GITHUB_TAG="main"

# Authentication tokens (RECOMMENDED for security and automation)
# Docker Hub Personal Access Token (preferred over DOCKER_PASSWORD)
# DOCKER_TOKEN="your_docker_hub_pat_here"

# Alternative: Docker Hub password (less secure, use DOCKER_TOKEN instead)
# DOCKER_PASSWORD="your_docker_hub_password_here"

# GitHub Personal Access Token for GitHub Container Registry
# GITHUB_TOKEN="your_github_pat_here"

# Alternative GitHub Container Registry token name
# GHCR_TOKEN="your_github_pat_here"

# Build and optimization settings
# USE_CACHE=true
# FORCE_REBUILD=false
# LOG_LEVEL="normal"  # Options: quiet, normal, verbose
# CLEANUP_ON_EXIT=true
EOF
            if [[ $? -eq 0 ]]; then
                log_success "✓ Generated: $config_path"
                generated_files+=("$config_path")
            else
                log_error "Failed to generate: $config_path"
            fi
        else
            log_dry_run "Would generate configuration file: $config_path"
            generated_files+=("$config_path")
        fi
    done
    
    # Generate .dockerignore template if it doesn't exist
    local dockerignore_path="./.dockerignore"
    if [[ ! -f "$dockerignore_path" ]]; then
        log_info "Generating .dockerignore template: $dockerignore_path"
        
        if [[ "$DRY_RUN" != true ]]; then
            cat > "$dockerignore_path" << 'EOF'
# Docker CTP - Dockerignore Template
# Auto-generated by docker-ctp.sh --generate-config

# Version control
.git
.gitignore
.gitattributes

# Development files
.vscode
.idea
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
/tmp

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Documentation (adjust as needed)
README.md
*.md
docs/

# Testing
test/
tests/
coverage/
.nyc_output

# Build artifacts (adjust as needed)
# build/
# dist/

# Environment files (keep sensitive data out of images)
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
EOF
            if [[ $? -eq 0 ]]; then
                log_success "✓ Generated: $dockerignore_path"
                generated_files+=("$dockerignore_path")
            else
                log_error "Failed to generate: $dockerignore_path"
            fi
        else
            log_dry_run "Would generate .dockerignore template: $dockerignore_path"
            generated_files+=("$dockerignore_path")
        fi
    else
        log_info ".dockerignore already exists - skipping template generation"
    fi
    
    # Provide usage instructions
    if [[ ${#generated_files[@]} -gt 0 ]]; then
        log_success "Configuration generation completed!"
        log_info ""
        log_info "📋 Generated files:"
        for file in "${generated_files[@]}"; do
            log_info "  - $file"
        done
        log_info ""
        log_info "🔧 Next steps:"
        log_info "  1. Edit the .env file located at '$HOME/.config/docker-ctp/.env' with your actual values"
        log_info "  2. Set authentication tokens (DOCKER_TOKEN/GITHUB_TOKEN) in '$HOME/.config/docker-ctp/.env'"
        log_info "  3. Review and customize .dockerignore in the current directory as needed"
        log_info "  4. Run: ${0##*/} --dry-run to test your configuration"
        log_info ""
        log_warning "⚠️  Remember to add .env files (if storing them elsewhere) to your global .gitignore to protect sensitive tokens!"
    else
        log_info "No new configuration files were generated"
    fi
}

# Main function to encapsulate script logic
main() {
    # Handle version and help first (before any other processing)
    early_arg_parse "$@"
    
    # Print ASCII Art (now that we know it's not just version/help)
    print_ascii_art
    
    # Initialize variables for main execution
    init_variables
    
    # Parse command-line options
    parse_arguments "$@"

    # Resolve final USERNAME if not set by CLI's -u argument
    # At this point, REGISTRY variable holds the final registry value (CLI > .env/ENV > default)
    # DOCKER_USERNAME and GITHUB_USERNAME hold values from .env/ENV/default set in init_variables
    if [[ -z "$USERNAME" ]]; then # If -u was not used, USERNAME might be empty
        if [[ "$REGISTRY" == "docker" ]]; then
            USERNAME="$DOCKER_USERNAME"
        elif [[ "$REGISTRY" == "github" ]]; then
            USERNAME="$GITHUB_USERNAME"
        else
            # This case should ideally not be reached if REGISTRY validation is robust.
            # REGISTRY is validated in validate_and_sanitize_inputs to be 'docker' or 'github'.
            # If somehow it's not, this is an unexpected state.
            log_warning "Cannot determine default username for registry '$REGISTRY'."
            # USERNAME will remain empty and caught by validate_arguments if DOCKER_USERNAME/GITHUB_USERNAME were also empty.
        fi
    fi
    
    # Check system dependencies (only after parsing arguments)
    check_dependencies
    
    # Ensure all necessary arguments are provided
    validate_arguments

    # Dynamically set the default tag based on the registry (only if TAG not set)
    set_default_tag

    log_info "Starting Docker build and push process..."
    log_verbose "Registry: $REGISTRY, Username: $USERNAME, Image: $IMAGE_NAME:$TAG"
    log_verbose "Dockerfile directory: $DOCKERFILE_DIR"
    log_verbose "Cache enabled: $USE_CACHE, Dry run: $DRY_RUN, Force rebuild: $FORCE_REBUILD"

    # Main execution
    login_to_registry
    build_docker_image
    tag_docker_image
    push_docker_image

    if [[ "$DRY_RUN" == true ]]; then
        log_success "Dry run completed successfully - no actual operations were performed"
    else
        log_success "Docker image successfully pushed to $REGISTRY registry"
    fi
}

# Execute the main function
main "$@"
