#!/bin/bash
# Project structure verification script
# Ensures all expected files are in place

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "FOLC-V3 Project Structure Verification"
echo "======================================="
echo ""

ERRORS=0
WARNINGS=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1 (missing)"
        ((ERRORS++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
    else
        echo -e "${RED}✗${NC} $1/ (missing)"
        ((ERRORS++))
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 (executable)"
    else
        echo -e "${YELLOW}⚠${NC} $1 (not executable)"
        ((WARNINGS++))
    fi
}

echo "Checking directory structure..."
check_dir "src"
check_dir "src/core"
check_dir "src/ui"
check_dir "exploits"
check_dir "tools"
check_dir "config"
check_dir "docs"
check_dir "archive"

echo ""
echo "Checking core documentation..."
check_file "README.md"
check_file "LICENSE"
check_file "INSTALL.md"
check_file "SECURITY.md"
check_file "CONTRIBUTING.md"
check_file "requirements.txt"
check_file ".gitignore"

echo ""
echo "Checking source files..."
check_file "src/core/foac_core.py"
check_file "src/ui/foac_ui_v6.py"

echo ""
echo "Checking exploit files..."
check_file "exploits/wrapper_v4.sh"
check_file "exploits/wrapper_v3.sh"
check_file "exploits/wrapper_v2.sh"
check_file "exploits/rayhunter_wrapper.sh"

echo ""
echo "Checking tool scripts..."
check_file "tools/setup.sh"
check_file "tools/deploy_foac.sh"
check_file "tools/orbic_manager.py"
check_file "tools/install_toolkit.sh"
check_file "tools/enter_alpine.sh"
check_file "tools/start_foac_v2.sh"

echo ""
echo "Checking executables..."
check_executable "tools/setup.sh"
check_executable "tools/deploy_foac.sh"
check_executable "tools/orbic_manager.py"

echo ""
echo "Checking configuration..."
check_file "config/wifi_setup.conf"
check_file "config/tinyproxy.conf"

echo ""
echo "Checking documentation..."
check_file "docs/ROADMAP.md"
check_file "docs/TROUBLESHOOTING.md"
check_file "docs/QUICK_REFERENCE.md"
check_file "docs/PROJECT_SUMMARY.md"
check_file "docs/ORBIC_ARCH.md"
check_file "docs/ORBIC_SYSTEM_ANALYSIS.md"
check_file "docs/orbic_research.md"

echo ""
echo "======================================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warnings (non-critical)${NC}"
    exit 0
else
    echo -e "${RED}✗ $ERRORS errors found${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ $WARNINGS warnings${NC}"
    fi
    exit 1
fi
