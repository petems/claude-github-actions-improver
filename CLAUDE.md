# Claude Agent: GitHub Actions Improver

This repository contains a Claude Agent that automatically improves GitHub Actions workflows in any repository.

## 🎯 Claude Slash Commands (Primary Interface)

The fastest way to use this agent is through Claude CLI slash commands. After installation, use these commands in any Git repository:

### Primary Commands
- `/actions` - **Full analysis and improvement** (create, improve, fix workflows)
- `/ci` - **Quick CI workflow creation** (fast setup for any project type)
- `/actions-minimal` - **Ultra-fast template-based workflows** (no Claude API calls)

### Specialized Commands  
- `/actions-create` - **Create new workflows** (CI, security, release)
- `/actions-improve` - **Improve existing workflows** (best practices, security)
- `/actions-fix` - **Fix failing workflows** (concurrent issue resolution)
- `/actions-security` - **Add security scanning** (vulnerability detection)

### Installation
```bash
git clone https://github.com/petems/claude-github-actions-improver.git
cd claude-github-actions-improver
./install-slash-commands.sh
```

## 💬 Natural Language Commands (Alternative)

You can also use natural language commands:

### Primary Commands
- `Improve GitHub Actions in this repository` - Full analysis and improvement
- `Create GitHub Actions workflows for this project` - Create new workflows if none exist
- `Fix failing GitHub Actions workflows` - Fix common issues in existing workflows

### Specific Operations
- `Analyze this project and create CI workflows` - Project-aware workflow creation
- `Update GitHub Actions to latest versions` - Modernize existing workflows
- `Add security scanning to GitHub Actions` - Enhance with security workflows

## Agent Capabilities

### 🔍 **Smart Project Detection**
- Automatically detects: Python, Node.js, Rust, Go, Java, PHP, Ruby, .NET
- Identifies test frameworks and project structure
- Analyzes existing workflows and dependencies

### 🚀 **Workflow Creation**
- **CI Pipelines**: Build, test, lint with proper caching
- **Security Scanning**: Dependency vulnerabilities, SAST analysis
- **Release Automation**: Semantic versioning, asset publishing
- **Matrix Builds**: Multiple language/OS versions where appropriate

### 🔧 **Concurrent Improvements**
- **Multi-threading**: Processes multiple workflows simultaneously
- **Best Practices**: Latest action versions with SHA pinning
- **Security Hardening**: Minimal permissions, security scanning
- **Performance**: Optimized caching, build parallelization

### 🔨 **Intelligent Fixing**
- **Common Issues**: Outdated actions, syntax errors, missing deps
- **Environment Problems**: Path issues, variable configuration
- **Permission Fixes**: GITHUB_TOKEN scopes, security policies
- **Matrix Optimization**: Proper failure handling, parallel execution

## Usage Examples

### 🎯 Slash Commands (Recommended):
```bash
# Navigate to any repository
cd /path/to/your/repo

# Use slash commands in Claude CLI
claude
> /actions          # Full improvement
> /ci               # Quick CI setup
> /actions-minimal  # Template-based (ultra-fast)
```

### 💬 Natural Language:
```bash
# Use natural language prompts
claude --prompt "Improve GitHub Actions in this repository"
claude --prompt "Create GitHub Actions workflows for this Python project"
claude --prompt "Fix the failing CI workflow and add security scanning"
```

### ⚡ Direct Scripts:
```bash
# Template-based (no Claude API calls)
./github-actions-improver-minimal.py --mode create

# Claude-powered (intelligent analysis)
./github-actions-improver-v2.py --mode auto
```

### From IDE (with Claude integration):
Just type any slash command or natural language prompt in your Claude conversation.

## Technical Details

### Concurrent Processing
The agent uses Python's `ThreadPoolExecutor` to process multiple workflows simultaneously:
- Up to 4 concurrent workflow improvements
- Real-time status updates for each workflow
- Robust error handling per workflow

### Project Type Detection
Automatically detects project types based on:
```
Python: requirements.txt, pyproject.toml, setup.py, *.py
Node.js: package.json, yarn.lock, pnpm-lock.yaml  
Rust: Cargo.toml
Go: go.mod, go.sum
Java: pom.xml, build.gradle
PHP: composer.json
Ruby: Gemfile, Rakefile
.NET: *.csproj, *.sln
```

### Generated Workflows
The agent creates workflows optimized for each project type:

**Python Projects:**
- Multi-version matrix (3.9, 3.10, 3.11, 3.12)
- pip caching and dependency installation
- pytest with coverage reporting
- flake8 linting with sensible rules

**Node.js Projects:**
- Multi-version matrix (18, 20, 22)
- npm/yarn caching
- Test and lint commands
- Build artifact handling

**Other Languages:**
- Language-specific toolchain setup
- Appropriate testing and linting tools
- Optimized caching strategies

## Installation

To use this agent in any repository:

1. **Install the agent:**
   ```bash
   ./install-agent.sh
   ```

2. **Use from any repository:**
   ```bash
   cd /path/to/any/repo
   claude --prompt "Improve GitHub Actions in this repository"
   ```

## Files Created/Modified

The agent will create or modify:
```
.github/
├── workflows/
│   ├── ci.yml              # Main CI/CD pipeline
│   ├── security.yml        # Security scanning (if applicable)
│   └── release.yml         # Release automation (if applicable)
└── actions/                # Composite actions (for DRY)
    ├── setup-env/
    ├── cache-deps/
    └── run-tests/
```

## Error Handling

The agent includes robust error handling:
- Timeouts for long-running Claude calls (60s per workflow)
- Graceful failure handling per workflow
- Detailed error reporting and status updates
- Continues processing other workflows if one fails

## Performance

- **Concurrent**: Processes multiple workflows simultaneously
- **Optimized Prompts**: Focused, concise prompts for faster responses  
- **Caching**: Intelligent caching strategies in generated workflows
- **Minimal Context**: Only includes relevant project files as context

This agent transforms any repository's GitHub Actions into modern, secure, and efficient workflows using the power of Claude AI.