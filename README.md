# Claude GitHub Actions Improver

A Claude Agent that automatically improves GitHub Actions workflows in any repository. When run in a GitHub repo, it:

1. **Creates relevant Actions** if none exist (based on project type detection)
2. **Improves existing workflows** with DRY principles and best practices  
3. **Fixes failing workflows** by spawning specialized agents for each failure

## Features

- 🔍 **Smart Project Detection** - Automatically detects Node.js, Python, Rust, Go, Java, PHP, Ruby, .NET projects
- 🚀 **Workflow Creation** - Creates CI/CD, security scanning, and release workflows tailored to your project
- 🔧 **DRY Improvements** - Extracts common steps into composite actions and reusable workflows
- 🔨 **Failure Fixing** - Analyzes and fixes common workflow issues using specialized Claude agents
- ⚡ **Best Practices** - Updates action versions, improves caching, enhances security

## Prerequisites

1. **Claude CLI** - Install from [https://docs.anthropic.com/claude/docs](https://docs.anthropic.com/claude/docs)
2. **Python 3.7+** 
3. **Git repository** - Must be run from within a git repository
4. **GitHub CLI** (optional) - For better failure detection: `gh auth login`

## Installation

```bash
# Clone or download the script
curl -O https://raw.githubusercontent.com/your-repo/claude-github-actions-fixer/main/github-actions-improver.py
chmod +x github-actions-improver.py
```

## Usage

### Basic Usage

Run in any Git repository to automatically improve GitHub Actions:

```bash
./github-actions-improver.py
```

### Mode Options

```bash
# Only create workflows (if none exist)
./github-actions-improver.py --mode create

# Only improve existing workflows  
./github-actions-improver.py --mode improve

# Only fix failing workflows
./github-actions-improver.py --mode fix

# Do everything (default)
./github-actions-improver.py --mode auto
```

### Specify Repository Path

```bash
./github-actions-improver.py --repo-path /path/to/your/repo
```

## What It Does

### 1. Creates Workflows (if none exist)

Detects your project type and creates appropriate workflows:

**Node.js Project:**
- CI pipeline with build, test, lint
- Security scanning with npm audit
- Release automation with semantic versioning

**Python Project:**  
- CI with multiple Python versions
- Security scanning with safety/bandit
- Package publishing to PyPI

**Rust Project:**
- CI with cargo build/test/clippy
- Security audit with cargo-audit
- Crate publishing

**Go Project:**
- CI with multiple Go versions
- Security scanning with gosec
- Module publishing

### 2. Improves Existing Workflows

Applies DRY principles and best practices:

- **Extracts common steps** into composite actions (`.github/actions/`)
- **Creates reusable workflows** for repeated patterns
- **Updates action versions** to latest stable
- **Improves caching** for dependencies and build artifacts
- **Enhances security** with pinned versions and minimal permissions
- **Optimizes performance** with better parallelization

### 3. Fixes Failing Workflows

Spawns specialized Claude agents to fix common issues:

- Outdated action versions
- Missing dependencies
- YAML syntax errors  
- Environment setup problems
- Permission issues
- Caching configuration problems
- Matrix build issues

## Example Output

```
🤖 Claude GitHub Actions Improver
📁 Repository: /path/to/your/project
🎯 Mode: auto

🔍 Detected project type: node
🚀 Creating GitHub Actions workflows...
✅ Workflows created successfully

🔧 Improving 3 existing workflows...
✅ Workflows improved successfully

🔨 Found 1 potentially failing workflows
🔍 Analyzing and fixing: ci
✅ Fixed issues in ci

🎉 GitHub Actions improvement complete!

Next steps:
- Review the created/modified workflow files
- Test the workflows by pushing changes or running them manually
- Commit and push the improvements to your repository
```

## Created Files

The agent may create or modify:

```
.github/
├── workflows/
│   ├── ci.yml              # Main CI/CD pipeline
│   ├── security.yml        # Security scanning
│   └── release.yml         # Release automation
└── actions/                # Composite actions (for DRY)
    ├── setup-node/
    ├── cache-dependencies/
    └── run-tests/
```

## Supported Project Types

- **Node.js** - `package.json`, `yarn.lock`, `pnpm-lock.yaml`
- **Python** - `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`  
- **Rust** - `Cargo.toml`
- **Go** - `go.mod`, `go.sum`
- **Java** - `pom.xml`, `build.gradle`, `build.gradle.kts`
- **PHP** - `composer.json`
- **Ruby** - `Gemfile`, `Rakefile`
- **C#/.NET** - `*.csproj`, `*.sln`, `*.fsproj`, `*.vbproj`
- **Docker** - `Dockerfile`, `docker-compose.yml`
- **Generic** - Basic CI workflow for unknown project types

## Troubleshooting

### Claude CLI Not Found
```bash
# Install Claude CLI
curl -fsSL https://claude.ai/cli/install.sh | sh
```

### Not in Git Repository
```bash
# Initialize git repository
git init
```

### GitHub CLI Issues
```bash
# Install and authenticate GitHub CLI for better failure detection
gh auth login
```

### Permission Issues
```bash
# Make script executable
chmod +x github-actions-improver.py
```

## Advanced Usage

### Custom Prompts

The agent uses sophisticated prompts to guide Claude's analysis. You can modify the prompts in the script to customize behavior for your specific needs.

### Integration with CI/CD

You can run this agent as part of your own CI/CD pipeline:

```yaml
- name: Improve GitHub Actions
  run: |
    python github-actions-improver.py --mode improve
    git add .github/
    git commit -m "Improve GitHub Actions workflows" || exit 0
```

## Contributing

This tool is designed to be extensible. You can:

1. Add support for new project types in `detect_project_type()`
2. Customize workflow templates in the prompts
3. Add new improvement patterns
4. Enhance failure detection logic

## License

MIT License - feel free to use and modify for your projects.