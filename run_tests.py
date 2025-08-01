#!/usr/bin/env python3
"""
Test runner for GitHub Actions Improver and WGU Fighter
Runs unit tests, integration tests, and generates coverage reports
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_basic_tests():
    """Run basic functionality tests"""
    print("🔧 Running basic functionality tests...")
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_basic.py", 
        "-v", "--tb=short"
    ], capture_output=False)
    
    return result.returncode == 0

def run_wgu_unit_tests():
    """Run WGU fighter unit tests"""
    print("\n🥊 Running WGU Fighter unit tests...")
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_wgu_fighter.py", 
        "-v", "--tb=short"
    ], capture_output=False)
    
    return result.returncode == 0

def run_wgu_integration_tests():
    """Run WGU fighter integration tests"""
    print("\n🚀 Running WGU Fighter integration tests...")
    
    result = subprocess.run([
        sys.executable, "tests/integration_test_wgu.py"
    ], capture_output=False)
    
    return result.returncode == 0

def run_with_coverage():
    """Run all tests with coverage reporting"""
    print("📊 Running tests with coverage analysis...")
    
    # Install coverage if not available
    try:
        import coverage
    except ImportError:
        print("Installing coverage package...")
        subprocess.run([sys.executable, "-m", "pip", "install", "coverage"], check=True)
        
    # Run tests with coverage
    commands = [
        [sys.executable, "-m", "coverage", "run", "--source=.", "-m", "pytest", "tests/test_basic.py", "tests/test_wgu_fighter.py"],
        [sys.executable, "-m", "coverage", "report", "-m"],
        [sys.executable, "-m", "coverage", "html", "--directory=coverage_html"]
    ]
    
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            return False
            
    print("\n📋 Coverage report generated in coverage_html/")
    return True

def run_lint_check():
    """Run code quality checks"""
    print("\n🔍 Running code quality checks...")
    
    try:
        # Check if flake8 is available
        result = subprocess.run([sys.executable, "-m", "flake8", "--version"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("Installing flake8...")
            subprocess.run([sys.executable, "-m", "pip", "install", "flake8"], check=True)
        
        # Run flake8 on WGU fighter
        result = subprocess.run([
            sys.executable, "-m", "flake8", 
            "wgu-fighter.py", "tests/test_wgu_fighter.py",
            "--max-line-length=120",
            "--ignore=E501,W503"  # Ignore long lines and line break before binary operator
        ], capture_output=False)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"⚠️ Lint check failed: {e}")
        return False

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="GitHub Actions Improver Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage reporting")
    parser.add_argument("--lint", action="store_true", help="Run code quality checks")
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")
    
    args = parser.parse_args()
    
    # Default to running all if no specific test type specified
    if not any([args.unit, args.integration, args.coverage, args.lint]):
        args.all = True
    
    print("🎯 GitHub Actions Improver & WGU Fighter Test Suite")
    print("=" * 60)
    
    success = True
    
    # Run basic tests
    if args.all or args.unit:
        if not run_basic_tests():
            success = False
    
    # Run WGU unit tests
    if args.all or args.unit:
        if not run_wgu_unit_tests():
            success = False
    
    # Run integration tests
    if args.all or args.integration:
        if not run_wgu_integration_tests():
            success = False
    
    # Run with coverage
    if args.coverage or args.all:
        if not run_with_coverage():
            success = False
    
    # Run lint checks
    if args.lint or args.all:
        if not run_lint_check():
            success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! The WGU Fighter is battle-ready! (ง'̀-'́)ง")
        print("✅ Ready for deployment and real-world GitHub Actions battles!")
    else:
        print("❌ Some tests failed. Please review the output above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())