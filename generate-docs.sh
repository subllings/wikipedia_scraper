#!/bin/bash

# === generate-docs.sh ===
# Make this file executable: chmod +x generate-docs.sh
# Run it with: ./generate-docs.sh
# Or run both commands: chmod +x generate-docs.sh && ./generate-docs.sh

# -----------------------------------------------------------------------------
# Purpose: Generate HTML documentation with pdoc and open it automatically
# Compatible: Git Bash on Windows, pdoc ≥ 15
# -----------------------------------------------------------------------------

# Move to the root of the project (where this script is)
clear

# === Define color codes ===
BLUE_BG="\033[44m"
GREEN_BG="\033[42m"
RED_BG="\033[41m"
WHITE_TEXT="\033[97m"
BLACK_TEXT="\033[30m"
RESET="\033[0m"

# === Define print helpers ===
print_blue() {
    echo ""
    echo -e "${BLUE_BG}${WHITE_TEXT}>>> $1${RESET}"
    echo ""
}

print_green() {
    echo ""
    echo -e "${GREEN_BG}${WHITE_TEXT}>>> $1${RESET}"
    echo ""
}

print_error() {
    echo ""
    echo -e "${RED_BG}${WHITE_TEXT}>>> ERROR: $1${RESET}"
    echo ""
    exit 1
}

# Activate the virtual environment (Windows-specific path)
. .venv/Scripts/activate

# === Install pdoc if not installed ===
print_blue "Checking if pdoc is installed..."
if ! pip show pdoc > /dev/null 2>&1; then
    print_blue "'pdoc' is not installed. Attempting to install it..."
    pip install pdoc || print_error "Failed to install 'pdoc'"
    print_green "'pdoc' installed successfully."
fi

# === Move to script directory ===
cd "$(dirname "$0")" || print_error "Failed to navigate to script directory."

# === Configuration ===
OUTPUT_DIR="docs-pdoc"
TARGET_MODULE="src/leaders_scraper.py"

# === Ensure PYTHONPATH includes current project root ===
export PYTHONPATH=.

# === Remove previous output if any ===
print_blue "Cleaning previous documentation..."
rm -rf "$OUTPUT_DIR"

# === Generate documentation ===
print_blue "Generating documentation for: $TARGET_MODULE"
pdoc "$TARGET_MODULE" --output-dir "$OUTPUT_DIR" || print_error "Documentation generation failed."

# === Open the result ===
HTML_PATH="$OUTPUT_DIR/index.html"
if [ -f "$HTML_PATH" ]; then
    # --- Open documentation in default web browser
    print_green "Documentation successfully generated!"
    print_blue "Opening documentation in file explorer..."
    explorer.exe "$(cygpath -w "$OUTPUT_DIR")"

    # --- Open documentation in default web browser
    print_blue "Opening documentation in default web browser..."
    echo "Command: powershell.exe -Command Start-Process '$(cygpath -w "$HTML_PATH")'"
    powershell.exe -Command "Start-Process '$(cygpath -w "$HTML_PATH")'" \
        || print_error "Failed to open the default browser."

else
    print_error "Documentation not found. Something went wrong."
fi