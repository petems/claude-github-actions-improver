#!/bin/bash
# GitHub Actions Improver - Automated Demo Script for asciicinema
# Usage: ./create-demo.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Demo configuration
DEMO_SPEED=1.5  # Typing speed multiplier
PAUSE_SHORT=1   # Short pause (seconds)
PAUSE_LONG=3    # Long pause (seconds)

# Simulate typing with delays
type_text() {
    local text="$1"
    local delay="${2:-0.05}"  # Default delay between characters
    
    for (( i=0; i<${#text}; i++ )); do
        printf "${text:$i:1}"
        sleep "$delay"
    done
    echo
}

# Simulate command execution with realistic output
simulate_command() {
    local prompt="$1"
    local command="$2"
    local simulate_output="$3"
    
    echo -e "${CYAN}$prompt${NC}"
    type_text "$command" 0.03
    sleep 0.5
    
    if [[ "$simulate_output" == "true" ]]; then
        case "$command" in
            "pwd")
                echo "/Users/demo/failing-repo"
                ;;
            "ls -la .github/workflows/")
                echo "total 32"
                echo "-rw-r--r--  1 demo  staff  1234 Jan  1 12:00 ci.yml"
                echo "-rw-r--r--  1 demo  staff   890 Jan  1 12:00 broken-test.yml"
                echo "-rw-r--r--  1 demo  staff   567 Jan  1 12:00 security.yml"
                ;;
            "gh run list --limit 5")
                echo -e "${RED}✗${NC} CI                  failing  main  1234567  1h"
                echo -e "${RED}✗${NC} Tests               failing  main  1234568  2h" 
                echo -e "${RED}✗${NC} Security Scan       failing  main  1234569  3h"
                echo -e "${RED}✗${NC} CI                  failing  main  1234570  1d"
                echo -e "${RED}✗${NC} Tests               failing  main  1234571  1d"
                ;;
        esac
    fi
    sleep "$PAUSE_SHORT"
}

# Simulate Claude CLI interactive session
simulate_claude_session() {
    echo -e "${PURPLE}Starting Claude CLI...${NC}"
    sleep 2
    
    echo -e "${BLUE}Claude CLI v2.1.0${NC}"
    echo -e "${BLUE}Type /help for available commands${NC}"
    echo
    
    # Simulate /gha:analyze command
    echo -e "${CYAN}> ${NC}"
    type_text "/gha:analyze" 0.08
    echo
    sleep 1
    
    echo -e "${YELLOW}🎯 GitHub Actions Comprehensive Analysis${NC}"
    echo
    sleep 1
    
    # Phase 1: Workflow Discovery
    echo -e "${BLUE}Phase 1: Workflow Discovery${NC}"
    simulate_progress_bar "Scanning workflows" 3
    echo -e "${GREEN}✅ Found 3 workflows: ci.yml, broken-test.yml, security.yml${NC}"
    echo
    
    # Phase 2: Historical Analysis  
    echo -e "${BLUE}Phase 2: Historical Analysis (Last 7 Days)${NC}"
    simulate_progress_bar "Analyzing workflow runs" 4
    echo -e "${RED}❌ Success Rate: 0% (8/8 failed runs)${NC}"
    echo -e "${YELLOW}⚠️  Failure Pattern Detected: Missing test infrastructure${NC}"
    echo
    
    # Phase 3: Pattern Recognition
    echo -e "${BLUE}Phase 3: Pattern Recognition${NC}"
    simulate_progress_bar "Analyzing error patterns" 3
    echo -e "${GREEN}🔍 Identified 3 primary failure patterns:${NC}"
    echo -e "   • Missing tests/ directory (Confidence: 0.96)"
    echo -e "   • Incomplete requirements.txt (Confidence: 0.89)" 
    echo -e "   • Demo workflows causing noise (Confidence: 0.92)"
    echo
    
    # Phase 4: Recommendations
    echo -e "${BLUE}Phase 4: Fix Recommendations${NC}"
    echo -e "${GREEN}📋 Recommended Actions:${NC}"
    echo -e "   1. Create test infrastructure with pytest"
    echo -e "   2. Update requirements.txt with test dependencies"
    echo -e "   3. Remove problematic demo workflows"
    echo -e "   4. Update to SHA-pinned actions for security"
    echo
    sleep 2
    
    # Simulate /gha:fix command
    echo -e "${CYAN}> ${NC}"
    type_text "/gha:fix --days 7 --auto" 0.08
    echo
    sleep 1
    
    echo -e "${YELLOW}🔧 GitHub Actions Failure Analysis & Automated Fixing${NC}"
    echo
    
    # Analysis Results Box
    echo "┌─────────────────────────────────────────────┐"
    echo "│ Found 8 workflow runs with 0% success rate │"
    echo "│ Identified 3 primary failure patterns      │" 
    echo "│ Confidence Score: 0.94 (Very High)         │"
    echo "└─────────────────────────────────────────────┘"
    echo
    sleep 2
    
    echo -e "${RED}🔍 Root Cause Analysis:${NC}"
    echo -e "${RED}✗${NC} Missing test infrastructure (tests/ directory)"
    echo -e "${RED}✗${NC} Incomplete dependencies in requirements.txt"
    echo -e "${RED}✗${NC} Demo workflows causing noise and confusion"
    echo
    sleep 1
    
    echo -e "${GREEN}🔧 Applying Automated Fixes:${NC}"
    
    # Animated progress bar for fixes
    echo -n "["
    for i in {1..32}; do
        echo -n "█"
        sleep 0.1
    done
    echo "] 100%"
    echo
    
    # Show fixes being applied
    echo -e "${GREEN}✅ Created test infrastructure with 6 test cases${NC}"
    sleep 0.8
    echo -e "${GREEN}✅ Updated requirements.txt with pytest, flake8, coverage${NC}"
    sleep 0.8
    echo -e "${GREEN}✅ Removed problematic demo workflows${NC}"
    sleep 0.8
    echo -e "${GREEN}✅ Updated ci.yml with SHA-pinned actions (security)${NC}"
    sleep 0.8
    echo -e "${GREEN}✅ Applied 2 additional fixes based on pattern analysis${NC}"
    echo
    sleep 1
    
    echo -e "${CYAN}📈 Expected Result: 0% → 95% success rate improvement${NC}"
    echo
    echo -e "${GREEN}🎉 Automated fixing complete! All tests now pass.${NC}"
    echo
    sleep 2
    
    # Exit Claude CLI
    echo -e "${CYAN}> ${NC}"
    type_text "exit" 0.08
    echo
    sleep 1
}

# Simulate progress bar
simulate_progress_bar() {
    local message="$1"
    local duration="$2"
    local width=30
    
    echo -n "$message: ["
    
    for ((i=0; i<=width; i++)); do
        echo -n "█"
        sleep $(echo "scale=2; $duration / $width" | bc -l)
    done
    
    echo "] Done"
    sleep 0.5
}

# Main demo script
main_demo() {
    clear
    echo -e "${PURPLE}🎬 GitHub Actions Improver Demo${NC}"
    echo -e "${PURPLE}Intelligent Failure Analysis & Automated Fixing${NC}"
    echo
    sleep 2
    
    echo -e "${BLUE}📁 Current Repository Status:${NC}"
    simulate_command "\$ " "pwd" true
    simulate_command "\$ " "ls -la .github/workflows/" true
    echo
    
    echo -e "${BLUE}📊 Recent Workflow Runs:${NC}"
    simulate_command "\$ " "gh run list --limit 5" true
    echo
    sleep 2
    
    echo -e "${RED}❌ All workflows are failing! Let's fix this...${NC}"
    echo
    sleep 2
    
    simulate_claude_session
    
    echo -e "${BLUE}🎯 Verification - Let's check the results:${NC}"
    echo
    
    simulate_command "\$ " "git status" false
    echo "On branch main"
    echo "Changes not staged for commit:"
    echo -e "  ${GREEN}modified:   .github/workflows/ci.yml${NC}"
    echo -e "  ${GREEN}modified:   requirements.txt${NC}"
    echo -e "  ${RED}deleted:    .github/workflows/broken-test.yml${NC}"
    echo
    echo "Untracked files:"
    echo -e "  ${GREEN}tests/${NC}"
    echo
    sleep 2
    
    simulate_command "\$ " "python3 -m pytest tests/ -v" false
    echo "========================= test session starts =========================="
    echo "collecting ... collected 6 items"
    echo
    echo -e "tests/test_basic.py::TestBasicFunctionality::test_python_environment ${GREEN}PASSED${NC}"
    echo -e "tests/test_basic.py::TestBasicFunctionality::test_project_structure ${GREEN}PASSED${NC}"
    echo -e "tests/test_basic.py::TestBasicFunctionality::test_workflows_exist ${GREEN}PASSED${NC}"
    echo -e "tests/test_basic.py::TestToolFunctionality::test_failure_analyzer_exists ${GREEN}PASSED${NC}"
    echo -e "tests/test_basic.py::TestToolFunctionality::test_requirements_parseable ${GREEN}PASSED${NC}"
    echo -e "tests/test_basic.py::TestBasicFunctionality::test_basic_imports ${GREEN}PASSED${NC}"
    echo
    echo -e "${GREEN}========================== 6 passed in 0.12s ==========================${NC}"
    echo
    sleep 2
    
    echo -e "${GREEN}🎉 Success! From 0% to 100% test pass rate!${NC}"
    echo
    echo -e "${CYAN}Key Features Demonstrated:${NC}"
    echo -e "• ${GREEN}Pattern Recognition${NC}: 15+ error types with 94% confidence"
    echo -e "• ${GREEN}Root Cause Analysis${NC}: Identified missing test infrastructure"
    echo -e "• ${GREEN}Automated Fixes${NC}: Applied 5 targeted fixes automatically"
    echo -e "• ${GREEN}Real-time Feedback${NC}: Interactive progress bars and updates"
    echo -e "• ${GREEN}Multi-threading${NC}: Concurrent processing capabilities"
    echo
    echo -e "${PURPLE}Learn more: https://github.com/petems/claude-github-actions-improver${NC}"
    echo
}

# Check dependencies
check_dependencies() {
    if ! command -v bc &> /dev/null; then
        echo "Installing bc for calculations..."
        brew install bc 2>/dev/null || echo "Please install bc: brew install bc"
    fi
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_dependencies
    
    if [[ "$1" == "--record" ]]; then
        echo "Starting asciicinema recording..."
        echo "The demo will start in 3 seconds..."
        sleep 3
        asciinema rec github-actions-demo.cast -c "./create-demo.sh --play"
    elif [[ "$1" == "--play" ]]; then
        main_demo
    else
        echo "GitHub Actions Improver - Demo Script"
        echo ""
        echo "Usage:"
        echo "  ./create-demo.sh --record    # Record with asciicinema"
        echo "  ./create-demo.sh --play      # Just run the demo"
        echo ""
        echo "This will create 'github-actions-demo.cast' that can be:"
        echo "• Played back with: asciinema play github-actions-demo.cast"
        echo "• Embedded in web pages: asciinema upload github-actions-demo.cast"
        echo "• Converted to GIF: agg github-actions-demo.cast demo.gif"
    fi
fi