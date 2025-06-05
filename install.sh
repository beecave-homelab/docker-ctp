#!/bin/bash
set -euo pipefail

# Simple installer for docker-ctp.sh

SOURCE_SCRIPT_NAME="docker-ctp.sh"
INSTALL_DIR="/usr/local/bin"
INSTALL_NAME="docker-ctp"
CONFIG_DIR="$HOME/.config/docker-ctp"
CONFIG_FILE="$CONFIG_DIR/.env"
DRY_RUN=false

log_info() { echo "ℹ️  [INFO] $1"; }
log_success() { echo "✅ [SUCCESS] $1"; }
log_warning() { echo "⚠️  [WARNING] $1" >&2; }
log_error() { echo "❌ [ERROR] $1" >&2; exit 1; }
log_dry() { [[ "$DRY_RUN" == true ]] && echo "🔸 [DRY-RUN] $1"; }

show_help() {
    cat <<EOF_HELP
Usage: $0 [--dry-run]
Installs $SOURCE_SCRIPT_NAME to $INSTALL_DIR/$INSTALL_NAME
EOF_HELP
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run|-n)
                DRY_RUN=true
                ;;
            --help|-h)
                show_help
                ;;
            *)
                log_error "Unknown option: $1"
                ;;
        esac
        shift
    done
}

ensure_writable() {
    if [[ ! -w "$INSTALL_DIR" ]]; then
        log_error "Need write access to $INSTALL_DIR"
    fi
}

copy_script() {
    log_info "Installing $SOURCE_SCRIPT_NAME to $INSTALL_DIR/$INSTALL_NAME"
    if [[ "$DRY_RUN" == true ]]; then
        log_dry "cp $SOURCE_SCRIPT_NAME $INSTALL_DIR/$INSTALL_NAME"
    else
        cp "$SOURCE_SCRIPT_NAME" "$INSTALL_DIR/$INSTALL_NAME"
        chmod +x "$INSTALL_DIR/$INSTALL_NAME"
    fi
}

create_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        log_warning "Config file already exists: $CONFIG_FILE"
    else
        log_info "Creating default config at $CONFIG_FILE"
        if [[ "$DRY_RUN" == true ]]; then
            log_dry "mkdir -p $CONFIG_DIR && touch $CONFIG_FILE"
        else
            mkdir -p "$CONFIG_DIR"
            touch "$CONFIG_FILE"
        fi
    fi
}

main() {
    parse_args "$@"
    ensure_writable
    copy_script
    create_config
    log_success "Installation complete"
}

main "$@"
