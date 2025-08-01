#!/usr/bin/env python3
"""
GitHub API Rate Limit Handler for Concurrent Job Processing
Handles authentication, rate limiting, and token management
"""

import os
import time
import json
import subprocess
import urllib.request
import urllib.parse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import threading
from datetime import datetime, timedelta

@dataclass
class RateLimit:
    """GitHub API rate limit information"""
    limit: int
    remaining: int
    reset_timestamp: int
    used: int
    
    @property
    def reset_time(self) -> datetime:
        return datetime.fromtimestamp(self.reset_timestamp)
    
    @property
    def time_until_reset(self) -> int:
        return max(0, self.reset_timestamp - int(time.time()))

class GitHubAPILimitHandler:
    """Handles GitHub API rate limits and authentication"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or self._get_token()
        self.rate_limit_lock = threading.Lock()
        self.last_rate_limit: Optional[RateLimit] = None
        self.request_count = 0
        
    def _get_token(self) -> Optional[str]:
        """Get GitHub token from various sources"""
        # Priority order: explicit env var > gh CLI > GitHub Actions
        token_sources = [
            ("GITHUB_TOKEN", os.getenv("GITHUB_TOKEN")),
            ("GH_TOKEN", os.getenv("GH_TOKEN")),
            ("gh CLI", self._get_gh_token()),
            ("Actions Token", os.getenv("GITHUB_TOKEN"))  # In GitHub Actions
        ]
        
        for source, token in token_sources:
            if token:
                print(f"🔑 Using GitHub token from: {source}")
                return token
                
        print("⚠️ No GitHub token found. API limits will be severely restricted.")
        print("💡 Set GITHUB_TOKEN env var or run 'gh auth login' for higher limits")
        return None
    
    def _get_gh_token(self) -> Optional[str]:
        """Extract token from GitHub CLI"""
        try:
            result = subprocess.run(
                ["gh", "auth", "token"], 
                capture_output=True, 
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def get_rate_limit_info(self) -> RateLimit:
        """Get current rate limit status from GitHub API"""
        url = "https://api.github.com/rate_limit"
        headers = {}
        
        if self.token:
            headers["Authorization"] = f"token {self.token}"
            
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            core_limits = data["rate"]["core"]
            rate_limit = RateLimit(
                limit=core_limits["limit"],
                remaining=core_limits["remaining"], 
                reset_timestamp=core_limits["reset"],
                used=core_limits["used"]
            )
            
            self.last_rate_limit = rate_limit
            return rate_limit
            
        except Exception as e:
            print(f"⚠️ Could not fetch rate limit info: {e}")
            # Return conservative defaults
            return RateLimit(
                limit=60 if not self.token else 5000,
                remaining=30 if not self.token else 4000,
                reset_timestamp=int(time.time()) + 3600,
                used=0
            )
    
    def check_rate_limit_before_request(self, requests_needed: int = 1) -> bool:
        """Check if we can make requests without hitting limits"""
        with self.rate_limit_lock:
            rate_limit = self.get_rate_limit_info()
            
            # Conservative buffer (keep 10% of limit in reserve)
            buffer = max(10, rate_limit.limit * 0.1)
            available = rate_limit.remaining - buffer
            
            if available >= requests_needed:
                return True
            
            # We're near the limit
            wait_time = rate_limit.time_until_reset
            print(f"⏳ Rate limit approaching: {rate_limit.remaining}/{rate_limit.limit}")
            print(f"⏳ Waiting {wait_time}s until reset ({rate_limit.reset_time})")
            
            if wait_time < 300:  # Less than 5 minutes
                time.sleep(wait_time + 5)  # Add 5s buffer
                return True
            else:
                print("⚠️ Rate limit reset too far away. Reduce concurrency or try later.")
                return False
    
    def get_optimal_worker_count(self) -> int:
        """Calculate optimal worker count based on rate limits"""
        rate_limit = self.get_rate_limit_info()
        
        # Each worker typically makes 3-5 API calls per job
        calls_per_worker = 4
        
        # Calculate safe concurrency (with 20% buffer)
        safe_requests = int(rate_limit.remaining * 0.8)
        optimal_workers = max(1, safe_requests // calls_per_worker)
        
        # Cap based on token type
        if not self.token:
            max_workers = 2  # Very conservative for unauthenticated
        elif rate_limit.limit <= 60:
            max_workers = 4  # Personal token
        else:
            max_workers = 20  # GitHub App or Enterprise
            
        recommended = min(optimal_workers, max_workers)
        
        print(f"📊 Rate Limit Analysis:")
        print(f"   • Available requests: {rate_limit.remaining}/{rate_limit.limit}")
        print(f"   • Recommended workers: {recommended}")
        print(f"   • Requests per worker: ~{calls_per_worker}")
        
        return recommended
    
    def create_authenticated_gh_command(self, base_cmd: List[str]) -> List[str]:
        """Add authentication to gh commands if needed"""
        if self.token and "GITHUB_TOKEN" not in os.environ:
            # Set token in environment for this command
            env_cmd = ["env", f"GITHUB_TOKEN={self.token}"] + base_cmd
            return env_cmd
        return base_cmd
    
    def get_api_limits_summary(self) -> Dict[str, any]:
        """Get comprehensive API limits summary"""
        rate_limit = self.get_rate_limit_info()
        
        return {
            "authenticated": bool(self.token),
            "token_type": self._detect_token_type(),
            "rate_limit": {
                "limit": rate_limit.limit,
                "remaining": rate_limit.remaining,
                "reset_time": rate_limit.reset_time.isoformat(),
                "usage_percent": (rate_limit.used / rate_limit.limit) * 100
            },
            "recommendations": {
                "max_workers": self.get_optimal_worker_count(),
                "batch_size": self._get_optimal_batch_size(),
                "wait_between_batches": self._get_wait_time()
            }
        }
    
    def _detect_token_type(self) -> str:
        """Detect the type of GitHub token being used"""
        if not self.token:
            return "unauthenticated"
        
        rate_limit = self.get_rate_limit_info()
        
        if rate_limit.limit >= 15000:
            return "github_app_installation"
        elif rate_limit.limit >= 5000:
            return "github_app_or_oauth"
        elif rate_limit.limit >= 1000:
            return "personal_access_token"
        else:
            return "basic_auth_or_limited"
    
    def _get_optimal_batch_size(self) -> int:
        """Get optimal batch size for processing jobs"""
        rate_limit = self.get_rate_limit_info()
        
        if rate_limit.limit >= 5000:
            return 20  # Can handle large batches
        elif rate_limit.limit >= 1000:
            return 10  # Medium batches
        else:
            return 5   # Small batches
    
    def _get_wait_time(self) -> float:
        """Get recommended wait time between API calls"""
        rate_limit = self.get_rate_limit_info()
        
        if rate_limit.limit >= 5000:
            return 0.1  # 100ms between calls
        elif rate_limit.limit >= 1000:
            return 0.5  # 500ms between calls
        else:
            return 1.0  # 1s between calls

def setup_github_authentication():
    """Interactive setup for GitHub authentication"""
    print("🔧 GitHub Authentication Setup")
    print("=" * 50)
    
    handler = GitHubAPILimitHandler()
    summary = handler.get_api_limits_summary()
    
    print(f"📊 Current Status:")
    print(f"   • Authenticated: {summary['authenticated']}")
    print(f"   • Token Type: {summary['token_type']}")
    print(f"   • Rate Limit: {summary['rate_limit']['remaining']}/{summary['rate_limit']['limit']}")
    print(f"   • Usage: {summary['rate_limit']['usage_percent']:.1f}%")
    
    if not summary['authenticated']:
        print(f"\n💡 To increase API limits:")
        print(f"   1. Create a Personal Access Token:")
        print(f"      https://github.com/settings/tokens")
        print(f"   2. Set environment variable:")
        print(f"      export GITHUB_TOKEN=your_token_here")
        print(f"   3. Or use GitHub CLI:")
        print(f"      gh auth login")
        
        print(f"\n📈 Rate Limit Comparison:")
        print(f"   • Unauthenticated: 60 requests/hour")
        print(f"   • Personal Token: 5,000 requests/hour")  
        print(f"   • GitHub App: 15,000 requests/hour")
    
    print(f"\n🚀 Recommendations:")
    print(f"   • Max concurrent workers: {summary['recommendations']['max_workers']}")
    print(f"   • Optimal batch size: {summary['recommendations']['batch_size']}")
    print(f"   • Wait between batches: {summary['recommendations']['wait_between_batches']}s")
    
    return handler

if __name__ == "__main__":
    setup_github_authentication()