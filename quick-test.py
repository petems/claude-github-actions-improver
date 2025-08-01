#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path

def create_python_workflows():
    """Create GitHub Actions workflows for Python project."""
    workflows_dir = Path(".github/workflows")
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Simple prompt for CI workflow
    prompt = """Create a GitHub Actions CI workflow for a Python project. Include:
    - Test on Python 3.8, 3.9, 3.10, 3.11
    - Install from requirements.txt
    - Run pytest and flake8
    - Use proper caching
    
    Output only the YAML content for .github/workflows/ci.yml"""
    
    cmd = ["claude", "--print", prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        # Extract YAML from response (remove markdown code blocks if present)
        yaml_content = result.stdout
        if "```yaml" in yaml_content:
            yaml_content = yaml_content.split("```yaml")[1].split("```")[0].strip()
        elif "```" in yaml_content:
            yaml_content = yaml_content.split("```")[1].split("```")[0].strip()
        
        # Write to file
        ci_file = workflows_dir / "ci.yml"
        with open(ci_file, 'w') as f:
            f.write(yaml_content)
        
        print(f"✅ Created {ci_file}")
        return True
    else:
        print(f"❌ Error: {result.stderr}")
        return False

if __name__ == "__main__":
    print("🤖 Quick GitHub Actions Creator")
    create_python_workflows()