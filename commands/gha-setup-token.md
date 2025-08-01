# /gha:setup-token - GitHub Token Generator & Configuration

## Workflow: Detect → Guide → Generate → Configure → Test

**Target:** Interactive GitHub token setup for enhanced API access

**Scope:** Create and configure GitHub tokens for higher rate limits and better concurrent processing

## 🎯 Interactive Mode Instructions
**IMPORTANT**: This command provides step-by-step token creation and setup:

1. **Token Type Selection** (30-60 seconds):
   - "🔍 Analyzing your needs..."
   - "📊 Comparing token options..."
   - "💡 Recommended: GitHub CLI for individual use"
   - "✅ Choice confirmed: Personal Access Token"

2. **Token Generation** (2-5 minutes):
   - "🌐 Opening GitHub token creation page..."
   - "📋 Configuring required scopes (repo, workflow, actions:read)..."
   - "🔑 Validating token with GitHub API..."
   - "✅ Token validated successfully!"

3. **Configuration Setup** (1-2 minutes):
   - "💾 Saving token to environment variables..."
   - "📝 Adding to shell configuration..."
   - "🔒 Setting up secure storage..."

4. **Integration Testing** (30 seconds):
   - "🧪 Testing with GitHub Actions Improver..."
   - "📊 Rate limit check: 4,847/5,000 requests available"
   - "🚀 Optimal worker count: 20 concurrent jobs"

**Format**: Interactive prompts, browser automation where possible, secure token handling

## Execution Steps

### 1. **Token Requirements Analysis**
   - Assess user's usage pattern (personal/team/enterprise)
   - Determine optimal token type based on needs
   - Calculate expected API usage and rate limits
   - Recommend authentication method

### 2. **Guided Token Creation**
   - **GitHub CLI Setup**: `gh auth login` with interactive flow
   - **Personal Token**: Step-by-step browser automation
   - **Fine-grained Token**: Advanced permission configuration
   - **GitHub App**: Organization-level setup guidance

### 3. **Secure Configuration**
   - Environment variable setup (`GITHUB_TOKEN`)
   - Shell configuration file integration
   - Project-specific `.env` file creation
   - `.gitignore` protection for security

### 4. **Validation & Testing**
   - API connectivity test with GitHub
   - Rate limit verification and reporting
   - Integration test with Actions Improver
   - Performance benchmark with sample jobs

### 5. **Usage Instructions**
   - Command examples with new token
   - Rate limit optimization tips
   - Troubleshooting common issues
   - Security best practices

## Command Parameters

### **Setup Options**
- `--type TYPE` - Token type (cli|personal|fine-grained|app)
- `--quick` - Quick setup with recommended options
- `--advanced` - Advanced configuration options
- `--validate-existing` - Validate current token setup

### **Configuration Options**
- `--save-to ENV` - Where to save token (env|shell|project|display)
- `--scope SCOPES` - Custom permission scopes
- `--expiry DAYS` - Token expiration (30|90|never)

### **Testing Options**
- `--test-only` - Only test existing configuration
- `--benchmark` - Run performance benchmark
- `--show-limits` - Display current rate limits

## Example Setup Sessions

### **Quick Setup (Recommended)**
```bash
/gha:setup-token --quick
```
*GitHub CLI setup with automatic configuration*

### **Personal Token Creation**
```bash
/gha:setup-token --type personal --save-to shell
```
*Manual token creation with shell integration*

### **Organization Setup**
```bash
/gha:setup-token --type app --advanced
```
*GitHub App setup for team/enterprise use*

### **Validation Only**
```bash
/gha:setup-token --validate-existing --show-limits
```
*Check current token status and limits*

## Token Type Comparison

### **🟢 GitHub CLI (Easiest)**
- **Setup Time**: 2 minutes
- **Rate Limit**: 5,000/hour
- **Best For**: Individual developers
- **Maintenance**: Automatic
- **Command**: `gh auth login`

### **🟡 Personal Access Token**
- **Setup Time**: 5 minutes
- **Rate Limit**: 5,000/hour
- **Best For**: Teams, shared systems
- **Maintenance**: Manual renewal
- **Scopes**: `repo`, `workflow`, `actions:read`

### **🟠 Fine-grained Token**
- **Setup Time**: 10 minutes
- **Rate Limit**: 5,000/hour
- **Best For**: Specific repositories
- **Maintenance**: Manual renewal
- **Scopes**: Granular permissions

### **🔴 GitHub App**
- **Setup Time**: 20 minutes
- **Rate Limit**: 15,000+/hour
- **Best For**: Organizations, CI/CD
- **Maintenance**: Automated
- **Scopes**: Installation-based

## Success Criteria

### **Token Generation**
- ✅ Valid token created with correct scopes
- ✅ Token validated against GitHub API
- ✅ Rate limits verified and reported
- ✅ Secure storage configured

### **Integration Success**
- ✅ Token automatically detected by system
- ✅ Rate limits show 5,000+ requests/hour
- ✅ Concurrent worker count increased to 20+
- ✅ Sample API calls succeed

### **User Experience**
- ✅ Clear step-by-step guidance provided
- ✅ Browser automation where possible
- ✅ Security warnings and best practices shown
- ✅ Troubleshooting help available

## Rate Limit Benefits

**Before Token Setup:**
```
❌ Unauthenticated: 60 requests/hour
❌ Max workers: 2
❌ Job capacity: ~5 jobs
❌ Processing time: 30-60 seconds
```

**After Token Setup:**
```
✅ Authenticated: 5,000+ requests/hour  
✅ Max workers: 20+
✅ Job capacity: 50+ jobs
✅ Processing time: 3-5 seconds
```

## Integration Points

- **Claude CLI Settings**: Automatic token detection
- **Environment Variables**: `GITHUB_TOKEN` configuration
- **Shell Integration**: `.bashrc`/`.zshrc` setup
- **GitHub Actions Improver**: Direct integration testing
- **API Limit Handler**: Real-time rate monitoring

This command transforms basic GitHub Actions analysis into enterprise-grade concurrent processing with proper authentication and optimal rate limits.