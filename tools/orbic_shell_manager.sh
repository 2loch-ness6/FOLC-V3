#!/bin/bash
# FOLC-V3 Shell Session Manager
# Manage and reconnect to tmux sessions

TMUX_SOCKET="/tmp/folc_tmux_${USER}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

list_sessions() {
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              Active FOLC Shell Sessions                      ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if ! tmux -L "$TMUX_SOCKET" list-sessions 2>/dev/null; then
        echo -e "${YELLOW}[INFO]${NC} No active sessions found"
        return 1
    fi
    return 0
}

attach_session() {
    local session_name="$1"
    
    if [ -z "$session_name" ]; then
        echo -e "${RED}[ERROR]${NC} Please specify a session name"
        echo -e "${YELLOW}Usage:${NC} $0 attach <session_name>"
        return 1
    fi
    
    echo -e "${GREEN}[ATTACH]${NC} Reconnecting to session: $session_name"
    tmux -L "$TMUX_SOCKET" attach-session -t "$session_name"
}

kill_session() {
    local session_name="$1"
    
    if [ -z "$session_name" ]; then
        echo -e "${RED}[ERROR]${NC} Please specify a session name"
        echo -e "${YELLOW}Usage:${NC} $0 kill <session_name>"
        return 1
    fi
    
    echo -e "${YELLOW}[KILL]${NC} Terminating session: $session_name"
    tmux -L "$TMUX_SOCKET" kill-session -t "$session_name"
    echo -e "${GREEN}[SUCCESS]${NC} Session terminated"
}

kill_all() {
    echo -e "${YELLOW}[KILL]${NC} Terminating all FOLC sessions..."
    tmux -L "$TMUX_SOCKET" kill-server 2>/dev/null
    echo -e "${GREEN}[SUCCESS]${NC} All sessions terminated"
}

show_help() {
    echo -e "${CYAN}FOLC-V3 Shell Session Manager${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  $0 ${GREEN}list${NC}                    - List all active sessions"
    echo -e "  $0 ${GREEN}attach${NC} <session>        - Attach to a detached session"
    echo -e "  $0 ${GREEN}kill${NC} <session>          - Kill a specific session"
    echo -e "  $0 ${GREEN}kill-all${NC}                - Kill all sessions"
    echo -e "  $0 ${GREEN}help${NC}                    - Show this help"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  $0 list"
    echo -e "  $0 attach folc_orbic_1234567890"
    echo -e "  $0 kill folc_orbic_1234567890"
}

main() {
    local command="${1:-list}"
    
    case "$command" in
        list|ls)
            list_sessions
            ;;
        attach|a)
            attach_session "$2"
            ;;
        kill|k)
            kill_session "$2"
            ;;
        kill-all|ka)
            kill_all
            ;;
        help|h|-h|--help)
            show_help
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Unknown command: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
