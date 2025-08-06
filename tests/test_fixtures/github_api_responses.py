#!/usr/bin/env python3
"""
Test fixtures for GitHub Actions API responses
Provides mock data for testing the GHA jobs commands
"""

from datetime import datetime, timedelta
import json

def get_sample_runs_data():
    """Sample GitHub Actions runs data"""
    base_time = datetime.now()
    
    return [
        {
            "databaseId": 16679735137,
            "name": "CI",
            "status": "completed",
            "conclusion": "failure",
            "createdAt": (base_time - timedelta(hours=2)).isoformat() + "Z",
            "headBranch": "main",
            "event": "push",
            "url": "https://github.com/test/repo/actions/runs/16679735137"
        },
        {
            "databaseId": 16679735136,
            "name": "Security Scan",
            "status": "completed", 
            "conclusion": "failure",
            "createdAt": (base_time - timedelta(hours=3)).isoformat() + "Z",
            "headBranch": "feat/new-feature",
            "event": "pull_request",
            "url": "https://github.com/test/repo/actions/runs/16679735136"
        },
        {
            "databaseId": 16679735135,
            "name": "CI",
            "status": "completed",
            "conclusion": "success",
            "createdAt": (base_time - timedelta(hours=4)).isoformat() + "Z",
            "headBranch": "main", 
            "event": "push",
            "url": "https://github.com/test/repo/actions/runs/16679735135"
        },
        {
            "databaseId": 16679735134,
            "name": "Deploy",
            "status": "completed",
            "conclusion": "failure",
            "createdAt": (base_time - timedelta(days=1)).isoformat() + "Z",
            "headBranch": "main",
            "event": "push", 
            "url": "https://github.com/test/repo/actions/runs/16679735134"
        },
        {
            "databaseId": 16679735133,
            "name": "CI",
            "status": "completed",
            "conclusion": "cancelled",
            "createdAt": (base_time - timedelta(days=2)).isoformat() + "Z",
            "headBranch": "feat/test-branch",
            "event": "pull_request",
            "url": "https://github.com/test/repo/actions/runs/16679735133"
        }
    ]

def get_sample_log_npm_error():
    """Sample log with npm package.json error"""
    return """
2024-08-02T10:30:15.123Z ##[group]Run npm ci
2024-08-02T10:30:15.124Z shell: /usr/bin/bash -e {0}
2024-08-02T10:30:15.125Z env:
2024-08-02T10:30:15.126Z   NODE_VERSION: 18
2024-08-02T10:30:15.127Z ##[endgroup]
2024-08-02T10:30:15.500Z npm ERR! code ENOENT
2024-08-02T10:30:15.501Z npm ERR! syscall open
2024-08-02T10:30:15.502Z npm ERR! path /home/runner/work/project/project/package.json
2024-08-02T10:30:15.503Z npm ERR! errno -2
2024-08-02T10:30:15.504Z npm ERR! enoent ENOENT: no such file or directory, open '/home/runner/work/project/project/package.json'
2024-08-02T10:30:15.505Z npm ERR! enoent This is related to npm not being able to find a file.
2024-08-02T10:30:15.506Z npm ERR! enoent 
2024-08-02T10:30:15.507Z 
2024-08-02T10:30:15.508Z npm ERR! A complete log of this run can be found in:
2024-08-02T10:30:15.509Z npm ERR!     /home/runner/.npm/_logs/2024-08-02T10_30_15_510Z-debug-0.log
2024-08-02T10:30:15.510Z ##[error]Process completed with exit code 254.
"""

def get_sample_log_python_import_error():
    """Sample log with Python import error"""
    return """
2024-08-02T10:35:20.123Z ##[group]Run python -m pytest tests/
2024-08-02T10:35:20.124Z shell: /usr/bin/bash -e {0}
2024-08-02T10:35:20.125Z ##[endgroup]
2024-08-02T10:35:25.200Z ============================================ FAILURES ============================================
2024-08-02T10:35:25.201Z _______________________________ test_user_creation _______________________________
2024-08-02T10:35:25.202Z 
2024-08-02T10:35:25.203Z     def test_user_creation():
2024-08-02T10:35:25.204Z >       import requests
2024-08-02T10:35:25.205Z E       ModuleNotFoundError: No module named 'requests'
2024-08-02T10:35:25.206Z 
2024-08-02T10:35:25.207Z tests/test_api.py:15: ModuleNotFoundError
2024-08-02T10:35:25.208Z ==========================================  short test summary info ==========================================
2024-08-02T10:35:25.209Z FAILED tests/test_api.py::test_user_creation - ModuleNotFoundError: No module named 'requests'
2024-08-02T10:35:25.210Z =================================== 1 failed, 0 passed in 0.12s ===================================
2024-08-02T10:35:25.211Z ##[error]Process completed with exit code 1.
"""

def get_sample_log_test_assertion_error():
    """Sample log with test assertion failure"""
    return """
2024-08-02T10:40:10.123Z ##[group]Run python -m pytest tests/
2024-08-02T10:40:10.124Z shell: /usr/bin/bash -e {0}
2024-08-02T10:40:10.125Z ##[endgroup]
2024-08-02T10:40:15.300Z ============================================ FAILURES ============================================
2024-08-02T10:40:15.301Z _______________________________ test_calculation _______________________________
2024-08-02T10:40:15.302Z 
2024-08-02T10:40:15.303Z     def test_calculation():
2024-08-02T10:40:15.304Z         result = calculate_sum(2, 3)
2024-08-02T10:40:15.305Z >       assert result == 6
2024-08-02T10:40:15.306Z E       AssertionError: Expected 6 but got 5
2024-08-02T10:40:15.307Z 
2024-08-02T10:40:15.308Z tests/test_math.py:25: AssertionError
2024-08-02T10:40:15.309Z ==========================================  short test summary info ==========================================
2024-08-02T10:40:15.310Z FAILED tests/test_math.py::test_calculation - AssertionError: Expected 6 but got 5
2024-08-02T10:40:15.311Z =================================== 1 failed, 0 passed in 0.08s ===================================
2024-08-02T10:40:15.312Z ##[error]Process completed with exit code 1.
"""

def get_sample_log_docker_error():
    """Sample log with Docker permission error"""
    return """
2024-08-02T10:45:30.123Z ##[group]Run docker build -t myapp .
2024-08-02T10:45:30.124Z shell: /usr/bin/bash -e {0}
2024-08-02T10:45:30.125Z ##[endgroup]
2024-08-02T10:45:35.400Z Sending build context to Docker daemon  2.048kB
2024-08-02T10:45:35.401Z Step 1/5 : FROM node:18-alpine
2024-08-02T10:45:35.402Z  ---> 44f69ba09d19
2024-08-02T10:45:35.403Z Step 2/5 : WORKDIR /app
2024-08-02T10:45:35.404Z  ---> Using cache
2024-08-02T10:45:35.405Z  ---> 8f9b2f6c4d23
2024-08-02T10:45:35.406Z Step 3/5 : COPY package*.json ./
2024-08-02T10:45:35.407Z  ---> bf8a1c3e9f12
2024-08-02T10:45:35.408Z Step 4/5 : RUN npm ci
2024-08-02T10:45:35.409Z  ---> Running in a1b2c3d4e5f6
2024-08-02T10:45:40.500Z docker: Error response from daemon: pull access denied for private-registry/myapp, repository does not exist or may require 'docker login': permission denied
2024-08-02T10:45:40.501Z ##[error]Process completed with exit code 125.
"""

def get_sample_log_cache_warning():
    """Sample log with cache restore warning"""
    return """
2024-08-02T10:50:45.123Z ##[group]Restore cached dependencies
2024-08-02T10:50:45.124Z ##[endgroup]
2024-08-02T10:50:45.200Z ##[warning]Failed to restore cache entry. Request failed with status code 404, request id: a1b2c3d4-e5f6-7890-abcd-ef1234567890 (10 ms)
2024-08-02T10:50:45.201Z Cache not found for input keys: npm-cache-Linux-18-abc123def456
2024-08-02T10:50:45.202Z ##[group]Run npm ci
2024-08-02T10:50:45.203Z shell: /usr/bin/bash -e {0}
2024-08-02T10:50:45.204Z ##[endgroup]
2024-08-02T10:50:50.300Z added 1234 packages in 5.1s
2024-08-02T10:50:50.301Z ##[group]Run npm test
2024-08-02T10:50:50.302Z shell: /usr/bin/bash -e {0}
2024-08-02T10:50:50.303Z ##[endgroup]
2024-08-02T10:50:55.400Z > test
2024-08-02T10:50:55.401Z > jest
2024-08-02T10:50:55.402Z 
2024-08-02T10:50:55.403Z PASS  src/test.js
2024-08-02T10:50:55.404Z   ✓ should pass (2 ms)
2024-08-02T10:50:55.405Z 
2024-08-02T10:50:55.406Z Test Suites: 1 passed, 1 total
2024-08-02T10:50:55.407Z Tests:       1 passed, 1 total
"""

def get_sample_log_complex_multi_error():
    """Sample log with multiple error patterns"""
    return """
2024-08-02T11:00:00.123Z ##[group]Run npm ci
2024-08-02T11:00:00.124Z shell: /usr/bin/bash -e {0}
2024-08-02T11:00:00.125Z ##[endgroup]
2024-08-02T11:00:00.200Z ##[warning]Failed to restore cache entry. Request failed with status code 404
2024-08-02T11:00:00.201Z Cache not found for input keys: npm-cache-Linux-18-xyz789
2024-08-02T11:00:05.300Z npm ERR! code ENOENT
2024-08-02T11:00:05.301Z npm ERR! syscall open
2024-08-02T11:00:05.302Z npm ERR! path /home/runner/work/project/project/package.json
2024-08-02T11:00:05.303Z npm ERR! errno -2
2024-08-02T11:00:05.304Z npm ERR! enoent ENOENT: no such file or directory, open '/home/runner/work/project/project/package.json'
2024-08-02T11:00:05.305Z ##[error]Process completed with exit code 254.
2024-08-02T11:00:10.400Z ##[group]Run python -m pytest
2024-08-02T11:00:10.401Z shell: /usr/bin/bash -e {0}
2024-08-02T11:00:10.402Z ##[endgroup]
2024-08-02T11:00:15.500Z ============================================ FAILURES ============================================
2024-08-02T11:00:15.501Z _______________________________ test_integration _______________________________
2024-08-02T11:00:15.502Z 
2024-08-02T11:00:15.503Z     def test_integration():
2024-08-02T11:00:15.504Z >       import missing_module
2024-08-02T11:00:15.505Z E       ModuleNotFoundError: No module named 'missing_module'
2024-08-02T11:00:15.506Z 
2024-08-02T11:00:15.507Z tests/test_integration.py:10: ModuleNotFoundError
2024-08-02T11:00:15.508Z ##[error]Process completed with exit code 1.
"""

# Command line output examples
SAMPLE_GH_RUN_LIST_OUTPUT = json.dumps(get_sample_runs_data(), indent=2)

SAMPLE_GH_RUN_VIEW_LOG_OUTPUT = get_sample_log_npm_error()

# Expected test results
EXPECTED_FAILURE_PATTERNS = {
    "npm_error": {
        "pattern_name": "npm_package_not_found",
        "confidence": 0.9,
        "description": "Missing package.json or wrong working directory"
    },
    "python_import": {
        "pattern_name": "python_module_missing", 
        "confidence": 0.85,
        "description": "Missing Python module dependency"
    },
    "test_assertion": {
        "pattern_name": "test_failure_assertion",
        "confidence": 0.7,
        "description": "Test assertion failure"
    },
    "docker_permission": {
        "pattern_name": "docker_permission_denied",
        "confidence": 0.85,
        "description": "Docker permission or access issue"
    },
    "cache_warning": {
        "pattern_name": "cache_restore_failed",
        "confidence": 0.6,
        "description": "Cache restoration failure"
    }
}