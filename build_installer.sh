#!/bin/bash

# PNG to JPEG Converter - macOS Installer Build Script
# =====================================================
# This script builds the .app bundle and creates a DMG installer.
#
# IMPORTANT: This script MUST be run on macOS.
# It will not work on Linux or Windows.
#
# Prerequisites:
#   - macOS 10.13 or later
#   - Python 3.8+ with tkinter support (python.org installer recommended)
#   - pip (Python package manager)
#
# Optional:
#   - create-dmg (brew install create-dmg) for prettier DMG
#   - Custom AppIcon.icns in the project directory
#
# Usage:
#   chmod +x build_installer.sh
#   ./build_installer.sh

set -e  # Exit on any error

# Configuration
APP_NAME="PNG to JPEG Converter"
APP_NAME_NOSPACE="PNG2JPGConverter"
VERSION="1.0.0"
DMG_NAME="PNG-to-JPEG-Converter-${VERSION}.dmg"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=============================================="
echo "  Building ${APP_NAME} v${VERSION}"
echo "=============================================="
echo ""

# Step 0: Verify we're on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${RED}ERROR: This script must be run on macOS.${NC}"
    echo "Current OS: $(uname)"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Running on macOS"

# Step 1: Verify Python and tkinter
echo ""
echo "Checking Python environment..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed.${NC}"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}[OK]${NC} ${PYTHON_VERSION}"

# Verify tkinter is available
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo -e "${RED}ERROR: tkinter is not available in your Python installation.${NC}"
    echo ""
    echo "This is common with Homebrew Python. Solutions:"
    echo "  1. Install Python from https://www.python.org/downloads/ (recommended)"
    echo "  2. Or run: brew install python-tk"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} tkinter is available"

# Step 2: Change to script directory
cd "${SCRIPT_DIR}"
echo -e "${GREEN}[OK]${NC} Working directory: ${SCRIPT_DIR}"

# Step 3: Verify required files exist
echo ""
echo "Checking required files..."

if [[ ! -f "png2jpg_gui.py" ]]; then
    echo -e "${RED}ERROR: png2jpg_gui.py not found${NC}"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} png2jpg_gui.py"

if [[ ! -f "png2jpg.py" ]]; then
    echo -e "${RED}ERROR: png2jpg.py not found${NC}"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} png2jpg.py"

if [[ ! -f "PNG2JPG.spec" ]]; then
    echo -e "${RED}ERROR: PNG2JPG.spec not found${NC}"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} PNG2JPG.spec"

# Check for optional icon
if [[ -f "AppIcon.icns" ]]; then
    echo -e "${GREEN}[OK]${NC} AppIcon.icns (custom icon found)"
else
    echo -e "${YELLOW}[INFO]${NC} No AppIcon.icns found - using default icon"
fi

# Step 4: Clean previous builds
echo ""
echo "Cleaning previous builds..."
rm -rf build dist *.dmg dmg_temp 2>/dev/null || true
echo -e "${GREEN}[OK]${NC} Cleaned"

# Step 5: Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
pip3 install --upgrade pyinstaller pillow --quiet
echo -e "${GREEN}[OK]${NC} Dependencies installed"

# Step 6: Build .app with PyInstaller
echo ""
echo "Building .app bundle (this may take a minute)..."
pyinstaller PNG2JPG.spec --noconfirm

# Verify .app was created
if [[ ! -d "dist/${APP_NAME}.app" ]]; then
    echo -e "${RED}ERROR: .app bundle was not created!${NC}"
    echo "Check the PyInstaller output above for errors."
    exit 1
fi
echo -e "${GREEN}[OK]${NC} .app bundle created: dist/${APP_NAME}.app"

# Step 7: Create DMG installer
echo ""
echo "Creating DMG installer..."

# Create temporary folder for DMG contents
mkdir -p dmg_temp
cp -R "dist/${APP_NAME}.app" "dmg_temp/"
ln -s /Applications "dmg_temp/Applications"

# Check if create-dmg is available
if command -v create-dmg &> /dev/null; then
    echo "Using create-dmg for prettier installer..."
    
    # Build create-dmg arguments
    CREATE_DMG_ARGS=(
        --volname "${APP_NAME}"
        --window-pos 200 120
        --window-size 600 400
        --icon-size 100
        --icon "${APP_NAME}.app" 150 185
        --hide-extension "${APP_NAME}.app"
        --app-drop-link 450 185
    )
    
    # Add volume icon if available
    if [[ -f "AppIcon.icns" ]]; then
        CREATE_DMG_ARGS+=(--volicon "AppIcon.icns")
    fi
    
    # Create DMG (create-dmg may return non-zero even on success due to warnings)
    set +e
    create-dmg "${CREATE_DMG_ARGS[@]}" "${DMG_NAME}" "dmg_temp/"
    CREATE_DMG_EXIT=$?
    set -e
    
    # Check if DMG was created despite exit code
    if [[ ! -f "${DMG_NAME}" ]]; then
        echo -e "${YELLOW}[WARN]${NC} create-dmg failed, falling back to hdiutil..."
        hdiutil create -volname "${APP_NAME}" \
            -srcfolder dmg_temp \
            -ov -format UDZO \
            "${DMG_NAME}"
    fi
else
    echo "create-dmg not found, using hdiutil..."
    hdiutil create -volname "${APP_NAME}" \
        -srcfolder dmg_temp \
        -ov -format UDZO \
        "${DMG_NAME}"
fi

# Clean up temp folder
rm -rf dmg_temp

# Verify DMG was created
if [[ ! -f "${DMG_NAME}" ]]; then
    echo -e "${RED}ERROR: DMG was not created!${NC}"
    exit 1
fi

# Step 8: Show results
echo ""
echo "=============================================="
echo -e "  ${GREEN}Build Complete!${NC}"
echo "=============================================="
echo ""
echo "App Bundle:    dist/${APP_NAME}.app"
echo "DMG Installer: ${DMG_NAME}"
echo "DMG Size:      $(du -h "${DMG_NAME}" | cut -f1)"
echo ""
echo "To test the app:"
echo "  open \"dist/${APP_NAME}.app\""
echo ""
echo "To test the DMG:"
echo "  open \"${DMG_NAME}\""
echo ""
echo -e "${YELLOW}Note:${NC} The app is unsigned. On first launch, users may need to:"
echo "  1. Right-click the app and select 'Open'"
echo "  2. Or go to System Preferences > Security & Privacy and click 'Open Anyway'"
echo ""
echo "Architecture: $(uname -m)"
if [[ "$(uname -m)" == "arm64" ]]; then
    echo -e "${YELLOW}Note:${NC} This build is for Apple Silicon (M1/M2/M3) Macs."
    echo "For Intel Mac compatibility, build on an Intel Mac or use a universal2 Python."
else
    echo -e "${YELLOW}Note:${NC} This build is for Intel Macs."
    echo "For Apple Silicon compatibility, build on an Apple Silicon Mac."
fi
