# /gha:analyze - Comprehensive GitHub Actions Intelligence Report

## Workflow: Discover → Assess → Benchmark → Recommend → Report

**Target:** $ARGUMENTS (Default: complete repository analysis with 30-day failure history)

**Scope:** Generate comprehensive intelligence report on GitHub Actions performance, patterns, and optimization opportunities

## 🎯 Interactive Mode Instructions
**IMPORTANT**: This is a longer analysis (2-5 minutes). Provide continuous updates:

1. **Discovery Phase** (30-90 seconds):
   - "🔍 Discovering workflows and dependencies..."
   - "📊 Found 4 workflows, 23 jobs, 156 steps total"
   - "🔍 Mapping integrations: CodeQL, Trivy, Codecov..."
   - "⏱️ Fetching 30-day performance history..."

2. **Performance Assessment** (60-120 seconds):
   - "📈 Analyzing 47 workflow runs..."
   - "⏱️ Average execution time: 8.5 minutes (↓0.8 min vs baseline)"
   - "💰 Estimated monthly cost: $203.25"
   - "🔍 Identifying bottlenecks in 'security-scan' job..."

3. **Security & Compliance Audit** (45-90 seconds):
   - "🛡️ Auditing 12 external actions..."
   - "⚠️ Found 3 actions using non-SHA references"
   - "✅ All workflows have minimal permissions"
   - "🔍 Checking for secret exposure risks..."

4. **Recommendations & Reporting** (30-60 seconds):
   - "📋 Generating optimization recommendations..."
   - "💡 Identified 6 improvement opportunities"
   - "📊 Calculating potential ROI: 35% performance gain"
   - "📄 Compiling final intelligence report..."

**Format**: Include time estimates, progress percentages, and intermediate findings throughout.

## Execution Steps

### 1. **Repository Discovery & Mapping**
   - **Workflow Inventory**: Catalog all existing workflows, jobs, and steps
   - **Dependency Mapping**: Identify action dependencies and version patterns
   - **Trigger Analysis**: Document workflow triggers, schedules, and conditions
   - **Resource Usage**: Analyze runner types, execution times, and resource consumption
   - **Integration Points**: Identify external services, secrets, and environment dependencies

### 2. **Historical Performance Assessment**
   - **Success/Failure Rates**: Calculate reliability metrics over specified timeframe
   - **Execution Time Analysis**: Identify bottlenecks, slow steps, and optimization opportunities
   - **Failure Pattern Recognition**: Categorize and quantify different types of failures
   - **Resource Utilization**: Track runner usage, billing implications, and efficiency metrics
   - **Trend Analysis**: Identify performance trends, degradation patterns, and improvements

### 3. **Security & Compliance Benchmarking**
   - **Action Version Audit**: Identify outdated actions and security vulnerabilities
   - **Permission Analysis**: Review workflow permissions and access scopes
   - **Secret Usage Review**: Audit secret handling and exposure risks
   - **Supply Chain Security**: Analyze third-party dependencies and trust chains
   - **Compliance Validation**: Check against security best practices and standards

### 4. **Optimization Opportunity Identification**
   - **Performance Bottlenecks**: Identify slow jobs, inefficient steps, and parallelization opportunities
   - **Caching Optimization**: Analyze cache hit rates and improvement potential
   - **Resource Right-sizing**: Recommend optimal runner types and configurations
   - **Workflow Consolidation**: Identify duplicate patterns and merge opportunities
   - **Cost Optimization**: Calculate potential savings from efficiency improvements

### 5. **Strategic Recommendations & Reporting**
   - **Priority Matrix**: Rank improvements by impact and implementation difficulty
   - **Implementation Roadmap**: Provide step-by-step improvement plan
   - **Risk Assessment**: Identify potential risks and mitigation strategies
   - **ROI Calculations**: Quantify benefits of recommended improvements
   - **Executive Summary**: High-level insights for decision makers

## Command Parameters

### **Scope Control**
- `--timeframe DAYS` - Analysis period in days (default: 30)
- `--workflows PATTERN` - Focus on specific workflows (glob pattern)
- `--jobs PATTERN` - Analyze specific jobs only
- `--include-success` - Include successful runs in analysis (default: failures only)

### **Analysis Depth**
- `--detailed` - Include comprehensive technical analysis
- `--summary` - High-level overview only
- `--security-focus` - Emphasize security and compliance analysis
- `--performance-focus` - Emphasize performance and optimization analysis
- `--cost-focus` - Emphasize cost analysis and optimization

### **Historical Data**
- `--baseline DATE` - Compare against baseline date (YYYY-MM-DD)
- `--trend-analysis` - Include trend analysis over time
- `--seasonal-patterns` - Identify seasonal usage patterns
- `--regression-detection` - Detect performance regressions

### **Output Customization**
- `--format FORMAT` - Output format (markdown|json|html|pdf)
- `--template TEMPLATE` - Use custom report template
- `--charts` - Include visual charts and graphs
- `--export PATH` - Export raw data for external analysis

### **Benchmarking**
- `--industry-comparison` - Compare against industry benchmarks
- `--best-practices` - Include best practice recommendations
- `--maturity-assessment` - Assess CI/CD maturity level
- `--gap-analysis` - Identify gaps in current implementation

## Example Analysis Sessions

### **Comprehensive Health Check**
```bash
/gha:analyze --timeframe 60 --detailed --charts --format html
```
*Full 60-day analysis with detailed insights and visual charts*

### **Security Audit**
```bash
/gha:analyze --security-focus --best-practices --format pdf
```
*Security-focused analysis with compliance recommendations*

### **Performance Optimization**
```bash
/gha:analyze --performance-focus --trend-analysis --baseline 2024-01-01
```
*Performance analysis with trend tracking and baseline comparison*

### **Cost Analysis**
```bash
/gha:analyze --cost-focus --seasonal-patterns --industry-comparison
```
*Cost optimization analysis with usage patterns and benchmarking*

## Analysis Dimensions

### **Reliability Metrics**
```
Success Rate: 87.3% (↑2.1% vs last month)
MTTR (Mean Time To Recovery): 1.2 hours
MTBF (Mean Time Between Failures): 15.4 hours
Availability: 99.2%
```

### **Performance Metrics**
```
Average Execution Time: 8.5 minutes (↓0.8 min vs baseline)
P95 Execution Time: 23.1 minutes
Fastest Workflow: unit-tests (2.1 min)
Slowest Workflow: integration-tests (45.6 min)
```

### **Resource Utilization**
```
Total Runner Hours: 847.2 hours
Cost per Hour: $0.008
Monthly Cost Estimate: $203.25
Runner Efficiency: 73.4%
```

### **Security Posture**
```
Outdated Actions: 12 (Medium Risk)
Missing SHA Pins: 8 (High Risk)
Excessive Permissions: 3 workflows (Medium Risk)
Secret Exposure Risk: Low
```

## Intelligence Categories

### **🎯 Performance Intelligence**
- **Execution Time Patterns**: Identify peak usage times and resource contention
- **Bottleneck Analysis**: Pinpoint slowest steps and optimization opportunities
- **Caching Effectiveness**: Measure cache hit rates and improvement potential
- **Parallelization Opportunities**: Identify jobs that could run concurrently
- **Resource Right-sizing**: Recommend optimal runner configurations

### **🔍 Failure Intelligence**
- **Failure Taxonomy**: Categorize failures by type (infrastructure, code, configuration)
- **Pattern Recognition**: Identify recurring failure patterns and root causes
- **Impact Analysis**: Quantify business impact of different failure types
- **Recovery Patterns**: Analyze how quickly different failures are resolved
- **Prevention Opportunities**: Suggest proactive measures to prevent failures

### **🛡️ Security Intelligence**
- **Vulnerability Assessment**: Identify security risks in workflows and dependencies
- **Compliance Mapping**: Map workflows against security frameworks and standards
- **Supply Chain Analysis**: Assess third-party action and dependency risks
- **Permission Optimization**: Recommend minimal required permissions
- **Secret Management**: Audit secret usage and recommend improvements

### **💰 Cost Intelligence**
- **Usage Patterns**: Understand when and how runners are being used
- **Cost Attribution**: Break down costs by team, project, or workflow
- **Optimization Opportunities**: Identify potential cost savings
- **Efficiency Metrics**: Measure cost per deployment, test, or build
- **Budget Forecasting**: Project future costs based on current trends

## Report Structure

### **Executive Summary**
```markdown
# GitHub Actions Intelligence Report

## Key Findings
- **Overall Health**: Good (78/100)
- **Primary Risk**: Outdated dependencies (12 high-risk actions)
- **Top Opportunity**: Caching optimization (potential 35% speed improvement)
- **Cost Impact**: $203/month current, $145/month optimized

## Immediate Actions Required
1. Update GitHub Actions to latest versions (Security Risk)
2. Implement intelligent caching strategy (Performance)
3. Consolidate duplicate workflow patterns (Maintainability)
```

### **Technical Deep Dive**
- Detailed workflow analysis with specific recommendations
- Performance metrics and benchmarking data
- Security findings with remediation steps
- Cost analysis with optimization recommendations

### **Implementation Roadmap**
- Prioritized list of improvements
- Estimated effort and impact for each item
- Risk assessment and mitigation strategies
- Success metrics and monitoring recommendations

## Success Criteria

### **Analysis Completeness**
- ✅ All workflows analyzed and categorized
- ✅ Historical data processed and trends identified
- ✅ Security posture thoroughly assessed
- ✅ Performance bottlenecks clearly identified

### **Insight Quality**
- ✅ Actionable recommendations with clear ROI
- ✅ Risk-prioritized improvement roadmap
- ✅ Quantified impact of proposed changes
- ✅ Implementation guidance provided

### **Report Usability**
- ✅ Executive summary for decision makers
- ✅ Technical details for implementation teams
- ✅ Visual representations of key metrics
- ✅ Exportable data for further analysis

## Integration Points

- **GitHub API**: Comprehensive workflow run data
- **Billing APIs**: Cost and usage information
- **Security Databases**: Vulnerability and best practice data
- **Benchmarking Services**: Industry comparison data
- **Visualization Tools**: Charts, graphs, and dashboards

This command transforms ad-hoc workflow monitoring into strategic intelligence that drives informed decisions about CI/CD optimization, security improvements, and resource allocation.