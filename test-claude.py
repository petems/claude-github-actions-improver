#!/usr/bin/env python3
import subprocess

# Simple test of Claude CLI
cmd = ["claude", "--print", "Create a simple GitHub Actions CI workflow for a Python project. Just output the YAML content."]

result = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", result.returncode)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)