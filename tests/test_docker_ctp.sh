#!/usr/bin/env bats

# Basic BATS test suite for docker-ctp.sh

# Load test helpers (if any)
# load 'test_helper'

# Global setup (runs once)
setup_file() {
    # Ensure BATS is installed (simple check)
    if ! command -v bats >/dev/null 2>&1; then
        echo "Error: BATS (Bash Automated Testing System) is not installed." >&2
        echo "Please install BATS to run these tests (e.g., 'brew install bats-core' or 'sudo apt-get install bats')." >&2
        exit 1
    fi

    # Determine the absolute path to the script under test
    # Assumes the test file is in a subdirectory (e.g., 'tests') of the project root
    local test_file_dir
    test_file_dir="$(cd "$(dirname "$BATS_TEST_FILENAME")" && pwd)"
    local script_path_relative_to_test_file="../docker-ctp.sh"
    SCRIPT_UNDER_TEST="$test_file_dir/$script_path_relative_to_test_file"
    # Normalize to an absolute path
    SCRIPT_UNDER_TEST="$(cd "$(dirname "$SCRIPT_UNDER_TEST")" && pwd)/$(basename "$SCRIPT_UNDER_TEST")"

    if [ ! -f "$SCRIPT_UNDER_TEST" ]; then
        echo "Error: Script not found at $SCRIPT_UNDER_TEST." >&2
        echo "Attempted to resolve from BATS_TEST_FILENAME: $BATS_TEST_FILENAME" >&2
        exit 1
    fi
    # Make the script executable if it's not (common in CI environments)
    chmod +x "$SCRIPT_UNDER_TEST"
    export SCRIPT_UNDER_TEST # Export for subshells
    
    # Define a temporary directory for tests that might create files
    TEST_TEMP_DIR="$(mktemp -d -t docker_ctp_tests_XXXXXX)"
    export TEST_TEMP_DIR
}

# Global teardown (runs once)
teardown_file() {
    if [ -d "$TEST_TEMP_DIR" ]; then
        rm -rf "$TEST_TEMP_DIR"
    fi
}

# Per-test setup (runs before each test)
setup() {
    # Ensure we have a clean environment for some variables if needed
    unset DOCKER_USERNAME GITHUB_USERNAME IMAGE_NAME DOCKERFILE_DIR REGISTRY TAG
    unset DOCKER_TOKEN GITHUB_TOKEN
    
    # Create a dummy Dockerfile in a temporary context for tests that need it
    DUMMY_CONTEXT="$TEST_TEMP_DIR/dummy_context"
    mkdir -p "$DUMMY_CONTEXT"
    echo "FROM alpine" > "$DUMMY_CONTEXT/Dockerfile"
    export DUMMY_CONTEXT
}

# Per-test teardown (runs after each test)
teardown() {
    # Clean up dummy context if it was used
    if [ -d "$DUMMY_CONTEXT" ]; then
        rm -rf "$DUMMY_CONTEXT"
    fi
}

# --- Helper Functions ---

# Function to run the script with arguments and capture output
run_script() {
    run "$SCRIPT_UNDER_TEST" "$@"
}

# --- Test Cases ---

@test "Displays help message with --help" {
    run_script --help
    [ "$status" -eq 0 ]
    assert_output --partial "Usage: docker-ctp.sh [OPTIONS]"
    assert_output --partial "Options:"
    assert_output --partial "Examples:"
}

@test "Displays help message with -h" {
    run_script -h
    [ "$status" -eq 0 ]    assert_output --partial "Usage: docker-ctp.sh [OPTIONS]"
    assert_output --partial "Options:"
    assert_output --partial "Examples:"
    assert_output --partial "Usage: docker-ctp.sh [OPTIONS]"
}

@test "Displays version information with --version" {
    run_script --version
    [ "$status" -eq 0 ]
    assert_output --partial "docker-ctp.sh version" # Current version is 0.4.0, this is more flexible
    assert_output --partial "Author: elvee"
    assert_output --partial "License: MIT"
}

@test "Exits with error on unknown option" {
    run_script --unknown-option
    [ "$status" -ne 0 ] # Should be 1
    assert_output --partial "ERROR"
    assert_output --partial "Unknown option: --unknown-option"
}

@test "Dry run: Simulates operations without execution (--dry-run)" {
    # This is a basic dry run test. More specific dry-run tests will be added later.
    run_script --dry-run -g docker -u testuser -i testimage -d "$DUMMY_CONTEXT"
    [ "$status" -eq 0 ]
    assert_output --partial "[DRY-RUN] Would login to docker registry"
    assert_output --partial "[DRY-RUN] Would build: docker build -t testimage:latest" # Assumes default tag
    assert_output --partial "[DRY-RUN] Would tag: docker tag testimage:latest testuser/testimage:latest"
    assert_output --partial "[DRY-RUN] Would push: docker push testuser/testimage:latest"
    assert_output --partial "Dry run completed successfully"
    
    # Verify no actual docker commands were run (more complex to check directly without mocking docker)
    # For now, relying on script output and assuming docker commands are guarded by DRY_RUN checks.
}

@test "Configuration: Generates config files with --generate-config" {
    cd "$TEST_TEMP_DIR" # Run in a clean temp directory
    
    run "$SCRIPT_UNDER_TEST" --generate-config
    [ "$status" -eq 0 ]
    assert_output --partial "Generating default configuration files..."
    assert_output --partial "Generated: ./.env"
    assert_output --partial "Generated: ./.dockerignore"
    assert_output --partial "Configuration generation completed!"
    
    [ -f ".env" ]
    [ -f ".dockerignore" ]
    
    # Cleanup (go back to original dir for other tests)
    cd "$OLDPWD"
}

@test "Configuration: --generate-config skips if files exist" {
    cd "$TEST_TEMP_DIR"
    touch .env
    touch .dockerignore
    echo "existing content" > .env # Add some content to check it's not overwritten

    run "$SCRIPT_UNDER_TEST" --generate-config
    [ "$status" -eq 0 ]
    assert_output --partial "Configuration file already exists: ./.env"
    assert_output --partial ".dockerignore already exists"
    assert_output --partial "No new configuration files were generated"

    # Verify existing file was not overwritten by checking its content
    local env_content
    env_content=$(cat .env)
    [ "$env_content" = "existing content" ]
    
    cd "$OLDPWD"
}


# --- Placeholder for future test categories ---

# @test "Variable Priority: CLI > ENV > .env > default for IMAGE_NAME" {
#   skip "TODO"
# }

# @test "Variable Priority: CLI > ENV > .env > default for USERNAME (Docker)" {
#   skip "TODO"
# }

# @test "Variable Priority: CLI > ENV > .env > default for USERNAME (GitHub)" {
#   skip "TODO"
# }

# @test "Variable Priority: CLI > ENV > .env > default for TAG" {
#   skip "TODO"
# }

# @test "Variable Priority: CLI > ENV > .env > default for REGISTRY" {
#   skip "TODO"
# }

# @test "Variable Priority: CLI > ENV > .env > default for DOCKERFILE_DIR" {
#   skip "TODO"
# }


# @test "Logging: --quiet mode suppresses info/verbose logs" {
#   skip "TODO"
# }

# @test "Logging: --verbose mode shows verbose logs" {
#   skip "TODO"
# }


# @test "Input Validation: Invalid username" {
#   skip "TODO"
# }

# @test "Input Validation: Invalid image name" {
#   skip "TODO"
# }

# @test "Input Validation: Invalid tag" {
#   skip "TODO"
# }

# @test "Input Validation: Invalid registry" {
#   skip "TODO"
# }

# @test "Input Validation: Non-existent Dockerfile directory" {
#   skip "TODO"
# }

# @test "Input Validation: Dockerfile not found in directory" {
#   skip "TODO"
# }


# @test "Build Context: .dockerignore present and valid" {
#   skip "TODO"
# }

# @test "Build Context: Warns if .dockerignore is missing" {
#   skip "TODO"
# }

# @test "Build Context: Suggests excluding common files if not in .dockerignore" {
#   skip "TODO"
# }


# @test "Smart Rebuild: Skips build if image exists" {
#   # Requires Docker daemon and ability to create/inspect images
#   skip "TODO: Complex test requiring Docker interaction"
# }

# @test "Smart Rebuild: Builds if image does not exist" {
#   skip "TODO: Complex test requiring Docker interaction"
# }

# @test "Smart Rebuild: Forces rebuild with --force-rebuild even if image exists" {
#   skip "TODO: Complex test requiring Docker interaction"
# }


# @test "Authentication: Uses DOCKER_TOKEN environment variable for Docker Hub" {
#   skip "TODO: Requires mocking/spying on 'docker login' or secure credential handling"
# }

# @test "Authentication: Uses GITHUB_TOKEN environment variable for GitHub CR" {
#   skip "TODO: Requires mocking/spying on 'docker login' or secure credential handling"
# }

# @test "Authentication: Prompts for token if not in ENV (interactive test - harder to automate)" {
#   skip "TODO: Interactive tests are difficult for automated suites"
# }

# @test "Authentication: Fails if no token and not interactive" {
#   skip "TODO"
# }


# @test "Build Process: Successful build (Docker Hub)" {
#   # Requires Docker daemon
#   skip "TODO: Complex test requiring Docker interaction"
# }

# @test "Build Process: Successful build (GitHub CR)" {
#   skip "TODO: Complex test requiring Docker interaction"
# }

# @test "Build Process: Build failure handling" {
#   skip "TODO: Complex test requiring Docker interaction and a failing Dockerfile"
# }


# @test "Tagging Process: Correct tagging for Docker Hub" {
#   skip "TODO: Complex test requiring Docker interaction"
# }

# @test "Tagging Process: Correct tagging for GitHub CR" {
#   skip "TODO: Complex test requiring Docker interaction"
# }


# @test "Push Process: Successful push (Docker Hub)" {
#   # Requires Docker daemon and registry credentials
#   skip "TODO: Very complex test requiring Docker interaction and live registry"
# }

# @test "Push Process: Successful push (GitHub CR)" {
#   skip "TODO: Very complex test requiring Docker interaction and live registry"
# }


# @test "Cleanup: Removes intermediate images on successful run" {
#   skip "TODO: Complex test requiring Docker interaction"
# }

# @test "Cleanup: --no-cleanup preserves images" {
#   skip "TODO: Complex test requiring Docker interaction"
# }

# @test "Cleanup: Removes images on script interruption (trap handling)" {
#   # This is very hard to test reliably in BATS
#   skip "TODO: Difficult to test signal trapping reliably"
# } 
