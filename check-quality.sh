#!/bin/bash

# === check-quality.sh ===
# Make this file executable: chmod +x check-quality.sh
# Run it with: ./check-quality.sh
# Or in one line: chmod +x check-quality.sh && ./check-quality.sh

clear

# === Define color codes ===
BLUE_BG="\033[44m"
GREEN_BG="\033[42m"
RED_BG="\033[41m"
WHITE_TEXT="\033[97m"
RESET="\033[0m"

# === Define print helpers ===
print_blue() {
    echo -e "${BLUE_BG}${WHITE_TEXT}>>> $1${RESET}"
}

print_green() {
    echo -e "${GREEN_BG}${WHITE_TEXT}>>> $1${RESET}"
}

print_error() {
    echo -e "${RED_BG}${WHITE_TEXT}>>> ERROR: $1${RESET}"
    exit 1
}

# Activate the virtual environment (Windows-specific path)
. .venv/Scripts/activate

# === Run Black to format the code ===
print_blue "Running Black (code formatter)..."
black src/ tests/ || print_error "Black failed"

# === Run isort to sort imports ===
echo ""
print_blue "Running isort (import sorting)..."
isort src/ tests/ || print_error "isort failed"

# === Run flake8 to catch linting issues ===
echo ""
print_blue "Running flake8 (code style & errors)..."
flake8 src/ tests/ || print_error "flake8 found issues"

# === Run mypy for static type checking ===
echo ""
print_blue "Running mypy (type checking)..."
mypy --explicit-package-bases src/ tests/ || print_error "mypy found type issues"

# === Run py_compile to check for syntax errors ===
echo ""
print_blue "Checking syntax with py_compile..."
find src/ tests/ -name "*.py" -exec python -m py_compile {} \; || print_error "Syntax errors found"

# === All checks passed ===
echo ""
print_green "All code quality checks passed successfully!"