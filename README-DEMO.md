# Asciicinema Demo Setup

## 🎬 Quick Start

### Record the Demo
```bash
# Make sure asciicinema is installed
brew install asciinema

# Record the automated demo
./create-demo.sh --record
```

This creates `github-actions-demo.cast` file.

### Playback Options

#### 1. Terminal Playback
```bash
# Play in terminal
asciinema play github-actions-demo.cast

# Play at different speed
asciinema play github-actions-demo.cast -s 2  # 2x speed
```

#### 2. Web Embedding
```bash
# Upload to asciinema.org for web embedding
asciinema upload github-actions-demo.cast
# Returns a URL like: https://asciinema.org/a/123456
```

#### 3. Convert to GIF
```bash
# Install agg (asciicinema gif generator)
# Method 1: Via Homebrew (easiest on macOS)
brew install agg

# Method 2: Via Cargo (if you have Rust installed)
cargo install --git https://github.com/asciinema/agg

# Create GIF from asciinema.org URL (recommended)
agg https://asciinema.org/a/4BeejbTjViMzbBtz9LWkZgZNf demo.gif

# Or create GIF from local .cast file
agg github-actions-demo.cast demo.gif

# Custom GIF settings for optimization
agg --cols 120 --rows 30 --speed 1.5 https://asciinema.org/a/4BeejbTjViMzbBtz9LWkZgZNf demo.gif
```

#### 4. Convert to SVG
```bash
# Generate SVG (vector format, very small file size)
svg-term --cast github-actions-demo.cast --out demo.svg
```

## 🎯 Demo Features

The automated demo showcases:

### 🔍 **Intelligent Analysis**
- Multi-phase workflow discovery
- Historical failure pattern analysis  
- 15+ error pattern recognition with confidence scoring
- Real-time progress indicators

### 🔧 **Automated Fixing**
- Root cause identification
- Targeted fix application
- Interactive progress bars
- Before/after verification

### 📊 **Results**
- 0% → 95% success rate improvement
- Test infrastructure creation
- Security hardening with SHA-pinned actions
- Requirements.txt updates

## 📁 Integration with README

### Option 1: Embedded Player (Recommended)
```markdown
## 🎬 Live Demo

[![asciicast](https://asciinema.org/a/123456.svg)](https://asciinema.org/a/123456)

*Click to watch the intelligent failure analysis in action*
```

### Option 2: GIF
```markdown
## 🎬 Demo: Automated Workflow Fixing

![GitHub Actions Improver Demo](demo.gif)

*Automated demo showing 0% → 95% success rate improvement*
```

### Option 3: SVG (Lightweight)
```markdown
## 🎬 Interactive Demo

![Demo](demo.svg)
```

## 🛠️ Customization

### Modify the Demo Script

Edit `create-demo.sh` to:
- Change typing speed: Modify `type_text` delay parameter
- Adjust pauses: Change `PAUSE_SHORT` and `PAUSE_LONG` values
- Customize output: Edit the simulated command outputs
- Add new sections: Extend the `main_demo()` function

### Demo Timing
- **Total Duration**: ~3-4 minutes
- **Analysis Phase**: 90 seconds
- **Fixing Phase**: 90 seconds  
- **Verification**: 60 seconds

### Colors and Styling
The script uses ANSI color codes:
- `RED`: Error states and failures
- `GREEN`: Success states and completions
- `YELLOW`: Warnings and important info
- `BLUE`: Section headers and phases
- `CYAN`: Commands and metrics
- `PURPLE`: Branding and highlights

## 📊 File Sizes (Approximate)

| Format | Size | Use Case |
|--------|------|----------|
| `.cast` | 15KB | Source recording |
| `.gif` | 2-5MB | GitHub README embedding |
| `.svg` | 100KB | Lightweight web embedding |
| Web player | 0KB | Hosted on asciinema.org |

## 🎯 Best Practices

### For GitHub README
1. **Use asciinema web player** - Best user experience
2. **Fallback to GIF** - If embedding restrictions exist
3. **Optimize GIF size** - Keep under 10MB for GitHub
4. **Add descriptive caption** - Explain what viewers will see

### For Documentation Sites
1. **SVG format** - Lightweight and scalable
2. **Direct `.cast` embedding** - If your site supports it
3. **Multiple formats** - Provide options for different browsers