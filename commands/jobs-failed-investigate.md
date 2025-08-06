# /gha:jobs-failed-investigate - Deep Investigation of Failed GitHub Actions

## Workflow: Fetch → Analyze → Think → Report

**Target:** Investigate and analyze the latest failed GitHub Actions runs with deep thinking

**Scope:** Intelligent analysis of actual failure logs with pattern recognition and root cause analysis

## 🎯 Interactive Mode Instructions
**IMPORTANT**: Provide thoughtful, analytical feedback throughout:

1. **Start investigation**: "🔍 Investigating failed GitHub Actions runs..."
2. **Stream analysis**: 
   - "📊 Found 3 failed runs, downloading logs..."
   - "🧠 Analyzing CI failure: npm ENOENT error detected..."
   - "💭 Thinking through root cause: missing package.json in working directory..."
   - "🎯 Pattern identified: all failures related to dependency resolution..."
3. **Deep thinking**: Actually reason through each failure type
4. **Provide insights**: Explain what's happening and why
5. **Suggest next steps**: Recommend specific investigation or fixing approaches

**Format**: Use progressive disclosure - start broad, then dive deeper into each failure.

## Execution Steps

### 1. **Failure Discovery & Prioritization**
   - Fetch recent failed runs: `gh run list --limit 10 --status failure`
   - Download logs for each failure: `gh run view <id> --log`
   - Prioritize by recency, impact, and failure type

### 2. **Intelligent Log Analysis**
   - **Pattern Recognition**: Apply 15+ error pattern matching
   - **Context Extraction**: Pull file paths, line numbers, specific errors
   - **Classification**: Categorize by failure type (build, test, deploy, etc.)
   - **Confidence Scoring**: Rate understanding of each failure (0.0-1.0)

### 3. **Deep Thinking & Root Cause Analysis**
   - **Think through each failure**: Why did this specific error occur?
   - **Connect patterns**: Are multiple failures related?
   - **Consider context**: Branch, timing, recent changes
   - **Assess complexity**: Simple config vs complex architectural issue

### 4. **Investigation Report Generation**
   - **Executive Summary**: What's broken and why
   - **Detailed Analysis**: Per-failure breakdown with reasoning
   - **Recommendations**: Specific next steps for resolution
   - **Confidence Assessment**: How certain are we about each diagnosis

## Command Parameters

### **Scope Control**
- `--runs N` - Investigate N most recent failures (default: 5)
- `--workflow NAME` - Focus on specific workflow only
- `--branch NAME` - Investigate specific branch failures
- `--days N` - Look back N days for failures (default: 3)

### **Analysis Depth**
- `--deep` - Extended log analysis with more context
- `--pattern-only` - Focus on pattern recognition only
- `--full-logs` - Include complete log excerpts in report
- `--confidence-threshold N` - Only report findings above N confidence (default: 0.6)

### **Output Control**  
- `--format FORMAT` - Output format (markdown|json|text) (default: markdown)
- `--save PATH` - Save investigation report to file
- `--github-issues` - Format suitable for GitHub issue creation

## Example Workflows

### **Standard Investigation**
```bash
/gha:jobs-failed-investigate
```
*Analyze latest 5 failures with detailed thinking*

### **Deep Dive on Specific Workflow**
```bash
/gha:jobs-failed-investigate --workflow CI --deep --runs 3
```
*Comprehensive analysis of CI workflow failures*

### **Branch-Specific Investigation**
```bash
/gha:jobs-failed-investigate --branch main --days 1
```
*Focus on recent main branch failures*

## Success Criteria

### **Analysis Quality**
- ✅ Accurate pattern recognition with confidence scores
- ✅ Root cause analysis for each failure type
- ✅ Context-aware reasoning about why failures occurred
- ✅ Clear distinction between symptoms vs actual problems

### **Thinking Depth** 
- ✅ Goes beyond surface-level error messages
- ✅ Considers environmental factors and dependencies
- ✅ Identifies relationships between multiple failures
- ✅ Provides reasoning for each conclusion drawn

### **Actionable Insights**
- ✅ Specific recommendations for each failure
- ✅ Prioritization of fixes by impact and difficulty
- ✅ Clear next steps for investigation or resolution
- ✅ Honest assessment of analysis confidence

## Investigation Report Format

### **Executive Summary**
```markdown
# GitHub Actions Investigation Report

## 🎯 Key Findings
- **3 failures analyzed** across 2 workflows (CI, Deploy)
- **Root cause identified**: Missing npm package dependency
- **Impact assessment**: Blocking all feature branch merges
- **Fix complexity**: Low - single dependency addition required
- **Confidence**: 0.85 - High confidence in diagnosis

## ⚡ Immediate Actions Needed
1. Add missing 'uuid' package to package.json
2. Update CI workflow to handle dependency installation failures gracefully
3. Consider adding dependency validation step to prevent recurrence
```

### **Detailed Analysis**
```markdown
## 🔍 Failure Analysis

### 1. CI Workflow Failure (Run #16679735137)
**Branch**: feat/user-auth  
**Failure Time**: 2 hours ago  
**Confidence**: 0.90

#### 🧠 Thinking Process:
The failure occurs during the "Install dependencies" step with error:
```
npm ERR! code ENOENT
npm ERR! syscall open  
npm ERR! path /home/runner/work/project/project/package.json
```

**Analysis**: This suggests the workflow is running in wrong directory or package.json is missing. However, looking at the full log, I can see the checkout action succeeded. The real issue appears to be that the workflow runs `npm ci` but the package.json was recently moved to a subdirectory.

**Root Cause**: Recent refactoring moved package.json to `/frontend/package.json` but workflow still expects it in root directory.

#### 🎯 Recommended Fix:
Update workflow to use correct working directory:
```yaml
- name: Install dependencies
  working-directory: ./frontend
  run: npm ci
```

#### 🔗 Related Failures:
This same pattern appears in Deploy workflow failure, confirming the diagnosis.
```

### **Pattern Recognition Results**
```markdown
## 📊 Failure Patterns Identified

### Pattern: Missing Package.json (Confidence: 0.90)
- **Occurrences**: 3 out of 3 failures
- **Workflows Affected**: CI, Deploy
- **Error Signature**: `npm ERR! code ENOENT.*package.json`
- **Context**: Recent repository restructuring

### Pattern: Working Directory Mismatch (Confidence: 0.85)  
- **Root Cause**: Workflows not updated after code reorganization
- **Impact**: All npm-based steps failing
- **Fix Complexity**: Low - workflow configuration update needed
```

## Advanced Analysis Features

### **Failure Correlation Analysis**
- Identifies when multiple failures stem from same root cause
- Detects cascading failures vs independent issues
- Analyzes timing patterns and deployment correlations

### **Environmental Context**
- Considers recent commits and code changes
- Analyzes branch-specific vs universal failures  
- Examines dependency changes and version conflicts

### **Historical Pattern Matching**
- Compares against known failure patterns database
- Learns from previous successful fixes
- Identifies recurring issues and their solutions

## Integration Points

- **Builds on**: `/gha:jobs-status` for failure identification
- **Connects to**: `/gha:jobs-fixfailed-ngu` for automated fixing
- **GitHub Integration**: Direct links to runs and commits
- **Knowledge Base**: Maintains failure pattern database

## Performance Considerations

- **Execution Time**: 30-60 seconds depending on failure complexity
- **API Calls**: Moderate usage - downloads logs for analysis
- **Intelligence**: Uses pattern matching + contextual reasoning
- **Rate Limiting**: Respects GitHub API limits with backoff

This command transforms quick failure status into **deep understanding** - providing the analytical thinking needed to efficiently resolve complex workflow issues.