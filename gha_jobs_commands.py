#!/usr/bin/env python3
"""
GitHub Actions Jobs Commands Implementation
Provides core functionality for jobs-status, jobs-failed-investigate, and jobs-fixfailed-ngu commands
"""

import json
import subprocess
import sys
import time
import re
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
import logging


class RunStatus(Enum):
    """GitHub Actions run status"""
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"


class FixConfidence(Enum):
    """Confidence levels for fixes"""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.9


@dataclass
class WorkflowRun:
    """Represents a GitHub Actions workflow run"""
    id: str
    name: str
    status: str
    conclusion: str
    created_at: str
    head_branch: str
    event: str
    url: str = ""
    
    @property
    def is_failed(self) -> bool:
        return self.conclusion in ["failure", "cancelled"]
    
    @property
    def age_hours(self) -> float:
        """Calculate age of run in hours"""
        try:
            # Handle both Z suffix and explicit timezone
            if self.created_at.endswith('Z'):
                created_str = self.created_at.replace('Z', '+00:00')
            else:
                created_str = self.created_at
            
            created = datetime.fromisoformat(created_str)
            
            # If created datetime is timezone-aware, make now timezone-aware too
            if created.tzinfo is not None:
                from datetime import timezone
                now = datetime.now(timezone.utc)
            else:
                now = datetime.now()
            
            return (now - created).total_seconds() / 3600
        except Exception as e:
            # Fallback for any parsing issues
            return 0


@dataclass
class FailurePattern:
    """Represents a detected failure pattern"""
    pattern_name: str
    error_signature: str
    confidence: float
    description: str
    suggested_fix: str
    file_context: Optional[str] = None
    line_number: Optional[int] = None


@dataclass
class InvestigationResult:
    """Results from failure investigation"""
    run: WorkflowRun
    patterns: List[FailurePattern]
    root_cause: str
    fix_recommendations: List[str]
    confidence: float
    log_excerpt: str


class GitHubActionsJobsManager:
    """Core manager for GitHub Actions jobs commands"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.failure_patterns = self._load_failure_patterns()
    
    def _load_failure_patterns(self) -> List[Dict]:
        """Load failure patterns for pattern recognition"""
        return [
            {
                "name": "npm_package_not_found",
                "regex": r"npm ERR! code ENOENT",
                "confidence": 0.9,
                "description": "Missing package.json or wrong working directory",
                "fix": "Add working-directory or check package.json location"
            },
            {
                "name": "python_module_missing", 
                "regex": r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]",
                "confidence": 0.85,
                "description": "Missing Python module dependency",
                "fix": "Add missing module to requirements.txt or install step"
            },
            {
                "name": "test_failure_assertion",
                "regex": r"AssertionError: (.+)",
                "confidence": 0.7,
                "description": "Test assertion failure",
                "fix": "Review test logic and expected vs actual values"
            },
            {
                "name": "docker_permission_denied",
                "regex": r"docker: Error response from daemon.*permission denied",
                "confidence": 0.85,
                "description": "Docker permission or access issue",
                "fix": "Check Docker permissions and registry access"
            },
            {
                "name": "cache_restore_failed",
                "regex": r"Failed to restore cache entry",
                "confidence": 0.6,
                "description": "Cache restoration failure",
                "fix": "Update cache keys or add restore-keys fallback"
            }
        ]
    
    def get_recent_runs(self, limit: int = 10, status_filter: Optional[str] = None) -> List[WorkflowRun]:
        """Get recent workflow runs using GitHub CLI"""
        cmd = [
            "gh", "run", "list", 
            "--limit", str(limit),
            "--json", "databaseId,name,status,conclusion,createdAt,headBranch,event,url"
        ]
        
        if status_filter:
            cmd.extend(["--status", status_filter])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            runs_data = json.loads(result.stdout)
            
            runs = []
            for run_data in runs_data:
                run = WorkflowRun(
                    id=str(run_data["databaseId"]),
                    name=run_data["name"],
                    status=run_data["status"],
                    conclusion=run_data.get("conclusion", ""),
                    created_at=run_data["createdAt"],
                    head_branch=run_data["headBranch"],
                    event=run_data["event"],
                    url=run_data.get("url", "")
                )
                runs.append(run)
            
            return runs
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get runs: {e}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse GitHub CLI output: {e}")
            return []
    
    def get_run_logs(self, run_id: str) -> str:
        """Get logs for a specific run"""
        try:
            cmd = ["gh", "run", "view", run_id, "--log"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get logs for run {run_id}: {e}")
            return ""
    
    def analyze_failure_patterns(self, log_content: str) -> List[FailurePattern]:
        """Analyze logs for failure patterns"""
        patterns = []
        
        for pattern_def in self.failure_patterns:
            matches = re.finditer(pattern_def["regex"], log_content, re.MULTILINE | re.IGNORECASE)
            
            for match in matches:
                pattern = FailurePattern(
                    pattern_name=pattern_def["name"],
                    error_signature=match.group(0),
                    confidence=pattern_def["confidence"],
                    description=pattern_def["description"],
                    suggested_fix=pattern_def["fix"],
                    file_context=self._extract_file_context(log_content, match.start()),
                    line_number=self._extract_line_number(log_content, match.start())
                )
                patterns.append(pattern)
        
        return patterns
    
    def _extract_file_context(self, log_content: str, match_pos: int) -> Optional[str]:
        """Extract file context around a match"""
        # Look for file paths in the surrounding context
        lines = log_content[:match_pos].split('\n')
        for line in reversed(lines[-10:]):  # Look at last 10 lines
            if re.search(r'\.(js|py|ts|yml|yaml|json):', line):
                return line.strip()
        return None
    
    def _extract_line_number(self, log_content: str, match_pos: int) -> Optional[int]:
        """Extract line number if available"""
        lines = log_content[:match_pos].split('\n')
        for line in reversed(lines[-10:]):  # Look at last 10 lines
            # Look for patterns like "line 25:", "at 25:", ":25:", etc.
            line_match = re.search(r'(?:line|at)?\s*(\d+):', line)
            if line_match:
                return int(line_match.group(1))
        return None


class JobsStatusCommand:
    """Implementation of /gha:jobs-status command"""
    
    def __init__(self):
        self.manager = GitHubActionsJobsManager()
    
    def execute(self, limit: int = 5, branch: Optional[str] = None, 
                workflow: Optional[str] = None, format_type: str = "table") -> Dict[str, Any]:
        """Execute jobs status command"""
        print("🔍 Checking latest GitHub Actions runs...")
        
        # Get recent failed runs
        all_runs = self.manager.get_recent_runs(limit=limit*2)  # Get more to filter
        
        # Filter runs
        filtered_runs = []
        for run in all_runs:
            if branch and run.head_branch != branch:
                continue
            if workflow and workflow.lower() not in run.name.lower():
                continue
            if run.is_failed:
                filtered_runs.append(run)
            
            if len(filtered_runs) >= limit:
                break
        
        # Generate output
        if format_type == "table":
            self._display_table_format(filtered_runs)
        else:
            self._display_simple_format(filtered_runs)
        
        # Generate summary
        self._display_summary(filtered_runs)
        
        return {
            "status": "success",
            "runs_found": len(filtered_runs),
            "runs": [asdict(run) for run in filtered_runs]
        }
    
    def _display_table_format(self, runs: List[WorkflowRun]):
        """Display results in table format"""
        if not runs:
            print("✅ No recent failures found!")
            return
        
        print("\n🔍 Latest GitHub Actions Failures\n")
        
        # Table header
        print("┌─────────────┬──────────────┬────────────┬─────────────────────┬────────────┐")
        print("│ Run ID      │ Workflow     │ Branch     │ Failed              │ Event      │")
        print("├─────────────┼──────────────┼────────────┼─────────────────────┼────────────┤")
        
        for run in runs:
            age_str = self._format_age(run.age_hours)
            print(f"│ {run.id:<11} │ {run.name[:12]:<12} │ {run.head_branch[:10]:<10} │ {age_str:<19} │ {run.event[:10]:<10} │")
        
        print("└─────────────┴──────────────┴────────────┴─────────────────────┴────────────┘")
    
    def _display_simple_format(self, runs: List[WorkflowRun]):
        """Display results in simple format"""
        if not runs:
            print("✅ No recent failures found!")
            return
        
        print("\n🔍 Latest GitHub Actions Failures\n")
        
        for run in runs:
            age_str = self._format_age(run.age_hours)
            print(f"❌ {run.name} ({run.head_branch}) - {age_str} - Run #{run.id}")
    
    def _display_summary(self, runs: List[WorkflowRun]):
        """Display summary statistics"""
        if not runs:
            return
        
        # Count by workflow
        workflow_counts = {}
        branch_counts = {}
        
        for run in runs:
            workflow_counts[run.name] = workflow_counts.get(run.name, 0) + 1
            branch_counts[run.head_branch] = branch_counts.get(run.head_branch, 0) + 1
        
        print(f"\n📊 Summary:")
        print(f"• {len(runs)} failures found")
        
        if workflow_counts:
            most_failing = max(workflow_counts, key=workflow_counts.get)
            print(f"• Most failing workflow: {most_failing} ({workflow_counts[most_failing]} failures)")
        
        if branch_counts:
            most_failing_branch = max(branch_counts, key=branch_counts.get)
            print(f"• Most failures on: {most_failing_branch} branch ({branch_counts[most_failing_branch]} failures)")
        
        print(f"• 🔗 View details: gh run list --limit {len(runs)} --status failure")
        print(f"\n💡 Use /gha:jobs-failed-investigate to analyze these failures")
    
    def _format_age(self, hours: float) -> str:
        """Format age in human-readable format"""
        if hours < 1:
            return f"{int(hours * 60)} minutes ago"
        elif hours < 24:
            return f"{int(hours)} hours ago"
        else:
            days = int(hours / 24)
            return f"{days} day{'s' if days > 1 else ''} ago"


class JobsFailedInvestigateCommand:
    """Implementation of /gha:jobs-failed-investigate command"""
    
    def __init__(self):
        self.manager = GitHubActionsJobsManager()
    
    def execute(self, runs_limit: int = 5, workflow: Optional[str] = None,
                confidence_threshold: float = 0.6) -> Dict[str, Any]:
        """Execute jobs failed investigate command"""
        print("🔍 Investigating failed GitHub Actions runs...")
        
        # Get failed runs
        failed_runs = self.manager.get_recent_runs(limit=runs_limit*2, status_filter="failure")
        if workflow:
            failed_runs = [r for r in failed_runs if workflow.lower() in r.name.lower()]
        
        failed_runs = failed_runs[:runs_limit]
        
        if not failed_runs:
            print("✅ No recent failures found to investigate!")
            return {"status": "success", "investigations": []}
        
        print(f"📊 Found {len(failed_runs)} failed runs, downloading logs...")
        
        # Investigate each failure
        investigations = []
        for i, run in enumerate(failed_runs, 1):
            print(f"🧠 Analyzing run {i}/{len(failed_runs)}: {run.name} (#{run.id})...")
            
            investigation = self._investigate_run(run, confidence_threshold)
            investigations.append(investigation)
        
        # Generate report
        self._generate_investigation_report(investigations)
        
        return {
            "status": "success",
            "investigations": [asdict(inv) for inv in investigations]
        }
    
    def _investigate_run(self, run: WorkflowRun, confidence_threshold: float) -> InvestigationResult:
        """Investigate a specific failed run"""
        # Get logs
        logs = self.manager.get_run_logs(run.id)
        
        # Analyze patterns
        patterns = self.manager.analyze_failure_patterns(logs)
        
        # Filter by confidence
        high_confidence_patterns = [p for p in patterns if p.confidence >= confidence_threshold]
        
        # Determine root cause
        root_cause = self._determine_root_cause(high_confidence_patterns, logs)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(high_confidence_patterns)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(high_confidence_patterns)
        
        # Extract relevant log excerpt
        log_excerpt = self._extract_relevant_logs(logs, patterns)
        
        return InvestigationResult(
            run=run,
            patterns=high_confidence_patterns,
            root_cause=root_cause,
            fix_recommendations=recommendations,
            confidence=overall_confidence,
            log_excerpt=log_excerpt
        )
    
    def _determine_root_cause(self, patterns: List[FailurePattern], logs: str) -> str:
        """Determine the root cause of failure"""
        if not patterns:
            return "Unable to identify specific root cause from available patterns"
        
        # Sort by confidence
        patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        # Use highest confidence pattern as primary root cause
        primary = patterns[0]
        
        if len(patterns) == 1:
            return f"{primary.description}"
        else:
            return f"{primary.description} (plus {len(patterns)-1} related issues)"
    
    def _generate_recommendations(self, patterns: List[FailurePattern]) -> List[str]:
        """Generate fix recommendations"""
        recommendations = []
        
        for pattern in patterns:
            recommendations.append(f"• {pattern.suggested_fix}")
        
        if not recommendations:
            recommendations = [
                "• Review workflow logs for specific error messages",
                "• Check recent code changes that might have caused the failure",
                "• Verify environment setup and dependencies"
            ]
        
        return recommendations
    
    def _calculate_overall_confidence(self, patterns: List[FailurePattern]) -> float:
        """Calculate overall confidence in analysis"""
        if not patterns:
            return 0.3
        
        # Weighted average of pattern confidences
        total_weight = sum(p.confidence for p in patterns)
        if total_weight == 0:
            return 0.3
        
        weighted_avg = sum(p.confidence * p.confidence for p in patterns) / total_weight
        return min(weighted_avg, 0.95)  # Cap at 95%
    
    def _extract_relevant_logs(self, logs: str, patterns: List[FailurePattern]) -> str:
        """Extract most relevant part of logs"""
        if not patterns:
            # Return last 500 characters as fallback
            return logs[-500:] if len(logs) > 500 else logs
        
        # Find log sections around pattern matches
        relevant_sections = []
        
        for pattern in patterns[:3]:  # Top 3 patterns
            # Find this pattern in logs
            match = re.search(re.escape(pattern.error_signature), logs)
            if match:
                start = max(0, match.start() - 200)
                end = min(len(logs), match.end() + 200)
                section = logs[start:end]
                relevant_sections.append(f"--- {pattern.pattern_name} ---\n{section}")
        
        return "\n\n".join(relevant_sections) if relevant_sections else logs[-500:]
    
    def _generate_investigation_report(self, investigations: List[InvestigationResult]):
        """Generate comprehensive investigation report"""
        print(f"\n# 🔍 GitHub Actions Investigation Report\n")
        
        # Executive summary
        total_patterns = sum(len(inv.patterns) for inv in investigations)
        avg_confidence = sum(inv.confidence for inv in investigations) / len(investigations) if investigations else 0
        
        print(f"## 🎯 Key Findings")
        print(f"- **{len(investigations)} failures analyzed** across workflows")
        print(f"- **{total_patterns} patterns identified** with avg confidence {avg_confidence:.2f}")
        
        # Most common patterns
        all_patterns = []
        for inv in investigations:
            all_patterns.extend(inv.patterns)
        
        if all_patterns:
            pattern_counts = {}
            for pattern in all_patterns:
                pattern_counts[pattern.pattern_name] = pattern_counts.get(pattern.pattern_name, 0) + 1
            
            most_common = max(pattern_counts, key=pattern_counts.get)
            print(f"- **Most common issue**: {most_common} ({pattern_counts[most_common]} occurrences)")
        
        print(f"\n## ⚡ Immediate Actions Needed")
        
        # Collect unique recommendations
        all_recommendations = set()
        for inv in investigations:
            all_recommendations.update(inv.fix_recommendations)
        
        for i, rec in enumerate(sorted(all_recommendations)[:5], 1):
            print(f"{i}. {rec.replace('• ', '')}")
        
        # Detailed analysis
        print(f"\n## 🔍 Detailed Analysis\n")
        
        for i, inv in enumerate(investigations, 1):
            print(f"### {i}. {inv.run.name} Failure (Run #{inv.run.id})")
            print(f"**Branch**: {inv.run.head_branch}")
            print(f"**Confidence**: {inv.confidence:.2f}\n")
            
            print(f"#### 🧠 Root Cause Analysis:")
            print(f"{inv.root_cause}\n")
            
            if inv.patterns:
                print(f"#### 🎯 Patterns Detected:")
                for pattern in inv.patterns:
                    print(f"- **{pattern.pattern_name}** (confidence: {pattern.confidence:.2f})")
                    print(f"  - {pattern.description}")
                    print(f"  - Fix: {pattern.suggested_fix}")
                print()
            
            print(f"#### 🛠️ Recommended Actions:")
            for rec in inv.fix_recommendations:
                print(rec)
            print()
        
        print(f"💡 **Next Steps**: Use `/gha:jobs-fixfailed-ngu` to automatically apply fixes")


# Placeholder for NGU command - this would be much more complex
class JobsFixFailedNGUCommand:
    """Implementation of /gha:jobs-fixfailed-ngu command"""
    
    def __init__(self):
        self.manager = GitHubActionsJobsManager()
        self.investigate_cmd = JobsFailedInvestigateCommand()
    
    def execute(self, max_rounds: int = 5, patience_minutes: int = 10) -> Dict[str, Any]:
        """Execute NGU fixing command - placeholder implementation"""
        print("💪 NGU MODE ACTIVATED! Never Give Up fixing GitHub Actions!")
        print("🔥 This is a demonstration - full NGU implementation would include:")
        print("   - Automated fix application based on patterns")
        print("   - Workflow triggering and monitoring")
        print("   - Retry loops with adaptive strategies")
        print("   - Victory detection and celebration")
        print("   - Loop detection and safety limits")
        
        # For now, just run investigation
        print("\n🔍 Starting with failure investigation...")
        result = self.investigate_cmd.execute()
        
        print("\n💪 NGU SPIRIT: In full implementation, would now apply fixes and retry!")
        print("🎯 Stay tuned for the complete NGU experience!")
        
        return {"status": "demo", "message": "NGU demo mode - investigation completed"}


if __name__ == "__main__":
    """Command-line interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Actions Jobs Commands")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # jobs-status command
    status_parser = subparsers.add_parser("jobs-status", help="Get latest failures status")
    status_parser.add_argument("--limit", type=int, default=5, help="Number of failures to show")
    status_parser.add_argument("--branch", help="Filter by branch")
    status_parser.add_argument("--workflow", help="Filter by workflow")
    status_parser.add_argument("--format", choices=["table", "simple"], default="table", help="Output format")
    
    # jobs-failed-investigate command
    investigate_parser = subparsers.add_parser("jobs-failed-investigate", help="Investigate failures")
    investigate_parser.add_argument("--runs", type=int, default=5, help="Number of runs to investigate")
    investigate_parser.add_argument("--workflow", help="Filter by workflow")
    investigate_parser.add_argument("--confidence", type=float, default=0.6, help="Confidence threshold")
    
    # jobs-fixfailed-ngu command
    ngu_parser = subparsers.add_parser("jobs-fixfailed-ngu", help="Never Give Up fixing")
    ngu_parser.add_argument("--max-rounds", type=int, default=5, help="Maximum rounds")
    ngu_parser.add_argument("--patience", type=int, default=10, help="Patience in minutes")
    
    args = parser.parse_args()
    
    if args.command == "jobs-status":
        cmd = JobsStatusCommand()
        cmd.execute(
            limit=args.limit,
            branch=args.branch,
            workflow=args.workflow,
            format_type=args.format
        )
    elif args.command == "jobs-failed-investigate":
        cmd = JobsFailedInvestigateCommand()
        cmd.execute(
            runs_limit=args.runs,
            workflow=args.workflow,
            confidence_threshold=args.confidence
        )
    elif args.command == "jobs-fixfailed-ngu":
        cmd = JobsFixFailedNGUCommand()
        cmd.execute(
            max_rounds=args.max_rounds,
            patience_minutes=args.patience
        )
    else:
        parser.print_help()