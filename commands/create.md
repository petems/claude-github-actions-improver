# /gha:create - Intelligent GitHub Actions Workflow Creation

## Workflow: Detect → Design → Generate → Optimize → Validate

**Target:** $ARGUMENTS (Default: comprehensive workflow suite for detected project)

**Scope:** Create production-ready GitHub Actions workflows tailored to project type, structure, and requirements

## 🎯 Interactive Mode Instructions
**IMPORTANT**: Provide step-by-step feedback with progress indicators:

1. **Project Analysis Phase** (30-60 seconds):
   - "🔍 Analyzing project structure..."
   - "📋 Detected: Python project with pytest framework"
   - "🔍 Found dependencies: requirements.txt, pyproject.toml"
   - "📊 Project complexity: Medium (5 packages, 23 tests)"

2. **Workflow Design Phase** (15-30 seconds):
   - "🎨 Designing CI/CD architecture..."
   - "✅ Selected: Python matrix testing + security scanning"
   - "🔧 Optimizations: Aggressive caching, parallel jobs"

3. **Generation Phase** (30-45 seconds):
   - "📝 Generating ci.yml workflow..."
   - "🛡️ Creating security.yml with CodeQL + Trivy..."
   - "📦 Adding release.yml for automated deployments..."

4. **Validation & Summary**:
   - Show what was created before writing files
   - Ask for confirmation for any potentially disruptive changes
   - Provide file-by-file summary of generated workflows

**Format**: Use progress bars, emojis, and estimated time remaining where helpful.

## Execution Steps

### 1. **Project Analysis & Detection**
   - **Language Detection**: Scan for package.json, requirements.txt, Cargo.toml, go.mod, pom.xml, etc.
   - **Framework Identification**: Detect React, Django, Rails, Spring Boot, etc.
   - **Test Framework Discovery**: Jest, pytest, cargo test, go test, JUnit
   - **Build System Analysis**: npm/yarn, pip/poetry, cargo, go build, maven/gradle
   - **Deployment Context**: Docker, serverless, static sites, APIs

### 2. **Workflow Architecture Design**
   - **CI Pipeline Strategy**: Matrix builds, parallel jobs, dependency optimization
   - **Security Integration**: SAST, dependency scanning, secret detection
   - **Quality Gates**: Testing, linting, coverage thresholds
   - **Performance Considerations**: Caching strategies, artifact management
   - **Deployment Pipeline**: Environment promotion, rollback strategies

### 3. **Intelligent Generation**
   - **Template Selection**: Choose optimal base templates for detected stack
   - **Customization Logic**: Adapt templates to specific project needs
   - **Best Practice Integration**: Latest action versions, security hardening
   - **Conditional Logic**: Feature detection for optional tools (Docker, docs, etc.)
   - **Environment Configuration**: Secrets, variables, environment-specific settings

### 4. **Workflow Optimization**
   - **Performance Tuning**: Parallel execution, efficient caching, resource usage
   - **Security Hardening**: Minimal permissions, SHA pinning, secret handling
   - **Maintainability**: Clear naming, documentation, modular structure
   - **Monitoring Integration**: Failure notifications, metrics collection
   - **Cost Optimization**: Efficient runner usage, conditional execution

### 5. **Validation & Documentation**
   - **YAML Syntax Validation**: Ensure all workflows are syntactically correct
   - **Logic Verification**: Check job dependencies, condition logic, matrix configurations
   - **Security Review**: Validate permissions, secret usage, external dependencies
   - **Documentation Generation**: README updates, workflow descriptions, usage guides

## Command Parameters

### **Project Scope**
- `--type TYPE` - Force specific project type (node|python|rust|go|java|php|ruby|dotnet)
- `--framework FRAMEWORK` - Specify framework (react|django|rails|spring|laravel)
- `--template TEMPLATE` - Use specific template (minimal|standard|comprehensive)

### **Workflow Selection**
- `--ci-only` - Generate only CI/testing workflows
- `--security` - Include security scanning workflows
- `--release` - Add release/deployment workflows
- `--docs` - Include documentation generation workflows
- `--full` - Generate comprehensive workflow suite (default)

### **Customization Options**
- `--matrix VERSIONS` - Specify version matrix (e.g., "18,20,22" for Node.js)
- `--platforms OS` - Target platforms (ubuntu|windows|macos|all)
- `--cache STRATEGY` - Caching strategy (aggressive|conservative|none)
- `--notifications CHANNELS` - Notification channels (slack|email|teams)

### **Generation Behavior**
- `--force` - Overwrite existing workflows
- `--merge` - Merge with existing workflows where possible
- `--backup` - Create backup of existing workflows
- `--preview` - Show generated content without creating files

### **Output Control**
- `--output-dir DIR` - Custom output directory (default: .github/workflows)
- `--prefix PREFIX` - Add prefix to workflow file names
- `--format STYLE` - Code style (compact|readable|documented)

## Example Workflows

### **New Project Setup**
```bash
/gha:create --full --backup --notifications slack
```
*Complete workflow suite with backup and Slack notifications*

### **Minimal CI Only**
```bash
/gha:create --ci-only --template minimal --platforms ubuntu
```
*Basic CI pipeline, minimal template, Ubuntu only*

### **Comprehensive Production Setup**
```bash
/gha:create --full --security --release --matrix "3.9,3.10,3.11,3.12" --cache aggressive
```
*Full production setup with security, releases, Python matrix, aggressive caching*

### **Framework-Specific**
```bash
/gha:create --type node --framework react --docs --notifications teams
```
*React-specific workflows with documentation and Teams notifications*

## Generated Workflow Types

### **Core CI/CD Pipeline** (`ci.yml`)
- Multi-version/platform matrix builds
- Dependency installation and caching
- Code quality checks (linting, formatting)
- Comprehensive testing with coverage
- Build artifact generation
- Conditional deployment triggers

### **Security Scanning** (`security.yml`)
- **Dependency Scanning**: Snyk, GitHub Security Advisories
- **Code Analysis**: CodeQL, SonarCloud, Semgrep
- **Container Scanning**: Trivy, Docker Scout
- **Secret Detection**: GitLeaks, TruffleHog
- **License Compliance**: FOSSA, License Finder

### **Release Automation** (`release.yml`)
- **Semantic Versioning**: Automatic version bumping
- **Changelog Generation**: Conventional commits, release notes
- **Asset Building**: Binaries, packages, containers
- **Multi-Platform Releases**: GitHub Releases, package registries
- **Deployment Triggers**: Production environment updates

### **Documentation** (`docs.yml`)
- **API Documentation**: OpenAPI, JSDoc, Sphinx
- **Static Site Generation**: GitHub Pages, Netlify
- **Coverage Reports**: Code coverage badges and reports
- **Link Validation**: Broken link detection
- **Documentation Testing**: Ensure examples work

### **Maintenance** (`maintenance.yml`)
- **Dependency Updates**: Dependabot, Renovate integration
- **Automated Testing**: Regression testing, integration tests
- **Performance Monitoring**: Benchmark tracking
- **Health Checks**: Service availability, performance metrics

## Project-Specific Optimizations

### **Node.js Projects**
```yaml
# Intelligent package manager detection
- uses: actions/setup-node@v4
  with:
    node-version: ${{ matrix.node-version }}
    cache: ${{ steps.detect-pm.outputs.package-manager }}

# Smart script detection
- name: Run tests
  run: |
    if npm run test --silent 2>/dev/null; then
      npm run test
    elif npm run test:ci --silent 2>/dev/null; then
      npm run test:ci
    else
      npm test
    fi
```

### **Python Projects**
```yaml
# Multi-environment support
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    if [ -f requirements-dev.txt ]; then
      pip install -r requirements-dev.txt
    elif [ -f requirements.txt ]; then
      pip install -r requirements.txt
    elif [ -f pyproject.toml ]; then
      pip install -e .[dev]
    fi

# Framework-specific optimizations
- name: Run Django Tests
  if: contains(github.repository, 'django') || hashFiles('manage.py')
  run: python manage.py test
```

### **Rust Projects**
```yaml
# Optimized caching strategy
- name: Cache Rust dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      target
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
    restore-keys: |
      ${{ runner.os }}-cargo-

# Comprehensive testing
- name: Run tests
  run: |
    cargo test --verbose
    cargo test --release --verbose
    cargo bench --no-run
```

## Success Criteria

### **Workflow Quality**
- ✅ All generated workflows are syntactically valid YAML
- ✅ Workflows follow GitHub Actions best practices
- ✅ Security considerations properly implemented
- ✅ Performance optimizations applied appropriately

### **Project Integration**
- ✅ Workflows correctly detect and handle project structure
- ✅ Language/framework-specific optimizations applied
- ✅ Existing project patterns respected and enhanced
- ✅ Dependencies and build processes correctly identified

### **Maintainability**
- ✅ Clear, documented workflow structure
- ✅ Modular design with reusable components
- ✅ Easy to customize and extend
- ✅ Following consistent naming and organization

## Integration Points

- **Template System**: Leverages pre-built templates for speed
- **Project Analysis**: Deep project structure understanding
- **Security Scanning**: Integrates with multiple security tools
- **Notification Systems**: Supports Slack, Teams, email notifications
- **Deployment Platforms**: GitHub Pages, Heroku, AWS, Azure, GCP

This command transforms basic workflow creation into intelligent, project-aware automation that generates production-ready CI/CD pipelines tailored to your specific technology stack and requirements.