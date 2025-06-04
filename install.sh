#!/bin/bash
set -euo pipefail

# Script to install docker-ctp.sh to /usr/local/bin
# and optionally generate a default config if one doesn't exist.

# --- Configuration ---
SOURCE_SCRIPT_NAME="docker-ctp.sh"
INSTALL_DIR="/usr/local/bin"
INSTALL_NAME="docker-ctp"
CONFIG_DIR="$HOME/.config/docker-ctp"
CONFIG_FILE="$CONFIG_DIR/.env"
BACKUP_SUFFIX=".backup.$(date +%Y%m%d_%H%M%S)"

# Prevent infinite recursion
SUDO_RETRY="${SUDO_RETRY:-false}"

# Dry-run mode - preview operations without executing them
DRY_RUN=false

# --- Helper Functions ---
log_info() {
    echo "ℹ️  [INFO] $1"
}

log_success() {
    echo "✅ [SUCCESS] $1"
}

log_warning() {
    echo "⚠️  [WARNING] $1" >&2
}

log_error() {
    echo "❌ [ERROR] $1" >&2
    exit 1
}

log_dry_run() {
    if [[ "$DRY_RUN" == true ]]; then
        echo "🔸 [DRY-RUN] $1"
    fi
}

# Show usage information
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Install docker-ctp.sh to /usr/local/bin and optionally generate default configuration.

OPTIONS:
    --dry-run, -n    Preview what would be done without making any changes
    --help, -h       Show this help message

EXAMPLES:
    $0                # Install docker-ctp
    $0 --dry-run      # Preview installation without changes
    $0 -n             # Same as --dry-run

EOF
    exit 0
}

# Function to ask for user confirmation
ask_yes_no() {
    local question="$1"
    local default_answer="${2:-N}" # Default to No
    local answer

    # In dry-run mode, assume default answer to avoid hanging
    if [[ "$DRY_RUN" == true ]]; then
        log_dry_run "Would ask: $question [default: $default_answer]"
        return $([ "$default_answer" = "Y" ] && echo 0 || echo 1)
    fi

    while true; do
        if [[ "$default_answer" == "Y" ]]; then
            read -r -p "$question [Y/n]: " answer
            answer=${answer:-Y}
        else
            read -r -p "$question [y/N]: " answer
            answer=${answer:-N}
        fi

        case "$answer" in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes (y) or no (n).";;
        esac
    done
}

# Function to validate installation directory
validate_install_dir() {
    local test_file="$INSTALL_DIR/.install_test_$$"
    
    log_info "Validating installation directory '$INSTALL_DIR'..."
    
    # Check if directory exists
    if [[ ! -d "$INSTALL_DIR" ]]; then
        if [[ "$DRY_RUN" == true ]]; then
            log_dry_run "Would check if directory '$INSTALL_DIR' exists"
            log_warning "Installation directory '$INSTALL_DIR' does not exist."
        else
            log_error "Installation directory '$INSTALL_DIR' does not exist."
        fi
        return 1
    fi
    
    # Test write permissions
    if [[ "$DRY_RUN" == true ]]; then
        log_dry_run "Would test write permissions to '$INSTALL_DIR'"
        # In dry-run, assume we need sudo for /usr/local/bin
        if [[ "$INSTALL_DIR" == "/usr/local/bin" ]]; then
            log_warning "Cannot write to '$INSTALL_DIR' without elevated privileges."
            return 1
        else
            log_success "Installation directory appears writable."
            return 0
        fi
    else
        if ! touch "$test_file" 2>/dev/null; then
            log_warning "Cannot write to '$INSTALL_DIR' without elevated privileges."
            return 1
        else
            rm -f "$test_file"
            log_success "Installation directory is writable."
            return 0
        fi
    fi
}

# Function to check if PATH contains install directory
check_path() {
    if [[ ":$PATH:" == *":$INSTALL_DIR:"* ]]; then
        log_success "'$INSTALL_DIR' is in your PATH."
        return 0
    else
        log_warning "'$INSTALL_DIR' is not in your PATH."
        log_info "You may need to add it to your shell profile (e.g., ~/.bashrc, ~/.zshrc)."
        return 1
    fi
}

# Function to backup existing files
backup_file() {
    local file_path="$1"
    local backup_path="${file_path}${BACKUP_SUFFIX}"
    
    if [[ -f "$file_path" ]]; then
        if [[ "$DRY_RUN" == true ]]; then
            log_dry_run "Would create backup: $backup_path"
        else
            log_info "Creating backup: $backup_path"
            cp "$file_path" "$backup_path" || {
                log_error "Failed to create backup of '$file_path'"
                return 1
            }
            log_success "Backup created successfully."
        fi
    fi
}

# Function to validate the source script
validate_source_script() {
    log_info "Validating source script '$SOURCE_SCRIPT_NAME'..."
    
    # Check if file exists and is readable
    if [[ ! -r "$SOURCE_SCRIPT_NAME" ]]; then
        log_error "Source script '$SOURCE_SCRIPT_NAME' is not readable or doesn't exist."
        return 1
    fi
    
    # Check if it's a valid shell script
    if ! head -1 "$SOURCE_SCRIPT_NAME" | grep -q "^#!/.*sh"; then
        log_warning "Source script doesn't appear to be a shell script (no shebang found)."
        if ! ask_yes_no "Continue anyway?" "N"; then
            return 1
        fi
    fi
    
    # Check if it supports --generate-config
    if ! grep -q "generate-config" "$SOURCE_SCRIPT_NAME"; then
        log_warning "Source script may not support --generate-config option."
    fi
    
    log_success "Source script validation passed."
    return 0
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run|-n)
                DRY_RUN=true
                log_info "Dry-run mode enabled - no changes will be made"
                shift
                ;;
            --help|-h)
                show_usage
                ;;
            *)
                log_error "Unknown option: $1"
                log_info "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Function to test configuration generation in dry-run mode
test_config_generation() {
    local temp_dir
    local temp_script
    local temp_config_dir
    local temp_config_file
    
    log_info "Testing configuration generation..."
    
    # Create temporary directory for testing
    temp_dir=$(mktemp -d -t docker-ctp-test.XXXXXX) || {
        log_warning "Failed to create temporary directory for testing"
        return 1
    }
    
    temp_script="$temp_dir/docker-ctp"
    temp_config_dir="$temp_dir/.config/docker-ctp"
    temp_config_file="$temp_config_dir/.env"
    
    # Copy source script to temp location
    if ! cp "$SOURCE_SCRIPT_NAME" "$temp_script"; then
        log_warning "Failed to copy script for testing"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Make it executable
    chmod +x "$temp_script" || {
        log_warning "Failed to make test script executable"
        rm -rf "$temp_dir"
        return 1
    }
    
    # Test if --generate-config works
    log_info "Testing --generate-config command..."
    
    # Set HOME for the test script to use our temp directory
    if ! HOME="$temp_dir" "$temp_script" --generate-config >/dev/null 2>&1; then
        log_warning "The --generate-config command failed during testing"
        log_info "This could be due to bash version compatibility issues"
        
        # Try to get more specific error information
        local error_output
        error_output=$(HOME="$temp_dir" "$temp_script" --generate-config 2>&1 | head -3)
        if [[ -n "$error_output" ]]; then
            log_info "Error details: $error_output"
        fi
        
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Check if config file was created
    if [[ -f "$temp_config_file" ]]; then
        log_success "Configuration generation test passed"
        log_info "Preview of generated .env file content:"
        echo "----------------------------------------"
        # Show first 20 lines with line numbers, but hide any sensitive defaults
        head -20 "$temp_config_file" | sed 's/^/  | /' | sed 's/password=.*/password=***HIDDEN***/i'
        
        local line_count=$(wc -l < "$temp_config_file")
        if [[ $line_count -gt 20 ]]; then
            echo "  | ... (showing first 20 of $line_count lines)"
        fi
        echo "----------------------------------------"
    else
        log_warning "Configuration file was not generated during testing"
    fi
    
    # Check for other generated files
    local generated_files=()
    while IFS= read -r -d '' file; do
        generated_files+=("${file#$temp_dir/}")
    done < <(find "$temp_dir" -type f -not -path "$temp_script" -print0 2>/dev/null)
    
    if [[ ${#generated_files[@]} -gt 0 ]]; then
        log_info "Other files that would be generated:"
        for file in "${generated_files[@]}"; do
            echo "  - $file"
        done
    fi
    
    # Cleanup
    rm -rf "$temp_dir"
    return 0
}

# --- Main Installation Logic ---
main() {
    # Parse command line arguments first
    parse_arguments "$@"
    
    if [[ "$DRY_RUN" == true ]]; then
        echo "🔸 DRY RUN MODE - No actual changes will be made"
        echo "=================================="
    fi
    
    log_info "Starting docker-ctp installation..."

    # Validate source script first
    validate_source_script || exit 1

    # Check if we need elevated privileges
    local need_sudo=false
    if ! validate_install_dir; then
        need_sudo=true
        log_info "Elevated privileges required for installation."
        
        if [[ "$DRY_RUN" == true ]]; then
            log_dry_run "Would attempt to re-run with sudo privileges"
            log_dry_run "Command would be: sudo -E '$0' $*"
        else
            # Prevent infinite recursion
            if [[ "$SUDO_RETRY" == "true" ]]; then
                log_error "Already attempted sudo escalation. Installation failed."
                exit 1
            fi
            
            # Check if sudo is available
            if ! command -v sudo >/dev/null 2>&1; then
                log_error "sudo is not available, but elevated privileges are required."
                exit 1
            fi
            
            # Test sudo access
            if ! sudo -v 2>/dev/null; then
                log_error "Cannot obtain sudo privileges."
                exit 1
            fi
            
            log_info "Re-running with elevated privileges..."
            export SUDO_RETRY=true
            exec sudo -E "$0" "$@"
        fi
    fi

    INSTALL_PATH="$INSTALL_DIR/$INSTALL_NAME"

    # Check if the script is already installed
    if [[ -f "$INSTALL_PATH" ]]; then
        if ask_yes_no "'$INSTALL_NAME' is already installed at '$INSTALL_PATH'. Do you want to replace it?" "N"; then
            log_info "Proceeding with replacement..."
            backup_file "$INSTALL_PATH"
        else
            log_info "Installation aborted by user. Existing script at '$INSTALL_PATH' will not be replaced."
            exit 0
        fi
    fi

    # Copy the script to the installation directory
    if [[ "$DRY_RUN" == true ]]; then
        log_dry_run "Would copy '$SOURCE_SCRIPT_NAME' to '$INSTALL_PATH'"
    else
        log_info "Copying '$SOURCE_SCRIPT_NAME' to '$INSTALL_PATH'..."
        if ! cp "$SOURCE_SCRIPT_NAME" "$INSTALL_PATH"; then
            log_error "Failed to copy script. Check permissions for $INSTALL_DIR."
        fi
        log_success "Script copied to $INSTALL_PATH."
    fi

    # Make the script executable
    if [[ "$DRY_RUN" == true ]]; then
        log_dry_run "Would make '$INSTALL_PATH' executable (chmod +x)"
    else
        log_info "Making '$INSTALL_PATH' executable..."
        if ! chmod +x "$INSTALL_PATH"; then
            log_error "Failed to make script executable. Check permissions for $INSTALL_PATH."
        fi
        log_success "'$INSTALL_PATH' is now executable."
    fi

    # Validate installation by testing the script
    if [[ "$DRY_RUN" == true ]]; then
        log_dry_run "Would validate installation by running '$INSTALL_PATH --help'"
        
        # Actually test the source script to ensure it works
        log_info "Testing source script functionality..."
        
        # Test basic execution first
        if "$SOURCE_SCRIPT_NAME" --help >/dev/null 2>&1; then
            log_success "Source script --help command works correctly"
        elif "$SOURCE_SCRIPT_NAME" --version >/dev/null 2>&1; then
            log_success "Source script --version command works (--help may have issues)"
        elif "$SOURCE_SCRIPT_NAME" >/dev/null 2>&1; then
            log_warning "Source script runs but --help/--version may not be supported"
        else
            log_warning "Source script execution failed - there may be compatibility issues"
            log_info "This could be due to bash version compatibility (e.g., associative arrays)"
        fi
    else
        log_info "Validating installation..."
        if ! "$INSTALL_PATH" --help >/dev/null 2>&1; then
            log_warning "Installed script may not be working properly (--help failed)."
        else
            log_success "Installation validation passed."
        fi
    fi

    # Check for existing configuration and generate if missing/requested
    log_info "Checking for existing configuration at '$CONFIG_FILE'..."
    local generate_new_config=true

    if [[ -f "$CONFIG_FILE" ]]; then
        if ask_yes_no "Configuration file '$CONFIG_FILE' already exists. Do you want to replace it with the default configuration?" "N"; then
            log_info "Existing configuration will be replaced."
            backup_file "$CONFIG_FILE"
            if [[ "$DRY_RUN" == true ]]; then
                log_dry_run "Would remove existing config file '$CONFIG_FILE'"
            else
                rm -f "$CONFIG_FILE" || log_warning "Could not remove existing config file '$CONFIG_FILE'."
            fi
        else
            log_info "Existing configuration file will be kept. Skipping generation of a new default config."
            generate_new_config=false
        fi
    else
        log_info "No existing configuration file found. A default configuration file will be generated."
    fi

    if [[ "$generate_new_config" == true ]]; then
        log_info "Attempting to generate default configuration..."
        
        # Ensure the config directory exists
        if [[ ! -d "$CONFIG_DIR" ]]; then
            if [[ "$DRY_RUN" == true ]]; then
                log_dry_run "Would create configuration directory '$CONFIG_DIR'"
            else
                log_info "Creating configuration directory '$CONFIG_DIR'..."
                mkdir -p "$CONFIG_DIR" || log_error "Failed to create configuration directory '$CONFIG_DIR'."
                log_success "Configuration directory created."
            fi
        fi
        
        # Run the --generate-config command using the newly installed script
        if [[ "$DRY_RUN" == true ]]; then
            log_dry_run "Would run '$INSTALL_PATH --generate-config' to generate default configuration"
            log_dry_run "Would check if configuration file was created at '$CONFIG_FILE'"
            
            # Actually test the configuration generation safely
            log_info "Testing configuration generation with source script..."
            if test_config_generation; then
                log_success "Configuration generation test completed successfully"
                log_info "The same configuration would be created at '$CONFIG_FILE'"
            else
                log_warning "Configuration generation test failed"
                log_info "There may be issues with the --generate-config command"
            fi
        else
            if "$INSTALL_PATH" --generate-config; then
                if [[ -f "$CONFIG_FILE" ]]; then
                    log_success "Default configuration generated successfully at '$CONFIG_FILE'."
                    log_info "Please review and edit '$CONFIG_FILE' with your details."
                else
                    log_warning "Configuration file '$CONFIG_FILE' was not created by --generate-config command."
                fi
            else
                log_warning "Failed to generate configuration using --generate-config command."
                log_info "You may need to create the configuration manually."
            fi
        fi
    fi

    # Final validation
    check_path

    if [[ "$DRY_RUN" == true ]]; then
        echo "=================================="
        echo "🔸 DRY RUN COMPLETED - No changes were made"
        log_info "To perform the actual installation, run without --dry-run flag"
    else
        log_success "docker-ctp installation process completed!"
        log_info "You can now run 'docker-ctp' from anywhere in your terminal."
    fi
    
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        log_info "To add '$INSTALL_DIR' to your PATH permanently, add this line to your shell profile:"
        log_info "export PATH=\"$INSTALL_DIR:\$PATH\""
    fi
}

# --- Script Execution ---
main "$@"
