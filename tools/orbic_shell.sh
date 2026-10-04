#!/bin/bash
# FOLC-V3 Enhanced Interactive Shell with tmux
# Provides a rich terminal UX for native host access
# Usage: ./orbic_shell.sh [--demo]

DEVICE="e830926d"
PORT=9999
SESSION_NAME="folc_orbic_$(date +%s)"
TMUX_SOCKET="/tmp/folc_tmux_${USER}"
DEMO_MODE=false

# Parse arguments
if [[ "$1" == "--demo" ]]; then
    DEMO_MODE=true
fi

# Colors for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              FOLC-V3 Orbic Interactive Shell                 ║"
    echo "║                  Enhanced Terminal Environment               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

check_dependencies() {
    local missing=()
    
    if ! command -v tmux &> /dev/null; then
        missing+=("tmux")
    fi
    
    if ! command -v adb &> /dev/null; then
        missing+=("adb")
    fi
    
    if ! command -v nc &> /dev/null && ! command -v netcat &> /dev/null; then
        missing+=("netcat")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}[ERROR]${NC} Missing dependencies: ${missing[*]}"
        echo -e "${YELLOW}[TIP]${NC} Install with: apt-get install ${missing[*]}"
        exit 1
    fi
}

setup_adb_forward() {
    echo -e "${BLUE}[INFO]${NC} Setting up ADB port forwarding..."
    
    if ! adb devices | grep -q "$DEVICE"; then
        echo -e "${RED}[ERROR]${NC} Device $DEVICE not found"
        echo -e "${YELLOW}[TIP]${NC} Available devices:"
        adb devices
        exit 1
    fi
    
    adb -s "$DEVICE" forward tcp:$PORT tcp:$PORT 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[SUCCESS]${NC} Port forwarding established (tcp:$PORT)"
    else
        echo -e "${RED}[ERROR]${NC} Failed to set up port forwarding"
        exit 1
    fi
}

test_connection() {
    echo -e "${BLUE}[INFO]${NC} Testing connection to native host..."
    
    if timeout 2 bash -c "echo '' | nc 127.0.0.1 $PORT" &>/dev/null; then
        echo -e "${GREEN}[SUCCESS]${NC} Native host is responsive"
        return 0
    else
        echo -e "${RED}[ERROR]${NC} Cannot connect to native host on port $PORT"
        echo -e "${YELLOW}[TIP]${NC} Ensure the native host daemon is running"
        exit 1
    fi
}

create_tmux_config() {
    local config_file="/tmp/folc_tmux.conf"
    
    cat > "$config_file" << 'EOF'
# FOLC-V3 tmux configuration
set -g status-style bg=colour235,fg=colour136
set -g status-left-length 40
set -g status-left "#[fg=colour166,bold]FOLC #[fg=colour245]│ #[fg=colour33]Session: #S #[fg=colour245]│ "
set -g status-right "#[fg=colour166]%H:%M:%S #[fg=colour245]│ #[fg=colour33]%Y-%m-%d"
set -g status-interval 1

# Pane borders
set -g pane-border-style fg=colour235
set -g pane-active-border-style fg=colour166

# Command/message line
set -g message-style bg=colour235,fg=colour166,bold

# Window status
setw -g window-status-current-style fg=colour166,bold
setw -g window-status-style fg=colour245

# Enable mouse support
set -g mouse on

# Vi mode
setw -g mode-keys vi

# Better history
set -g history-limit 50000

# Display messages for longer
set -g display-time 2000

# Prefix highlight
set -g status-left "#[fg=colour166,bold]⚡FOLC #[fg=colour245]│ #[fg=colour33]#S "
EOF
    
    echo "$config_file"
}

launch_interactive_shell() {
    local tmux_config=$(create_tmux_config)
    
    echo -e "${PURPLE}[LAUNCH]${NC} Starting interactive tmux session..."
    echo -e "${BLUE}[SESSION]${NC} Name: ${YELLOW}$SESSION_NAME${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Quick Reference:${NC}"
    echo -e "  ${GREEN}Ctrl+B then D${NC}  - Detach from session (keeps running)"
    echo -e "  ${GREEN}Ctrl+B then [${NC}  - Enter scroll mode (q to exit)"
    echo -e "  ${GREEN}Ctrl+B then ?${NC}  - Show all keybindings"
    echo -e "  ${GREEN}exit${NC}          - Close connection"
    echo ""
    echo -e "${YELLOW}Session Management:${NC}"
    echo -e "  ${GREEN}./orbic_shell_manager.sh list${NC}      - List sessions"
    echo -e "  ${GREEN}./orbic_shell_manager.sh attach${NC}    - Reconnect to session"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}Press ENTER to connect...${NC}"
    read
    
    # Create wrapper script for the connection
    local wrapper_script="/tmp/folc_shell_wrapper_$$.sh"
    cat > "$wrapper_script" << EOF
#!/bin/bash
echo -e "\033[1;32m[CONNECTED]\033[0m to Orbic Speed Native Host"
echo -e "\033[0;36m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo ""
nc 127.0.0.1 $PORT
echo ""
echo -e "\033[1;31m[DISCONNECTED]\033[0m from native host"
read -p "Press ENTER to close..."
EOF
    chmod +x "$wrapper_script"
    
    # Launch tmux with our config
    tmux -f "$tmux_config" -L "$TMUX_SOCKET" new-session -s "$SESSION_NAME" "$wrapper_script"
    
    # Cleanup
    rm -f "$wrapper_script" "$tmux_config"
    
    echo -e "${GREEN}[EXIT]${NC} Session closed"
}

show_fallback_shell() {
    echo -e "${YELLOW}[FALLBACK]${NC} Launching basic shell (tmux not available)"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[CONNECTED]${NC} to Orbic Speed Native Host"
    echo -e "${YELLOW}[TIP]${NC} Install tmux for enhanced terminal features"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    nc 127.0.0.1 $PORT
    
    echo ""
    echo -e "${RED}[DISCONNECTED]${NC} from native host"
}

cleanup() {
    echo -e "\n${BLUE}[CLEANUP]${NC} Closing session..."
    tmux -L "$TMUX_SOCKET" kill-session -t "$SESSION_NAME" 2>/dev/null
    rm -rf "/tmp/folc_shell_wrapper_*.sh" 2>/dev/null
}

main() {
    trap cleanup EXIT INT TERM
    
    print_banner
    
    if [ "$DEMO_MODE" = true ]; then
        echo -e "${YELLOW}[DEMO MODE]${NC} Running in demo mode (no device required)"
        echo -e "${BLUE}[INFO]${NC} This demonstrates the UI without connecting to a device"
        echo ""
    fi
    
    echo -e "${BLUE}[INIT]${NC} Checking dependencies..."
    check_dependencies
    
    if [ "$DEMO_MODE" = false ]; then
        setup_adb_forward
        test_connection
    else
        echo -e "${GREEN}[DEMO]${NC} Skipping device connection checks"
    fi
    
    echo ""
    
    if command -v tmux &> /dev/null; then
        if [ "$DEMO_MODE" = true ]; then
            echo -e "${YELLOW}[DEMO]${NC} In real mode, this would connect to the device"
            echo -e "${CYAN}[INFO]${NC} Run without --demo flag to connect to actual device"
            echo ""
            echo -e "${GREEN}Press ENTER to see tmux interface demo...${NC}"
            read
            
            # Show a demo shell instead of connecting
            local demo_script="/tmp/folc_demo_$$.sh"
            cat > "$demo_script" << 'DEMOEOF'
#!/bin/bash
echo -e "\033[1;33m╔══════════════════════════════════════════════════════╗\033[0m"
echo -e "\033[1;33m║             DEMO MODE - Not Connected                ║\033[0m"
echo -e "\033[1;33m╚══════════════════════════════════════════════════════╝\033[0m"
echo ""
echo "This is a demonstration of the tmux interface."
echo "In real mode, you would see the Orbic native host shell here."
echo ""
echo "Try these features:"
echo "  - Scroll up/down with mouse"
echo "  - Press Ctrl+B then [ to enter scroll mode"
echo "  - Press Ctrl+B then D to detach"
echo "  - Type 'exit' or press Ctrl+C to close"
echo ""
bash
DEMOEOF
            chmod +x "$demo_script"
            
            local tmux_config=$(create_tmux_config)
            tmux -f "$tmux_config" -L "$TMUX_SOCKET" new-session -s "$SESSION_NAME" "$demo_script"
            rm -f "$demo_script" "$tmux_config"
        else
            launch_interactive_shell
        fi
    else
        show_fallback_shell
    fi
}

# Run main function
main
