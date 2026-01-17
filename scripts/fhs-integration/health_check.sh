#!/bin/bash
# FHS Integration System Health Check
# 系統健康檢查腳本
#
# Usage:
#     ./health_check.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FHS_TOOLS_DIR="$REPO_ROOT/workspace/tools/fhs-integration"

echo "================================="
echo "FHS Integration System Health Check"
echo "================================="
echo ""

CHECKS_PASSED=0
CHECKS_FAILED=0

# 檢查函數
check_component() {
    local name="$1"
    local command="$2"
    
    if eval "$command" &>/dev/null; then
        echo -e "${GREEN}✓${NC} $name"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $name"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Python 可用性
check_component "Python 3 available" "command -v python3"

# FHS 目錄
check_component "bin/ directory exists" "test -d $REPO_ROOT/bin"
check_component "sbin/ directory exists" "test -d $REPO_ROOT/sbin"
check_component "lib/ directory exists" "test -d $REPO_ROOT/lib"
check_component "etc/ directory exists" "test -d $REPO_ROOT/etc"

# 工具文件
check_component "maturity_assessor.py exists" "test -f $FHS_TOOLS_DIR/maturity_assessor.py"
check_component "fhs_integrator.py exists" "test -f $FHS_TOOLS_DIR/fhs_integrator.py"
check_component "fhs_validator.py exists" "test -f $FHS_TOOLS_DIR/fhs_validator.py"
check_component "fhs_automation_master.py exists" "test -f $FHS_TOOLS_DIR/fhs_automation_master.py"

# 功能測試
check_component "Maturity assessor runs" "python3 $FHS_TOOLS_DIR/maturity_assessor.py --help"
check_component "FHS integrator runs" "python3 $FHS_TOOLS_DIR/fhs_integrator.py --help"
check_component "FHS validator runs" "python3 $FHS_TOOLS_DIR/fhs_validator.py --help"
check_component "Automation master runs" "python3 $FHS_TOOLS_DIR/fhs_automation_master.py --help"

# Git 狀態
check_component "Git repository clean" "git diff-index --quiet HEAD --"

echo ""
echo "================================="
echo "Summary:"
echo "  Passed: $CHECKS_PASSED"
echo "  Failed: $CHECKS_FAILED"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ System Health: GOOD${NC}"
    exit 0
else
    echo -e "${RED}✗ System Health: ISSUES DETECTED${NC}"
    exit 1
fi
