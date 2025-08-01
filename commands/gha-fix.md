# /gha:fix - Intelligent GitHub Actions Failure Resolution

## Workflow: Analyze → Identify → Fix → Verify → Report

**Target:** $ARGUMENTS (Default: analyze last 14 days of failures)

**Scope:** Systematic resolution of GitHub Actions workflow failures using intelligent log analysis and targeted fixes

## 🎯 Interactive Mode Instructions
**IMPORTANT**: Provide real-time feedback throughout the process. Use this structure:

1. **Start with progress indicator**: "🔍 Starting GitHub Actions failure analysis..."
2. **Stream updates as you work**: 
   - "📊 Found 8 failed runs in last 14 days..."
   - "🔍 Analyzing workflow: CI (run #1234)..."
   - "⚠️ Detected npm ENOENT error with 0.95 confidence..."
   - "✅ Applied dependency fix to package.json step..."
3. **Show intermediate results**: Present findings after each major step
4. **Ask for confirmation**: Before applying high-impact fixes
5. **Provide final summary**: Comprehensive report at the end

**Format**: Use emojis, progress indicators, and clear status messages throughout.

## Execution Steps

### 1. **Failure Detection & Analysis**
   - Fetch recent workflow runs using GitHub CLI: `gh run list --limit 50 --json`
   - Filter for failed runs within specified timeframe (default: 14 days)
   - Download detailed logs for each failed job: `gh run view <id> --log`
   - Parse logs for error patterns and failure signatures

### 2. **Pattern Recognition & Classification**
   - **Node.js Failures**: npm ENOENT, peer dependencies, package not found, version conflicts
   - **Python Failures**: ImportError, ModuleNotFoundError, SyntaxError, IndentationError
   - **Test Failures**: Unit test assertions, mock failures, timeout issues
   - **Build Failures**: Compilation errors, dependency resolution, environment setup
   - **Infrastructure**: Docker issues, cache corruption, permission problems

### 3. **Root Cause Analysis**
   - Extract error context: file paths, line numbers, specific error messages
   - Determine failure confidence score based on pattern matching (0.0-1.0)
   - Generate specific fix recommendations based on error type
   - Identify required workflow modifications vs code changes

### 4. **Intelligent Fix Application**
   - **High Confidence (0.8+)**: Apply fixes automatically with user confirmation
   - **Medium Confidence (0.5-0.8)**: Present options with explanations
   - **Low Confidence (<0.5)**: Provide diagnostic information for manual review
   - Create targeted workflow modifications addressing root causes

### 5. **Verification & Reporting**
   - Validate YAML syntax of modified workflows
   - Generate comprehensive fix report with before/after comparisons
   - Document applied changes and rationale
   - Suggest follow-up actions or monitoring

## Command Parameters

### **Timeframe Control**
- `--days N` - Analyze failures from last N days (default: 14)
- `--since DATE` - Analyze failures since specific date (YYYY-MM-DD)
- `--runs N` - Limit analysis to N most recent failed runs (default: 10)

### **Scope Control**
- `--workflow NAME` - Focus on specific workflow only
- `--job NAME` - Analyze specific job failures only
- `--severity LEVEL` - Filter by failure severity (critical|high|medium|low)

### **Fix Behavior**
- `--auto` - Automatically apply high-confidence fixes
- `--interactive` - Present options for each fix (default)
- `--dry-run` - Analyze and report without making changes
- `--backup` - Create backup before applying fixes

### **Output Control**
- `--format FORMAT` - Output format (markdown|json|text)
- `--verbose` - Include detailed diagnostic information
- `--save PATH` - Save analysis report to file

## Example Workflows

### **Quick Fix Session**
```bash
/gha:fix --days 7 --auto --backup
```
*Analyzes last 7 days, applies high-confidence fixes with backup*

### **Targeted Analysis**
```bash
/gha:fix --workflow ci --interactive --verbose
```
*Focus on CI workflow with interactive fixing and detailed output*

### **Comprehensive Review**
```bash
/gha:fix --days 30 --dry-run --save analysis-report.md
```
*Full 30-day analysis without changes, save detailed report*

## Success Criteria

### **Analysis Quality**
- ✅ All recent failures identified and categorized
- ✅ Error patterns recognized with >80% confidence where possible
- ✅ Root cause analysis completed for each failure type
- ✅ Fix recommendations generated with confidence scores

### **Fix Effectiveness**
- ✅ Workflow syntax remains valid after modifications
- ✅ Applied fixes target identified root causes
- ✅ Changes preserve existing workflow functionality
- ✅ Modifications follow GitHub Actions best practices

### **Documentation**
- ✅ Comprehensive report generated showing all findings
- ✅ Before/after comparisons for modified workflows
- ✅ Rationale documented for each applied fix
- ✅ Follow-up recommendations provided

## Common Failure Patterns & Fixes

### **npm/Node.js Issues**
```
Pattern: "npm ERR! ENOENT: no such file or directory, open 'package.json'"
Fix: Add working-directory or verify repository structure
Confidence: 0.95
```

### **Python Import Errors**
```
Pattern: "ModuleNotFoundError: No module named 'requests'"
Fix: Add missing dependency to requirements.txt or pip install step
Confidence: 0.90
```

### **Test Failures**
```
Pattern: "FAILED tests/test_api.py::test_user_creation"
Fix: Analyze test output and fix test logic or implementation
Confidence: 0.70 (requires context analysis)
```

### **Cache Issues**
```
Pattern: "Warning: Failed to restore cache"
Fix: Update cache key patterns and add restore-keys fallback
Confidence: 0.85
```

## Integration Points

- **GitHub CLI**: Required for accessing workflow run data and logs
- **Claude Agent Scripts**: Uses enhanced failure analysis engine
- **Workflow Templates**: Falls back to template-based fixes when needed
- **Backup System**: Integrates with git for change tracking

## Output Format

### **Summary Report**
```markdown
# GitHub Actions Failure Analysis Report

## Executive Summary
- **Analysis Period**: Last 14 days
- **Total Runs Analyzed**: 47
- **Failed Runs**: 8 (17%)
- **Patterns Identified**: 5 unique failure types
- **Fixes Applied**: 6 high-confidence fixes
- **Success Rate**: 75% of failures resolved

## Detailed Findings
[Comprehensive breakdown of each failure and applied fix]
```

This command transforms reactive workflow debugging into a systematic, intelligent process that learns from actual failure patterns and applies targeted solutions.