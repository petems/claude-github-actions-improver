# Claude Slash Commands for GitHub Actions

Quick reference for GitHub Actions slash commands in Claude CLI.

## Installation

```bash
chmod +x install-slash-commands.sh
./install-slash-commands.sh
```

## Available Commands

### 🚀 **Primary Commands**

| Command | Description | Use Case |
|---------|-------------|-----------|
| `/actions` | **Full GitHub Actions improvement** | Complete analysis, creation, improvement, and fixing |
| `/ci` | **Quick CI workflow creation** | Fast CI/CD pipeline setup |

### 🔧 **Specific Operations**

| Command | Description | Use Case |
|---------|-------------|-----------|
| `/actions-create` | **Create GitHub Actions workflows** | New project setup |
| `/actions-improve` | **Improve existing workflows** | Modernize and optimize |
| `/actions-fix` | **Fix failing workflows** | Debug and repair issues |
| `/actions-security` | **Add security scanning** | Enhance security posture |

## Usage Examples

### In any Git repository:

```bash
cd /path/to/your/project
claude
```

Then use slash commands:

```
> /actions
# Analyzes project, creates/improves/fixes all workflows

> /ci  
# Quick CI pipeline creation

> /actions-security
# Adds comprehensive security scanning

> /actions-fix
# Fixes common workflow issues
```

## What Each Command Does

### `/actions` - Full Analysis
- 🔍 **Detects** project type (Python, Node.js, Rust, Go, Java, etc.)
- 🚀 **Creates** workflows if none exist (CI, security, release)
- 🔧 **Improves** existing workflows with best practices
- 🔨 **Fixes** common issues (outdated actions, syntax errors)
- ⚡ **Concurrent** processing of multiple workflows

### `/ci` - Quick CI Setup
- 🎯 **Fast** CI/CD pipeline creation
- 📋 **Project-aware** testing and linting
- 🏗️ **Matrix builds** where appropriate
- 💾 **Intelligent caching** strategies

### `/actions-create` - New Workflows
- 📁 **Project analysis** and type detection
- 🛠️ **CI/CD pipelines** with build, test, lint
- 🔒 **Security scanning** workflows
- 📦 **Release automation** (if applicable)
- 🎨 **Modern best practices** and latest actions

### `/actions-improve` - Modernization
- 🆙 **Latest action versions** with SHA pinning
- 🛡️ **Security hardening** (minimal permissions, harden-runner)
- ⚡ **Performance optimization** (caching, parallelization)
- 🏗️ **Matrix improvements** (fail-fast: false, proper versions)
- 📝 **Better naming** and organization

### `/actions-fix` - Issue Resolution
- 🔧 **Outdated actions** → Latest versions
- ❌ **Syntax errors** → Proper YAML
- 📦 **Missing dependencies** → Proper installation
- 🔐 **Permission issues** → Correct GITHUB_TOKEN scopes
- 💾 **Caching problems** → Optimized cache strategies

### `/actions-security` - Security Enhancement
- 🔍 **Dependency scanning** (npm audit, safety, cargo-audit)
- 🛡️ **SAST analysis** (CodeQL, security linters)
- 📋 **License compliance** checking
- 🔒 **Security best practices** (pinned versions, minimal permissions)
- ⏰ **Scheduled scans** (weekly security checks)

## Project Type Detection

The commands automatically detect and optimize for:

| Language | Detection Files | Generated Workflows |
|----------|----------------|-------------------|
| **Python** | `requirements.txt`, `pyproject.toml`, `setup.py` | Python 3.9-3.12 matrix, pytest, flake8 |
| **Node.js** | `package.json`, `yarn.lock`, `pnpm-lock.yaml` | Node 18,20,22 matrix, npm test, eslint |
| **Rust** | `Cargo.toml` | Stable rust, cargo test, clippy |
| **Go** | `go.mod`, `go.sum` | Go 1.20-1.22 matrix, go test, go vet |
| **Java** | `pom.xml`, `build.gradle` | Multiple JDK versions, Maven/Gradle |
| **PHP** | `composer.json` | Multiple PHP versions, PHPUnit |
| **Ruby** | `Gemfile`, `Rakefile` | Multiple Ruby versions, RSpec |
| **C#/.NET** | `*.csproj`, `*.sln` | Multiple .NET versions, dotnet test |

## Concurrent Processing

All commands use concurrent processing:
- 🔄 **4 parallel workers** for workflow processing
- ⚡ **Real-time status** updates (`✅ ci.yml`, `❌ security.yml`)
- 🛡️ **Error isolation** (one failure doesn't stop others)
- ⏱️ **60-second timeouts** per workflow to prevent hanging

## File Structure Created

```
.github/
├── workflows/
│   ├── ci.yml              # Main CI/CD pipeline
│   ├── security.yml        # Security scanning
│   └── release.yml         # Release automation
└── actions/                # Composite actions (DRY)
    ├── setup-env/
    ├── cache-deps/
    └── run-tests/
```

## Tips

### 🎯 **For New Projects**
```
> /ci
# Quick start with essential CI pipeline
```

### 🔧 **For Existing Projects**
```
> /actions
# Full analysis and improvement
```

### 🛡️ **For Security Focus**
```
> /actions-security
# Add comprehensive security scanning
```

### 🔨 **For Troubleshooting**
```
> /actions-fix
# Fix failing or problematic workflows
```

## Configuration Location

Slash commands are stored in:
- **macOS**: `~/Library/Application Support/claude/settings.json`
- **Linux**: `~/.config/claude/settings.json`

## Troubleshooting

### Commands not appearing?
1. Restart Claude CLI: `claude --help`
2. Check settings file exists and has proper JSON syntax
3. Re-run installation: `./install-slash-commands.sh`

### Commands not working in repository?
1. Ensure you're in a Git repository: `git status`
2. Commands require `working_directory_required: true`
3. Use from repository root directory

### Want to customize commands?
Edit the settings.json file directly or modify `claude-slash-commands.json` and re-install.

---

🎉 **Ready to use!** Navigate to any Git repository and try `/actions` or `/ci`.