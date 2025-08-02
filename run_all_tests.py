#!/usr/bin/env python3
"""
Test runner for all GitHub Actions Improver tests
Runs unit tests, integration tests, and generates coverage reports
"""

import sys
import unittest
import os
import subprocess
from pathlib import Path
import time

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_test_suite(test_pattern=None, verbose=True):
    """Run the complete test suite"""
    test_dir = project_root / "tests"
    
    # Discover and run tests
    loader = unittest.TestLoader()
    
    if test_pattern:
        # Run specific test pattern
        suite = loader.discover(test_dir, pattern=test_pattern)
    else:
        # Run all tests
        suite = loader.discover(test_dir, pattern="test_*.py")
    
    # Run tests
    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        buffer=True,
        failfast=False
    )
    
    print(f"🧪 Running tests from {test_dir}")
    print("=" * 70)
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("=" * 70)
    print(f"⏱️  Tests completed in {end_time - start_time:.2f} seconds")
    print(f"🧪 Tests run: {result.testsRun}")
    print(f"✅ Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.failures:
        print(f"❌ Failures: {len(result.failures)}")
        for test, traceback in result.failures:
            print(f"   - {test}")
    
    if result.errors:
        print(f"💥 Errors: {len(result.errors)}")
        for test, traceback in result.errors:
            print(f"   - {test}")
    
    if result.skipped:
        print(f"⏭️  Skipped: {len(result.skipped)}")
    
    return result.wasSuccessful()


def run_with_coverage():
    """Run tests with coverage reporting"""
    try:
        import coverage
    except ImportError:
        print("❌ Coverage module not available. Install with: pip install coverage")
        return False
    
    print("📊 Running tests with coverage analysis...")
    
    # Initialize coverage
    cov = coverage.Coverage(
        source=[str(project_root)],
        omit=[
            "*/tests/*",
            "*/test_*",
            "*/__pycache__/*",
            "*/venv/*",
            "*/env/*",
            "setup.py",
            "run_all_tests.py"
        ]
    )
    
    cov.start()
    
    try:
        # Run tests
        success = run_test_suite()
        
        cov.stop()
        cov.save()
        
        # Generate coverage report
        print("\n📊 Coverage Report:")
        print("=" * 70)
        cov.report(show_missing=True)
        
        # Generate HTML coverage report
        html_dir = project_root / "htmlcov"
        cov.html_report(directory=str(html_dir))
        print(f"\n📁 HTML coverage report generated: {html_dir}/index.html")
        
        return success
        
    except Exception as e:
        cov.stop()
        print(f"❌ Error running coverage: {e}")
        return False


def run_specific_tests():
    """Run specific test categories"""
    print("🎯 Available test categories:")
    print("1. Unit tests only (test_*.py)")
    print("2. Integration tests only (integration_*.py)")
    print("3. GHA Jobs commands tests")
    print("4. All tests")
    print("5. All tests with coverage")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        return run_test_suite("test_*.py")
    elif choice == "2":
        return run_test_suite("integration_*.py")
    elif choice == "3":
        return run_test_suite("*gha_jobs*.py")
    elif choice == "4":
        return run_test_suite()
    elif choice == "5":
        return run_with_coverage()
    else:
        print("❌ Invalid choice")
        return False


def check_test_environment():
    """Check if test environment is properly set up"""
    print("🔍 Checking test environment...")
    
    required_modules = [
        "unittest", "json", "subprocess", "tempfile", "pathlib",
        "datetime", "dataclasses", "typing", "enum", "logging"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        return False
    
    # Check if GitHub CLI is available (for integration tests)
    try:
        result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ GitHub CLI available: {result.stdout.split()[0]}")
        else:
            print("⚠️  GitHub CLI not available - some integration tests may be skipped")
    except FileNotFoundError:
        print("⚠️  GitHub CLI not found - some integration tests may be skipped")
    
    # Check if git is available
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git available: {result.stdout.strip()}")
        else:
            print("❌ Git not available - integration tests may fail")
            return False
    except FileNotFoundError:
        print("❌ Git not found - integration tests may fail")
        return False
    
    print("✅ Test environment looks good!")
    return True


def main():
    """Main test runner function"""
    print("🚀 GitHub Actions Improver Test Suite")
    print("=" * 70)
    
    # Check environment
    if not check_test_environment():
        print("❌ Environment check failed")
        return 1
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ["--help", "-h"]:
            print("""
Usage: python run_all_tests.py [options]

Options:
  --unit           Run only unit tests
  --integration    Run only integration tests  
  --gha-jobs       Run only GHA jobs command tests
  --coverage       Run all tests with coverage
  --interactive    Interactive test selection
  --help, -h       Show this help
  
Without arguments: Run all tests
""")
            return 0
        elif arg == "--unit":
            success = run_test_suite("test_*.py")
        elif arg == "--integration":
            success = run_test_suite("integration_*.py")
        elif arg == "--gha-jobs":
            success = run_test_suite("*gha_jobs*.py")
        elif arg == "--coverage":
            success = run_with_coverage()
        elif arg == "--interactive":
            success = run_specific_tests()
        else:
            print(f"❌ Unknown argument: {arg}")
            return 1
    else:
        # Default: run all tests
        success = run_test_suite()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())