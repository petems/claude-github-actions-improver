#!/usr/bin/env python3
"""
Claude GitHub Actions Improver - Minimal Template-Based Version

Ultra-fast workflow creation using pre-built templates instead of Claude generation.
Only uses Claude for complex improvements and fixes.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# Import template manager
sys.path.append(str(Path(__file__).parent / "templates"))
from template_manager import TemplateManager

class MinimalGitHubActionsImprover:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.workflows_dir = self.repo_path / ".github" / "workflows"
        # Pass the templates directory to the template manager
        templates_dir = Path(__file__).parent / "templates"
        self.template_manager = TemplateManager(str(templates_dir))
        
    def detect_project_type(self) -> str:
        """Detect the primary project type based on files in the repository."""
        # Fast file-based detection
        if (self.repo_path / "package.json").exists():
            return "node"
        elif any((self.repo_path / f).exists() for f in ["requirements.txt", "pyproject.toml", "setup.py"]):
            return "python"
        elif (self.repo_path / "Cargo.toml").exists():
            return "rust"
        elif (self.repo_path / "go.mod").exists():
            return "go"
        elif any((self.repo_path / f).exists() for f in ["pom.xml", "build.gradle"]):
            return "java"
        elif (self.repo_path / "composer.json").exists():
            return "php"
        elif (self.repo_path / "Gemfile").exists():
            return "ruby"
        elif any(self.repo_path.glob("*.csproj")) or any(self.repo_path.glob("*.sln")):
            return "dotnet"
        else:
            return "generic"
    
    def has_workflows(self) -> bool:
        """Check if the repository has any GitHub Actions workflows."""
        if not self.workflows_dir.exists():
            return False
        return any(self.workflows_dir.glob("*.yml")) or any(self.workflows_dir.glob("*.yaml"))
    
    def create_workflows_from_templates(self) -> bool:
        """Create workflows using pre-built templates (no Claude needed)."""
        if self.has_workflows():
            print("✅ Workflows already exist, skipping creation")
            return False
        
        project_type = self.detect_project_type()
        print(f"🔍 Detected project type: {project_type}")
        print("⚡ Creating GitHub Actions workflows from templates...")
        
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Get CI template
        ci_template = self.template_manager.get_template(project_type)
        if ci_template:
            ci_file = self.workflows_dir / "ci.yml"
            with open(ci_file, 'w') as f:
                f.write(ci_template)
            print(f"✅ Created {ci_file.name} (from template)")
        
        # Add security template for non-generic projects
        if project_type != "generic":
            security_template = self.template_manager.get_security_template()
            if security_template:
                security_file = self.workflows_dir / "security.yml"
                with open(security_file, 'w') as f:
                    f.write(security_template)
                print(f"✅ Created {security_file.name} (from template)")
        
        return True
    
    def run_claude_for_complex_tasks(self, prompt: str, task_name: str = "") -> str:
        """Only use Claude for complex improvements that templates can't handle."""
        cmd = ["claude", "--print", prompt]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  cwd=self.repo_path, timeout=30)  # Shorter timeout
            if result.returncode != 0:
                print(f"❌ Claude error for {task_name}: {result.stderr}")
                return ""
            return result.stdout
        except subprocess.TimeoutExpired:
            print(f"⏰ Claude timeout for {task_name} (using fallback)")
            return ""
        except Exception as e:
            print(f"❌ Error running Claude for {task_name}: {e}")
            return ""
    
    def improve_existing_workflows(self) -> bool:
        """Improve existing workflows - only use Claude if needed."""
        if not self.has_workflows():
            print("ℹ️ No existing workflows to improve")
            return False
        
        workflows = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))
        print(f"🔧 Checking {len(workflows)} workflows for improvements...")
        
        improvements_made = False
        
        for workflow_file in workflows:
            print(f"🔍 Checking: {workflow_file.name}")
            
            with open(workflow_file, 'r') as f:
                content = f.read()
            
            # Quick template-based fixes
            if self._apply_quick_fixes(workflow_file, content):
                print(f"✅ Applied quick fixes to {workflow_file.name}")
                improvements_made = True
            else:
                # Only use Claude for complex cases
                if self._needs_complex_improvement(content):
                    print(f"🤖 Using Claude for complex improvements on {workflow_file.name}")
                    self._claude_improve_workflow(workflow_file, content)
                    improvements_made = True
                else:
                    print(f"✅ {workflow_file.name} looks good")
        
        return improvements_made
    
    def _apply_quick_fixes(self, workflow_file: Path, content: str) -> bool:
        """Apply quick template-based fixes without Claude."""
        fixes_applied = False
        original_content = content
        
        # Fix 1: Update checkout action
        if "actions/checkout@v3" in content:
            content = content.replace("actions/checkout@v3", "actions/checkout@v4")
            fixes_applied = True
        
        # Fix 2: Update setup actions
        replacements = {
            "actions/setup-python@v4": "actions/setup-python@v5",
            "actions/setup-node@v3": "actions/setup-node@v4", 
            "actions/setup-go@v4": "actions/setup-go@v5",
            "actions/cache@v3": "actions/cache@v4"
        }
        
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
                fixes_applied = True
        
        # Fix 3: Add cache if missing for common languages
        if "python" in content.lower() and "cache:" not in content:
            content = content.replace(
                "python-version: ${{ matrix.python-version }}",
                "python-version: ${{ matrix.python-version }}\n        cache: 'pip'"
            )
            fixes_applied = True
        
        if fixes_applied:
            with open(workflow_file, 'w') as f:
                f.write(content)
        
        return fixes_applied
    
    def _needs_complex_improvement(self, content: str) -> bool:
        """Determine if workflow needs complex Claude-based improvement."""
        # Check for issues that need Claude's help
        complex_issues = [
            len(content.split('\n')) > 100,  # Very long workflow
            "matrix:" in content and "fail-fast:" not in content,  # Missing fail-fast
            "permissions:" not in content,  # Missing permissions
            "workflow_dispatch:" not in content,  # Missing manual trigger
        ]
        
        return any(complex_issues)
    
    def _claude_improve_workflow(self, workflow_file: Path, content: str):
        """Use Claude only for complex workflow improvements."""
        prompt = f"""Improve this GitHub Actions workflow with these specific fixes:
        - Add proper permissions (minimal required)
        - Add workflow_dispatch trigger
        - Add fail-fast: false to matrix if present
        - Optimize for performance and security
        
        Current workflow:
        ```yaml
        {content[:1000]}...  
        ```
        
        Output only the improved YAML content."""
        
        response = self.run_claude_for_complex_tasks(prompt, f"improve {workflow_file.name}")
        if response and "name:" in response:
            # Extract YAML from response
            if "```yaml" in response:
                improved_content = response.split("```yaml")[1].split("```")[0].strip()
            elif "```" in response:
                improved_content = response.split("```")[1].split("```")[0].strip()
            else:
                improved_content = response.strip()
            
            with open(workflow_file, 'w') as f:
                f.write(improved_content)
            print(f"✅ Improved {workflow_file.name} with Claude")
    
    def run(self, mode: str = "auto"):
        """Run the minimal GitHub Actions improver."""
        print(f"⚡ Minimal GitHub Actions Improver")
        print(f"📁 Repository: {self.repo_path}")
        print(f"🎯 Mode: {mode}")
        print()
        
        if mode in ["auto", "create"]:
            self.create_workflows_from_templates()
        
        if mode in ["auto", "improve"]:
            self.improve_existing_workflows()
        
        print(f"\n🎉 GitHub Actions improvement complete!")
        print("💡 Used templates where possible to save tokens and time")

def main():
    parser = argparse.ArgumentParser(description="Minimal Claude Agent for GitHub Actions")
    parser.add_argument("--mode", choices=["create", "improve", "auto"], default="auto")
    parser.add_argument("--repo-path", default=".")
    
    args = parser.parse_args()
    
    # Verify git repository
    repo_path = Path(args.repo_path)
    if not (repo_path / ".git").exists():
        print("❌ Not a Git repository")
        sys.exit(1)
    
    improver = MinimalGitHubActionsImprover(args.repo_path)
    improver.run(args.mode)

if __name__ == "__main__":
    main()