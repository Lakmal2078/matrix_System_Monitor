#!/bin/bash

# MATRIX System Monitor - Installation Script
# This script installs the full-featured system monitor

echo "================================"
echo "🔥 MATRIX SYSTEM MONITOR v3.0 🔥"
echo "================================"
echo ""

# Check if running on appropriate OS
if [[ "$OSTYPE" != "linux-gnu"* && "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for Linux/macOS"
    exit 1
fi

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.6 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Install psutil
echo "Installing required packages..."
pip3 install psutil --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install psutil"
    exit 1
fi

echo "✓ psutil installed successfully"
echo ""

# Copy script to /usr/local/bin
SCRIPT_PATH="/usr/local/bin/pymonitor"
CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_FILE="$CURRENT_DIR/pymonitor_full.py"

if [ ! -f "$SOURCE_FILE" ]; then
    echo "❌ Source file not found: $SOURCE_FILE"
    exit 1
fi

echo "Installing pymonitor to /usr/local/bin..."
sudo cp "$SOURCE_FILE" "$SCRIPT_PATH"
sudo chmod +x "$SCRIPT_PATH"

if [ $? -ne 0 ]; then
    echo "❌ Failed to install pymonitor"
    exit 1
fi

echo "✓ pymonitor installed successfully"
echo ""

# Create bash alias
echo "Setting up command aliases..."

# Check shell configuration
if [ -f ~/.bashrc ]; then
    if ! grep -q "alias pymonitor=" ~/.bashrc; then
        echo "alias pymonitor='python3 $SCRIPT_PATH'" >> ~/.bashrc
        echo "✓ Added alias to ~/.bashrc"
    fi
fi

if [ -f ~/.zshrc ]; then
    if ! grep -q "alias pymonitor=" ~/.zshrc; then
        echo "alias pymonitor='python3 $SCRIPT_PATH'" >> ~/.zshrc
        echo "✓ Added alias to ~/.zshrc"
    fi
fi

echo ""
echo "================================"
echo "✅ Installation Complete!"
echo "================================"
echo ""
echo "Usage:"
echo "  pymonitor              - Start interactive menu"
echo "  pymonitor --monitor    - Start monitoring directly"
echo "  pymonitor --help       - Show help"
echo ""
echo "Log files will be saved to:"
echo "  ~/.system-monitor.log   (Text format)"
echo "  ~/.system-monitor.json  (JSON format)"
echo "  ~/.system-monitor.csv   (CSV format)"
echo ""
echo "⚠️  To see all system information, run with sudo:"
echo "  sudo pymonitor"
echo ""
echo "Type 'pymonitor' to start!"
echo ""
