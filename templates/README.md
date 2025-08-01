# GitHub Actions Templates

Minimalist, sensible baseline templates for different programming languages and project types. These templates provide fast, token-efficient workflow generation without requiring Claude for basic CI/CD setups.

## Available Templates

### Language-Specific CI Templates

| Language | Template | Features |
|----------|----------|----------|
| **Python** | `python-ci.yml` | Python 3.9-3.12 matrix, pip caching, flake8, pytest |
| **Node.js** | `node-ci.yml` | Node 18,20,22 matrix, npm caching, lint detection, tests |
| **Rust** | `rust-ci.yml` | Stable toolchain, cargo caching, fmt, clippy, tests |
| **Go** | `go-ci.yml` | Go 1.21-1.23 matrix, module caching, vet, tests, build |
| **Java** | `java-ci.yml` | JDK 11,17,21 matrix, Maven/Gradle detection, tests |
| **PHP** | `php-ci.yml` | PHP 8.1-8.3 matrix, Composer caching, PHPUnit |
| **Ruby** | `ruby-ci.yml` | Ruby 3.1-3.3 matrix, bundler caching, RuboCop, rake |
| **C#/.NET** | `dotnet-ci.yml` | .NET 6,7,8 matrix, restore, build, test |
| **Generic** | `generic-ci.yml` | Script detection, Makefile support, minimal setup |

### Security Template

| Template | Features |
|----------|----------|
| **Security** | `security.yml` | Trivy scanning, CodeQL analysis, SARIF uploads |

## Template Features

### 🎯 **Minimalist Design**
- Essential CI/CD steps only
- No bloat or unnecessary complexity
- Fast execution times

### ⚡ **Performance Optimized**
- Proper dependency caching for each language
- Matrix builds where beneficial
- Efficient step ordering

### 🛡️ **Security Conscious**
- Latest stable action versions
- Minimal required permissions
- Security scanning integration

### 🔧 **Smart Detection**
- Conditional steps based on file presence
- Graceful handling of missing dependencies
- Framework-aware configurations

## Usage

### With Template Manager
```python
from template_manager import TemplateManager

tm = TemplateManager()

# Get Python template
python_ci = tm.get_template('python')

# Get security template
security = tm.get_security_template()

# List all templates
templates = tm.list_templates()
```

### With Minimal Improver
```bash
# Uses templates automatically - no Claude needed for basic workflows
./github-actions-improver-minimal.py --mode create
```

### Direct File Usage
```bash
# Copy template directly
cp templates/python-ci.yml .github/workflows/ci.yml
```

## Template Customization

Templates are designed to work out-of-the-box but can be customized:

### Python Template Customizations
- Modify Python version matrix in `strategy.matrix.python-version`
- Add/remove linting tools in the lint step
- Customize test commands in the test step

### Node.js Template Customizations  
- Adjust Node version matrix in `strategy.matrix.node-version`
- Modify package manager (npm/yarn/pnpm) detection
- Add build steps if needed

### Security Template Customizations
- Configure Trivy scan types and formats
- Adjust CodeQL languages and queries
- Add additional security tools (Snyk, etc.)

## Template Design Principles

### 1. **Convention over Configuration**
- Use standard file locations and naming
- Follow ecosystem best practices
- Minimal setup required

### 2. **Fail-Safe Defaults**
- Graceful handling of missing files
- Conditional execution for optional tools
- Reasonable fallbacks

### 3. **Performance First**
- Aggressive caching strategies
- Parallel execution where possible
- Minimal dependencies

### 4. **Security by Default**
- Latest action versions
- Proper permission scoping
- Vulnerability scanning integration

## Adding New Templates

To add support for a new language:

1. **Create template file**: `templates/newlang-ci.yml`
2. **Follow naming convention**: `{language}-ci.yml`
3. **Include standard features**:
   - Checkout step
   - Language setup with version matrix
   - Dependency caching
   - Build/test/lint steps
   - Conditional execution for optional tools

4. **Update template manager**: Add mapping in `template_manager.py`
5. **Test thoroughly**: Ensure template works across different project structures

### Template Checklist
- [ ] Uses latest stable action versions
- [ ] Includes appropriate version matrix
- [ ] Has dependency caching configured
- [ ] Handles missing dependencies gracefully
- [ ] Includes basic linting/testing steps
- [ ] Follows language ecosystem conventions
- [ ] Is minimal but complete
- [ ] Works with common project structures

## Benefits over Claude Generation

### ⚡ **Speed**
- **Instant**: No API calls or generation time
- **Reliable**: No timeouts or rate limits
- **Consistent**: Same output every time

### 💰 **Cost Efficient**
- **Token Savings**: No tokens used for basic workflows
- **Rate Limit Friendly**: No API usage for common cases
- **Scalable**: Handle hundreds of repositories quickly

### 🎯 **Quality**
- **Tested**: Templates are verified and battle-tested
- **Best Practices**: Incorporate community feedback
- **Maintained**: Regular updates with latest actions

### 🔄 **Hybrid Approach**
- **Templates**: For standard CI/CD workflows (90% of cases)
- **Claude**: For complex customizations and edge cases (10% of cases)
- **Best of Both**: Speed + Intelligence when needed

This template system allows the GitHub Actions Improver to be blazingly fast for common use cases while still leveraging Claude's intelligence for complex scenarios.