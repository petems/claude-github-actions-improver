# /gha:jobs-status - Quick GitHub Actions Status Check

## Workflow: Fetch → Display → Summary

**Target:** Get latest 5 failed runs from GitHub Actions in current repository

**Scope:** Quick status check for recent failures, perfect after pushing a big block of work

## 🎯 Interactive Mode Instructions
**IMPORTANT**: Provide immediate, concise feedback in a clean format:

1. **Quick execution**: "🔍 Checking latest GitHub Actions runs..."
2. **Display results**: Show failures in a clean, scannable format
3. **Summary**: Provide count and basic pattern overview
4. **No fixes**: This is purely informational - just show what's failing

**Format**: Use emojis and clean tables for easy scanning.

## Execution Steps

### 1. **Fetch Recent Runs**
   - Get latest workflow runs: `gh run list --limit 10 --json "databaseId,name,status,conclusion,createdAt,headBranch,event"`
   - Filter for failed/cancelled runs only
   - Take the 5 most recent failures

### 2. **Display Status Information**
   - Show run ID, workflow name, branch, failure time
   - Display in a clean table format
   - Include direct links to the failed runs for easy access

### 3. **Basic Pattern Recognition**
   - Count failures by workflow name
   - Identify if failures are on specific branches
   - Note any obvious patterns (all failing on same commit, etc.)

## Command Parameters

### **Scope Control**
- `--limit N` - Show N most recent failures (default: 5)
- `--branch NAME` - Filter to specific branch only
- `--workflow NAME` - Filter to specific workflow only
- `--all` - Show all statuses (passed, failed, cancelled)

### **Output Control**
- `--format FORMAT` - Output format (table|json|simple) (default: table)
- `--links` - Include direct GitHub links to runs
- `--time-window HOURS` - Only show failures from last N hours

## Example Usage

### **Quick Status Check**
```bash
/gha:jobs-status
```
*Shows latest 5 failures in clean table format*

### **Specific Branch Check**
```bash
/gha:jobs-status --branch main --limit 3
```
*Check last 3 failures on main branch*

### **All Recent Activity**
```bash
/gha:jobs-status --all --limit 10
```
*Show all recent run statuses*

## Success Criteria

### **Speed & Clarity**
- ✅ Fast execution (< 10 seconds)
- ✅ Clean, scannable output format
- ✅ Essential information only (no verbose analysis)
- ✅ Direct links to failed runs for investigation

### **Information Quality**
- ✅ Accurate failure identification
- ✅ Proper sorting by recency
- ✅ Branch and timing context
- ✅ Basic pattern recognition

## Output Format

### **Table Format (Default)**
```
🔍 Latest GitHub Actions Failures

┌─────────────┬──────────────┬────────────┬─────────────────────┬────────────┐
│ Run ID      │ Workflow     │ Branch     │ Failed              │ Event      │
├─────────────┼──────────────┼────────────┼─────────────────────┼────────────┤
│ 16679735137 │ CI           │ main       │ 2 hours ago         │ push       │
│ 16679735136 │ Security     │ feat/new   │ 3 hours ago         │ pull_req   │
│ 16679735135 │ CI           │ main       │ 5 hours ago         │ push       │
│ 16679735134 │ Deploy       │ main       │ 1 day ago           │ push       │
│ 16679735133 │ CI           │ feat/test  │ 2 days ago          │ pull_req   │
└─────────────┴──────────────┴────────────┴─────────────────────┴────────────┘

📊 Summary:
• 5 failures found
• Most failing workflow: CI (3 failures)
• Most failures on: main branch (3 failures)
• 🔗 View details: gh run list --limit 5 --status failure
```

### **Simple Format**
```
❌ CI (main) - 2 hours ago - Run #16679735137
❌ Security (feat/new) - 3 hours ago - Run #16679735136  
❌ CI (main) - 5 hours ago - Run #16679735135
❌ Deploy (main) - 1 day ago - Run #16679735134
❌ CI (feat/test) - 2 days ago - Run #16679735133

💡 Use /gha:jobs-failed-investigate to analyze these failures
```

## Common Use Cases

### **After Big Push**
Quick check to see if your recent changes broke anything:
```bash
/gha:jobs-status --branch main --time-window 2
```

### **PR Status Check**
See if your feature branch has any issues:
```bash
/gha:jobs-status --branch feat/my-feature
```

### **Daily Standup Prep**
Get overview of recent failures for team discussion:
```bash
/gha:jobs-status --limit 10
```

## Integration Points

- **GitHub CLI**: Required for accessing workflow run data
- **Next Steps**: Use `/gha:jobs-failed-investigate` to analyze specific failures
- **Quick Links**: Provides `gh run view <id>` commands for detailed investigation

## Performance

- **Target Speed**: < 10 seconds execution
- **Rate Limiting**: Single API call to GitHub
- **Caching**: No caching - always fresh data
- **Offline**: Graceful failure if GitHub unavailable

This command is designed for **speed and clarity** - perfect for quick status checks without deep analysis. Use it to rapidly assess the health of your GitHub Actions after pushing changes or during daily development workflow.