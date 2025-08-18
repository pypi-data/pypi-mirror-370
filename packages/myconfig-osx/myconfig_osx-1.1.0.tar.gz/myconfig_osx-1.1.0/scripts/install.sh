#!/bin/bash
#########################################################################
# @File Name:    install.sh
# @Author:       MyConfig Team
# @Created Time: 2024
# @Copyright:    GPL 2.0
# @Description:  MyConfig installation script
#########################################################################

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}▸${NC} $1"
}

print_success() {
    echo -e "${GREEN}✔${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✘${NC} $1"
}

# Check system environment
check_environment() {
    print_info "Checking system environment..."
    
    # Check if macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This tool is designed for macOS systems only"
        exit 1
    fi
    
    # Check Python3
    if ! command -v python3 >/dev/null 2>&1; then
        print_error "Python3 not found, please install Python first:"
        echo "  brew install python"
        exit 1
    fi
    
    # Check pip3
    if ! command -v pip3 >/dev/null 2>&1; then
        print_error "pip3 not found, please install Python first"
        exit 1
    fi
    
    print_success "System environment check passed"
}

# Show installation menu
show_menu() {
    echo ""
    print_info "Welcome to MyConfig Installation!"
    print_info "=================================="
    echo ""
    print_info "MyConfig is a comprehensive macOS system configuration backup and restore tool."
    echo ""
    print_warning "⭐ RECOMMENDED: Install from PyPI"
    echo "   pip install myconfig-osx"
    echo ""
    print_info "If you prefer to install from source, please choose an installation method:"
    echo "  1) User installation (Recommended) - Install for current user"
    echo "  2) System installation - Install system-wide (requires sudo)"
    echo "  3) Development installation - Editable mode installation"
    echo "  4) Cancel installation"
    echo ""
}

# User installation
install_user() {
    print_info "Starting user installation..."
    
    # Install to user directory
    pip3 install --user -e .
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_warning "~/.local/bin is not in your PATH"
        print_info "Add the following line to your shell profile (~/.zshrc or ~/.bash_profile):"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
    
    print_success "User installation completed!"
    verify_installation
}

# System installation
install_system() {
    print_info "Starting system installation..."
    print_warning "This requires administrator privileges"
    
    # Install system-wide
    sudo pip3 install -e .
    
    print_success "System installation completed!"
    verify_installation
}

# Development installation
install_dev() {
    print_info "Starting development installation..."
    
    # Install in editable mode with dev dependencies
    pip3 install -e .[dev]
    
    print_success "Development installation completed!"
    verify_installation
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."
    
    if command -v myconfig >/dev/null 2>&1; then
        print_success "MyConfig installed successfully!"
        echo ""
        print_info "Version: $(myconfig --version)"
        echo ""
        print_info "Quick start:"
        echo "  myconfig doctor        # System health check"
        echo "  myconfig --help        # Show all commands"
        echo "  myconfig export        # Create backup"
        echo ""
    else
        print_error "Installation verification failed"
        print_info "Please check your PATH or try system installation"
        exit 1
    fi
}

# Installation choice handler
install_choice() {
    while true; do
        read -p "Please enter your choice [1-4]: " choice
        case $choice in
            1)
                install_user
                break
                ;;
            2)
                install_system
                break
                ;;
            3)
                install_dev
                break
                ;;
            4)
                print_info "Installation cancelled"
                exit 0
                ;;
            *)
                print_error "Invalid choice, please enter 1-4"
                ;;
        esac
    done
}

# Main function
main() {
    check_environment
    show_menu
    install_choice
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --user)
            check_environment
            install_user
            exit 0
            ;;
        --system)
            check_environment
            install_system
            exit 0
            ;;
        --dev)
            check_environment
            install_dev
            exit 0
            ;;
        --help|-h)
            echo "MyConfig Installation Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --user    Install for current user only"
            echo "  --system  Install system-wide (requires sudo)"
            echo "  --dev     Install in development mode"
            echo "  --help    Show this help message"
            echo ""
            echo "Interactive mode: $0"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
    shift
done

# Run main function if no arguments provided
main
