#!/usr/bin/env python3
"""
Claude Agent: GitHub Actions Improver

This can be called from Claude CLI as an agent to improve GitHub Actions in any repo.
Supports concurrent processing of multiple failing workflows.

Usage from Claude:
- Task: "Improve GitHub Actions in this repository"
- Task: "Create GitHub Actions workflows for this project" 
- Task: "Fix failing GitHub Actions workflows"
"""

import os
import sys
import subprocess
import json
import asyncio
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Optional

class GitHubActionsAgent:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.workflows_dir = self.repo_path / ".github" / "workflows"
        
    def detect_project_info(self) -> Dict[str, any]:
        """Detect comprehensive project information."""
        info = {
            "type": "generic",
            "languages": [],
            "frameworks": [],
            "has_tests": False,
            "has_workflows": False,
            "project_files": []
        }
        
        # Language detection
        project_indicators = {
            'python': ['requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile', '*.py'],
            'node': ['package.json', 'yarn.lock', 'pnpm-lock.yaml'],
            'rust': ['Cargo.toml'],
            'go': ['go.mod', 'go.sum'],
            'java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
            'php': ['composer.json'],
            'ruby': ['Gemfile', 'Rakefile'],
            'dotnet': ['*.csproj', '*.sln'],
            'docker': ['Dockerfile', 'docker-compose.yml']
        }
        
        for lang, indicators in project_indicators.items():
            for indicator in indicators:
                if list(self.repo_path.glob(indicator)):
                    info["languages"].append(lang)
                    # Add found files for context
                    info["project_files"].extend([str(f) for f in self.repo_path.glob(indicator)])
                    break
        
        # Primary type
        if 'python' in info["languages"]:
            info["type"] = "python"
        elif 'node' in info["languages"]:
            info["type"] = "node"
        elif info["languages"]:
            info["type"] = info["languages"][0]
        
        # Test detection
        test_patterns = ['**/test*.py', '**/test*.js', '**/test*.go', '**/test*.rs', 
                        '**/tests/**', '**/spec/**', '**/__tests__/**']
        for pattern in test_patterns:
            if list(self.repo_path.glob(pattern)):
                info["has_tests"] = True
                break
        
        # Workflow detection
        info["has_workflows"] = self.has_workflows()
        
        return info
    
    def has_workflows(self) -> bool:
        """Check if repository has GitHub Actions workflows."""
        if not self.workflows_dir.exists():
            return False
        return any(self.workflows_dir.glob("*.yml")) or any(self.workflows_dir.glob("*.yaml"))
    
    def get_workflow_files(self) -> List[Path]:
        """Get all workflow files."""
        if not self.workflows_dir.exists():
            return []
        workflows = []
        workflows.extend(self.workflows_dir.glob("*.yml"))
        workflows.extend(self.workflows_dir.glob("*.yaml"))
        return workflows
    
    def run_claude_subprocess(self, prompt: str, task_name: str = "") -> str:
        """Run Claude CLI in subprocess with optimized prompt."""
        cmd = ["claude", "--print", prompt]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  cwd=self.repo_path, timeout=60)
            if result.returncode != 0:
                print(f"❌ Claude error for {task_name}: {result.stderr}")
                return ""
            return result.stdout
        except subprocess.TimeoutExpired:
            print(f"⏰ Claude timeout for {task_name}")
            return ""
        except Exception as e:
            print(f"❌ Error running Claude for {task_name}: {e}")
            return ""
    
    def extract_yaml_content(self, response: str) -> str:
        """Extract YAML from Claude response."""
        if "```yaml" in response:
            return response.split("```yaml")[1].split("```")[0].strip()
        elif "```" in response:
            parts = response.split("```")
            for i, part in enumerate(parts):
                if "name:" in part and ("on:" in part or "jobs:" in part):
                    return part.strip()
        return response.strip()
    
    def create_workflow_for_project(self, project_info: Dict) -> bool:
        """Create workflows based on project information."""
        if project_info["has_workflows"]:
            print("✅ Workflows already exist")
            return False
        
        print(f"🚀 Creating workflows for {project_info['type']} project...")
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Create CI workflow
        ci_prompt = self._get_ci_prompt(project_info)
        ci_response = self.run_claude_subprocess(ci_prompt, "CI workflow")
        
        if ci_response:
            ci_content = self.extract_yaml_content(ci_response)
            ci_file = self.workflows_dir / "ci.yml"
            with open(ci_file, 'w') as f:
                f.write(ci_content)
            print(f"✅ Created {ci_file.name}")
            
            # Create security workflow if this is a significant project
            if project_info["has_tests"]:
                self._create_security_workflow(project_info)
            
            return True
        
        return False
    
    def _get_ci_prompt(self, project_info: Dict) -> str:
        """Generate CI workflow prompt based on project info."""
        project_type = project_info["type"]
        
        base_prompt = f"Create a GitHub Actions CI workflow for a {project_type} project."
        
        if project_type == "python":
            return f"""{base_prompt}
            Requirements:
            - Test Python versions: 3.9, 3.10, 3.11, 3.12
            - Use pip caching
            - Install from requirements.txt if exists
            - Run pytest if tests exist, otherwise basic python -m py_compile
            - Run flake8 linting
            - Use latest action versions
            Output only clean YAML content."""
            
        elif project_type == "node":
            return f"""{base_prompt}
            Requirements:
            - Test Node versions: 18, 20, 22
            - Use npm/yarn caching
            - Run npm test or yarn test
            - Run npm run lint if available
            - Use latest action versions
            Output only clean YAML content."""
            
        elif project_type == "rust":
            return f"""{base_prompt}
            Requirements:
            - Use stable rust toolchain
            - Run cargo build, cargo test
            - Run cargo clippy for linting
            - Use cargo caching
            - Use latest action versions
            Output only clean YAML content."""
            
        elif project_type == "go":
            return f"""{base_prompt}
            Requirements:
            - Test Go versions: 1.20, 1.21, 1.22
            - Run go build, go test
            - Run go vet for linting
            - Use Go module caching
            - Use latest action versions
            Output only clean YAML content."""
            
        else:
            return f"""{base_prompt}
            Requirements:
            - Basic checkout and build steps
            - Generic testing approach
            - Use latest action versions
            Output only clean YAML content."""
    
    def _create_security_workflow(self, project_info: Dict):
        """Create security scanning workflow."""
        security_prompt = f"""Create a GitHub Actions security workflow for a {project_info['type']} project.
        Include:
        - Dependency vulnerability scanning
        - SAST security analysis
        - Weekly schedule + manual trigger
        - Use latest action versions
        Output only clean YAML content."""
        
        response = self.run_claude_subprocess(security_prompt, "Security workflow")
        if response:
            content = self.extract_yaml_content(response)
            security_file = self.workflows_dir / "security.yml"
            with open(security_file, 'w') as f:
                f.write(content)
            print(f"✅ Created {security_file.name}")
    
    def improve_workflow_concurrent(self, workflow_file: Path) -> Dict:
        """Improve a single workflow file (for concurrent execution)."""
        try:
            with open(workflow_file, 'r') as f:
                current_content = f.read()
            
            prompt = f"""Improve this GitHub Actions workflow with modern best practices:
            
            Current workflow:
            ```yaml
            {current_content}
            ```
            
            Apply these improvements:
            - Update to latest action versions with SHA pinning
            - Add security hardening
            - Optimize caching strategies
            - Add proper permissions (principle of least privilege)
            - Improve matrix configurations
            - Add concurrency controls
            
            Output only the improved YAML content."""
            
            response = self.run_claude_subprocess(prompt, f"improve {workflow_file.name}")
            
            if response:
                improved_content = self.extract_yaml_content(response)
                with open(workflow_file, 'w') as f:
                    f.write(improved_content)
                return {"status": "success", "file": workflow_file.name}
            else:
                return {"status": "failed", "file": workflow_file.name}
                
        except Exception as e:
            return {"status": "error", "file": workflow_file.name, "error": str(e)}
    
    def fix_workflow_concurrent(self, workflow_file: Path) -> Dict:
        """Fix a single workflow file (for concurrent execution)."""
        try:
            with open(workflow_file, 'r') as f:
                current_content = f.read()
            
            prompt = f"""Analyze and fix common issues in this GitHub Actions workflow:
            
            Current workflow:
            ```yaml
            {current_content}
            ```
            
            Fix these common issues:
            - Outdated action versions
            - YAML syntax errors
            - Missing required dependencies
            - Permission problems
            - Broken caching configurations
            - Matrix build issues
            - Environment variable problems
            
            Output only the fixed YAML content."""
            
            response = self.run_claude_subprocess(prompt, f"fix {workflow_file.name}")
            
            if response:
                fixed_content = self.extract_yaml_content(response)
                with open(workflow_file, 'w') as f:
                    f.write(fixed_content)
                return {"status": "success", "file": workflow_file.name}
            else:
                return {"status": "failed", "file": workflow_file.name}
                
        except Exception as e:
            return {"status": "error", "file": workflow_file.name, "error": str(e)}
    
    def process_workflows_concurrently(self, workflow_files: List[Path], 
                                     operation: str = "improve") -> List[Dict]:
        """Process multiple workflows concurrently using thread pool."""
        if not workflow_files:
            return []
        
        print(f"🔄 Processing {len(workflow_files)} workflows concurrently...")
        
        # Choose operation function
        operation_func = (self.improve_workflow_concurrent if operation == "improve" 
                         else self.fix_workflow_concurrent)
        
        # Use ThreadPoolExecutor for concurrent processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            future_to_workflow = {
                executor.submit(operation_func, workflow): workflow 
                for workflow in workflow_files
            }
            
            results = []
            for future in concurrent.futures.as_completed(future_to_workflow):
                result = future.result()
                results.append(result)
                
                # Print real-time status
                if result["status"] == "success":
                    print(f"✅ {result['file']}")
                else:
                    print(f"❌ {result['file']}: {result.get('error', 'Failed')}")
        
        return results
    
    def run_full_analysis(self) -> Dict:
        """Run complete GitHub Actions analysis and improvement."""
        print("🤖 Claude Agent: GitHub Actions Improver")
        print(f"📁 Repository: {self.repo_path}")
        print()
        
        # Detect project information
        project_info = self.detect_project_info()
        print(f"🔍 Project type: {project_info['type']}")
        print(f"🔍 Languages: {', '.join(project_info['languages'])}")
        print(f"🔍 Has tests: {project_info['has_tests']}")
        print(f"🔍 Has workflows: {project_info['has_workflows']}")
        print()
        
        results = {
            "project_info": project_info,
            "created_workflows": False,
            "improved_workflows": [],
            "fixed_workflows": []
        }
        
        # Create workflows if needed
        if not project_info["has_workflows"]:
            results["created_workflows"] = self.create_workflow_for_project(project_info)
        
        # Get current workflows
        workflow_files = self.get_workflow_files()
        
        if workflow_files:
            # Improve workflows concurrently
            print("\n🔧 Improving existing workflows...")
            improve_results = self.process_workflows_concurrently(workflow_files, "improve")
            results["improved_workflows"] = improve_results
            
            # Fix any remaining issues concurrently
            print("\n🔨 Fixing workflow issues...")
            fix_results = self.process_workflows_concurrently(workflow_files, "fix")
            results["fixed_workflows"] = fix_results
        
        # Summary
        print(f"\n🎉 GitHub Actions improvement complete!")
        print(f"✅ Created workflows: {results['created_workflows']}")
        print(f"✅ Improved workflows: {len([r for r in results['improved_workflows'] if r['status'] == 'success'])}")
        print(f"✅ Fixed workflows: {len([r for r in results['fixed_workflows'] if r['status'] == 'success'])}")
        
        return results

def main():
    """Main entry point - can be called by Claude or directly."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Agent: GitHub Actions Improver")
    parser.add_argument("--mode", choices=["create", "improve", "fix", "full"], 
                       default="full", help="Operation mode")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    # Verify git repository
    repo_path = Path(args.repo_path)
    if not (repo_path / ".git").exists():
        print("❌ Not a Git repository")
        sys.exit(1)
    
    # Verify Claude CLI
    try:
        subprocess.run(["claude", "--help"], capture_output=True, check=True)
    except:
        print("❌ Claude CLI not available")
        sys.exit(1)
    
    agent = GitHubActionsAgent(args.repo_path)
    
    if args.mode == "full":
        agent.run_full_analysis()
    elif args.mode == "create":
        project_info = agent.detect_project_info()
        agent.create_workflow_for_project(project_info)
    elif args.mode == "improve":
        workflows = agent.get_workflow_files()
        agent.process_workflows_concurrently(workflows, "improve")
    elif args.mode == "fix":
        workflows = agent.get_workflow_files()
        agent.process_workflows_concurrently(workflows, "fix")

if __name__ == "__main__":
    main()