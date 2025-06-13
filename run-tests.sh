#!/bin/bash

# ================================================
# Usage:
# 1. Make the script executable:
#      chmod +x setup-env.sh
# 2. Run the script:
#      
# 
# Or do both in one command:
#      chmod +x run-tests.sh && ./run-tests.sh
# ================================================

clear

# === Colors ===
BLUE_BG="\033[44m"
GREEN_BG="\033[42m"
RED_BG="\033[41m"
WHITE="\033[97m"
RESET="\033[0m"

print_info() {
    echo -e "${BLUE_BG}${WHITE}>>> $1${RESET}"
}

print_success() {
    echo -e "${GREEN_BG}${WHITE}>>> $1${RESET}"
}

print_error() {
    echo -e "${RED_BG}${WHITE}>>> ERROR: $1${RESET}"
    exit 1
}

# === Run tests with output and coverage ===
print_info "Running unit tests with pytest (stdout visible, coverage enabled)..."

# Activate the virtual environment (Windows-specific path)
. .venv/Scripts/activate

# Run pytest via 'python -m' to ensure it uses the venv's interpreter
# -s            : allow print statements to be shown in the output
# --tb=short    : use a short traceback format
# --cov=src     : measure test coverage on the 'src' directory
# --cov-report=term-missing : show missing lines in the coverage report
# If the tests fail (exit code != 0), print an error message and exit
python -m pytest -s --tb=short --cov=src --cov-report=term-missing || print_error "Tests failed"

print_success "All tests passed successfully!"
