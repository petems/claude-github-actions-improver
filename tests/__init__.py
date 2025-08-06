# GitHub Actions Improver Test Suite

"""
Test suite for GitHub Actions Improver project

Includes tests for:
- Core functionality (enhanced concurrent fixer, failure analyzer)
- Token setup and configuration management
- API limit handling and secure configuration
- New GHA jobs commands (status, investigate, fix-failed-ngu)
- Integration tests for complete workflows

Run tests with:
    python -m pytest tests/
    python run_all_tests.py
    python run_all_tests.py --coverage
"""

# Test imports
from .test_gha_jobs_commands import *
from .integration_test_gha_jobs import *