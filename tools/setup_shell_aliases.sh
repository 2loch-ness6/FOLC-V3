#!/bin/bash
# Quick alias installer for FOLC-V3 Shell Tools
# Source this file or run it to add convenient aliases

TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define aliases
ALIASES="
# FOLC-V3 Orbic Shell Aliases
alias folc-shell='${TOOLS_DIR}/orbic_shell.sh'
alias folc-sessions='${TOOLS_DIR}/orbic_shell_manager.sh list'
alias folc-attach='${TOOLS_DIR}/orbic_shell_manager.sh attach'
alias folc-kill='${TOOLS_DIR}/orbic_shell_manager.sh kill'
"

echo "FOLC-V3 Shell Aliases Installer"
echo "================================"
echo ""
echo "Available aliases:"
echo "  folc-shell     - Launch interactive Orbic shell"
echo "  folc-sessions  - List all active sessions"
echo "  folc-attach    - Attach to a session"
echo "  folc-kill      - Kill a session"
echo ""

# Check if running in interactive shell
if [ -t 0 ]; then
    echo "Add these aliases to your ~/.bashrc? [y/N]"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # Check if aliases already exist
        if grep -q "# FOLC-V3 Orbic Shell Aliases" ~/.bashrc 2>/dev/null; then
            echo "Aliases already exist in ~/.bashrc"
        else
            echo "$ALIASES" >> ~/.bashrc
            echo "✓ Aliases added to ~/.bashrc"
            echo ""
            echo "Run 'source ~/.bashrc' or start a new terminal to use them"
        fi
    else
        echo "Skipped. You can manually add these aliases:"
        echo "$ALIASES"
    fi
else
    # Non-interactive, just output the aliases
    echo "$ALIASES"
fi
