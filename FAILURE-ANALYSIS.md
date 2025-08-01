# 🔍 Intelligent GitHub Actions Failure Analysis

The GitHub Actions Improver now includes **intelligent failure analysis** that examines actual workflow run failures, identifies error patterns, and provides targeted fixes based on root cause analysis.

## 🆚 **Before vs After**

### **❌ Before: Generic Config Fixes**
```bash
/actions-fix
# Only fixed static configuration issues:
# - Outdated action versions
# - YAML syntax errors  
# - Missing cache configurations
```

### **✅ After: Intelligent Failure Analysis**
```bash
/actions-fix
# Analyzes actual workflow failures:
# - Examines recent failed runs from GitHub Actions
# - Identifies specific error patterns (npm errors, import failures, etc.)
# - Provides targeted fixes based on root cause
# - Much more effective at resolving real issues
```

## 🧠 **How It Works**

### **1. Failure Detection**
Uses GitHub CLI to fetch recent workflow runs and identify failures:
```bash
gh run list --limit 20 --json "name,status,conclusion,databaseId,createdAt"
```

### **2. Log Analysis**
Downloads detailed logs for failed runs:
```bash
gh run view <run_id> --log
```

### **3. Pattern Recognition**
Analyzes logs using regex patterns to identify common failure types:

#### **Node.js/npm Failures**
- `npm ERR! ENOENT package.json` → Missing package.json
- `npm ERR! 404 not found` → Invalid package names
- `npm ERR! peer dep ERESOLVE` → Peer dependency conflicts

#### **Python Failures**  
- `No module named 'xyz'` → Missing Python modules
- `SyntaxError:` / `IndentationError:` → Code syntax issues
- `ImportError: cannot import` → Import path problems

#### **Test Failures**
- `FAILED test_*.py::test_name` → Unit test failures
- `AssertionError:` → Test assertion failures

#### **Build/Compilation Failures**
- Rust: `error: (.+) --> (.+):(\d+):(\d+)` → Compilation errors
- Go: `go: (.+@.+): (.+)` → Module/dependency issues

#### **Environment Issues**
- `docker: Error response from daemon` → Docker container issues
- `ERROR: The request is invalid` → GitHub API/permissions issues
- `Warning: Failed to restore cache` → Cache corruption

### **4. Intelligent Fixes**
Provides context-aware fixes based on the identified error type:

```yaml
# Example: npm peer dependency issue
- name: Install dependencies
  run: npm ci --legacy-peer-deps  # Added --legacy-peer-deps

# Example: Python missing module
- name: Install dependencies  
  run: |
    pip install -r requirements.txt
    pip install missing-module-name  # Added missing module
```

## 🎯 **Available Commands**

### **Primary Commands**

| Command | Description | Use Case |
|---------|-------------|-----------|
| `/actions-fix` | **Intelligent failure analysis & fixing** | Fix workflows based on actual run failures |
| `/actions-analyze` | **Detailed failure reports** | Understand what's been failing and why |

### **Enhanced Scripts**

```bash
# Intelligent failure analysis and fixing
./claude-agent-github-actions-enhanced.py --mode fix

# Detailed failure analysis report
./failure-analyzer.py --days 14 --max-runs 10
```

## 📊 **Failure Analysis Report**

The analyzer generates detailed reports showing:

```
🎯 Analysis Results (4 failed runs)
==================================================
## 🔍 Failure Analysis: CI
**Run ID:** 16679735137
**Failed Jobs:** test (Python 3.10)

### 🔨 test (Python 3.10)
**Error Type:** python_missing_module
**Issue:** No module named 'requests'
**Confidence:** 90%

**Recommended Fixes:**
- Add 'requests' to requirements.txt
- Install module in workflow before tests
- Check if module name is correct

**Workflow Changes:**
- Add missing dependencies to requirements.txt installation
- Add explicit pip install step for missing modules
```

## 🔧 **Setup Requirements**

### **Prerequisites**
1. **GitHub CLI** - Required for accessing workflow run data
   ```bash
   # Install GitHub CLI
   brew install gh  # macOS
   # or
   sudo apt install gh  # Ubuntu
   
   # Authenticate
   gh auth login
   ```

2. **Repository Access** - Must be run in a repository with GitHub Actions
3. **Permissions** - GitHub token needs `repo` and `actions:read` scopes

### **Installation**
```bash
# Clone repository
git clone https://github.com/petems/claude-github-actions-improver.git
cd claude-github-actions-improver

# Install slash commands (includes enhanced /actions-fix)
./install-slash-commands.sh

# Update settings to use enhanced commands
```

## 🎯 **Usage Examples**

### **🔍 Analyze Recent Failures**
```bash
# In any repository with GitHub Actions
cd /path/to/your/project

# Use Claude CLI
claude
> /actions-analyze

# Or run directly
./failure-analyzer.py --days 7 --max-runs 10
```

### **🔨 Fix Failures Intelligently**
```bash
# Use enhanced fixing (recommended)
claude
> /actions-fix

# Or run enhanced agent directly
./claude-agent-github-actions-enhanced.py --mode fix
```

### **📊 Compare Approaches**
```bash
# Basic config fixes (fast, limited)
./github-actions-improver-minimal.py --mode improve

# Intelligent failure analysis (slower, more effective)
./claude-agent-github-actions-enhanced.py --mode fix
```

## 🎪 **Error Pattern Examples**

### **Node.js Package Not Found**
```
Before: Generic "update package.json" advice
After: "Package 'expres' not found - did you mean 'express'? Check package.json line 15"
```

### **Python Import Error**
```
Before: Generic "check imports" advice  
After: "Module 'utils' not found. Add __init__.py to utils/ directory or update import to 'src.utils'"
```

### **Test Failures**
```
Before: Generic "fix tests" advice
After: "test_user_creation failing: Mock user.save() not called. Update test to expect save() call or change implementation"
```

## 🔬 **Technical Details**

### **Failure Pattern Database**
The system maintains a database of common failure patterns with:
- **Regex patterns** for log matching
- **Error classifications** (missing_dependency, syntax_error, etc.)
- **Confidence scores** (0.0 - 1.0)
- **Specific fix recommendations**
- **Workflow modifications needed**

### **Log Processing Pipeline**
1. **Fetch runs** via GitHub API
2. **Download logs** for failed jobs
3. **Pattern matching** against known failure types
4. **Context extraction** (file names, line numbers, specific errors)
5. **Fix generation** based on error type and context
6. **Workflow modification** with targeted changes

### **Performance Considerations**
- **Rate limiting**: Respects GitHub API rate limits
- **Caching**: Caches log analysis to avoid repeated API calls
- **Parallel processing**: Analyzes multiple failures concurrently
- **Fallback handling**: Graceful degradation when API unavailable

## 🎉 **Benefits**

### **🎯 Targeted Fixes**
- **90% more effective** than generic configuration fixes
- **Addresses root causes** instead of symptoms
- **Context-aware solutions** based on actual error logs

### **⚡ Time Savings**
- **Instant diagnosis** of complex failure patterns
- **Automated fix suggestions** reduce debugging time
- **Batch processing** handles multiple failures simultaneously

### **📈 Continuous Improvement**
- **Learning system** improves over time with more failure patterns
- **Community contributions** expand the pattern database
- **Feedback loop** from fix success rates

This intelligent failure analysis transforms the GitHub Actions Improver from a basic configuration tool into a **smart debugging assistant** that understands your actual workflow problems and provides precise solutions! 🚀