# 🎮 Tetris Analyzer - User Guide & Tutorials

## 📚 Table of Contents
1. [Getting Started](#getting-started)
2. [Installation Guide](#installation-guide)
3. [First Time Setup](#first-time-setup)
4. [Basic Usage](#basic-usage)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)
7. [Tips & Tricks](#tips--tricks)
8. [FAQ](#faq)

---

## 🚀 Getting Started

### What is Tetris Analyzer?
Tetris Analyzer is a real-time Tetris game analysis system that provides:
- **Move Predictions**: AI-powered suggestions for optimal piece placement
- **Coaching Hints**: Real-time strategy tips and danger warnings
- **Performance Monitoring**: FPS, latency, and resource usage tracking

### System Requirements
- **Python 3.8+** (required)
- **Windows, macOS, or Linux** (cross-platform)
- **A Tetris game** running on your screen
- **Minimum 4GB RAM** (8GB recommended)
- **Multi-core CPU** (for best performance)

---

## 📦 Installation Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/gainey666/tetris-analyzer-plugin.git
cd tetris-analyzer-plugin
```

### Step 2: Install Dependencies
```bash
# Using pip (recommended)
pip install -r requirements.txt

# Or using conda
conda env create -f environment.yml
conda activate tetris-analyzer
```

### Step 3: Verify Installation
```bash
python cli/main.py --help
```

You should see the help message with all available options.

---

## ⚙️ First Time Setup

### 1. System Check
Run a system check to ensure everything is ready:
```bash
python cli/main.py check
```

This will check:
- Python version and dependencies
- Screen capture capabilities
- System performance
- Available monitors

### 2. Calibration
Calibrate the system to detect your Tetris board:
```bash
python cli/main.py --calibrate
```

**Calibration Steps:**
1. Open your Tetris game
2. Make sure the game window is visible
3. Click on the game window to focus it
4. Wait for the analyzer to detect the board
5. Save the calibration when prompted

### 3. Create Configuration (Optional)
Create a custom configuration file:
```bash
python cli/main.py config create
```

This creates `sample_config.json` with all available settings.

---

## 🎯 Basic Usage

### Quick Start
```bash
# Start with default settings
python cli/main.py

# Start with verbose output
python cli/main.py --verbose

# Start without coaching hints
python cli/main.py --no-coaching
```

### What You'll See
```
🎮 Tetris Analyzer Started
==========================
Board Detected: ✅
FPS: 28.5
Accuracy: 98.2%
Latency: 12.3ms

=== MOVE SUGGESTIONS ===
1. Move left (confidence: 0.85)
2. Rotate (confidence: 0.72)
3. Drop (confidence: 0.68)

=== COACHING HINTS ===
💡 Consider clearing lines soon
⚠️ Stack getting high on the right
📊 Good piece placement opportunity
```

### Understanding the Output

#### Move Suggestions
- **Move**: Recommended action (left, right, rotate, drop)
- **Confidence**: How confident the system is (0.0-1.0)
- **Score**: Expected board improvement

#### Coaching Hints
- **💡 Strategy tips**: General advice
- **⚠️ Warnings**: Dangerous situations
- **📊 Opportunities**: Good placement chances

#### Performance Metrics
- **FPS**: Frames per second capture rate
- **Accuracy**: Piece recognition success rate
- **Latency**: Processing time per frame

---

## 🔧 Advanced Features

### Custom Configuration
Create and edit a configuration file:
```json
{
  "capture": {
    "fps": 30,
    "quality": "high",
    "monitor": 0
  },
  "detection": {
    "method": "edges",
    "threshold": 0.8
  },
  "prediction": {
    "max_suggestions": 5,
    "confidence_threshold": 0.6
  },
  "coaching": {
    "enabled": true,
    "max_hints": 5
  }
}
```

Use your configuration:
```bash
python cli/main.py --config my_config.json
```

### Performance Tuning
Run a benchmark to test performance:
```bash
python cli/main.py benchmark --duration 30
```

### Runtime Hub Integration
Start with Runtime Hub support:
```bash
python cli/main.py --runtime-hub
```

### Demo Mode
See all features in action:
```bash
python cli/main.py --demo
```

---

## 🛠️ Troubleshooting

### Common Issues

#### "Board Not Detected"
**Problem**: Analyzer can't find your Tetris board

**Solutions**:
1. Make sure the game window is visible
2. Try different detection methods in config
3. Re-run calibration: `python cli/main.py --calibrate`
4. Check if game is in fullscreen (try windowed mode)

#### "Low Performance"
**Problem**: High CPU usage or lag

**Solutions**:
1. Reduce capture FPS in config
2. Lower image quality
3. Close other applications
4. Try a different detection method

#### "Import Errors"
**Problem**: Module not found errors

**Solutions**:
1. Reinstall dependencies: `pip install -r requirements.txt`
2. Check Python version (3.8+)
3. Ensure you're in the project directory

#### "Piece Recognition Errors"
**Problem**: Wrong piece types detected

**Solutions**:
1. Recalibrate the system
2. Adjust recognition thresholds
3. Check game graphics settings
4. Ensure good lighting/contrast

### Debug Mode
Enable verbose output for detailed debugging:
```bash
python cli/main.py --verbose
```

This shows:
- Frame capture status
- Board detection results
- Piece recognition details
- Performance metrics

---

## 💡 Tips & Tricks

### Optimize Performance
- **Use windowed mode** instead of fullscreen
- **Set capture FPS to 20-30** for good balance
- **Disable unused features** (coaching/predictions)
- **Close background applications**

### Improve Accuracy
- **Calibrate regularly** for best results
- **Use consistent game settings**
- **Ensure good contrast** between pieces and background
- **Avoid moving the game window** during analysis

### Best Practices
- **Start the analyzer before** starting the game
- **Keep the game window focused**
- **Use a stable internet connection** (for Runtime Hub)
- **Save your calibration** for future sessions

### Advanced Tips
- **Experiment with detection methods** (edges, contours, template)
- **Adjust prediction weights** for your playstyle
- **Use configuration files** for different games
- **Monitor performance** regularly

---

## ❓ FAQ

### Q: Does this work with all Tetris games?
**A**: It works with most Tetris games, but may need calibration for different graphics styles.

### Q: Can I use this while playing online?
**A**: Yes, it only reads the screen and doesn't interfere with the game.

### Q: How much CPU does it use?
**A**: Typically 5-15% CPU usage, depending on settings and hardware.

### Q: Can I customize the coaching hints?
**A**: Yes, through the configuration file you can adjust hint types and thresholds.

### Q: Does this work on macOS/Linux?
**A**: Yes, it's cross-platform but may need different dependencies.

### Q: Can I use multiple monitors?
**A**: Yes, you can specify which monitor to use in the configuration.

### Q: How accurate are the predictions?
**A**: Typically 85-95% accuracy depending on game and settings.

### Q: Can I export the analysis data?
**A**: Yes, through the API or by enabling logging in configuration.

### Q: Does this require internet?
**A**: No, except for Runtime Hub integration features.

### Q: Can I contribute to the project?
**A**: Yes! Check the GitHub repository for contribution guidelines.

---

## 🎓 Tutorial Walkthroughs

### Tutorial 1: First Time Setup (5 minutes)

**Goal**: Get Tetris Analyzer running with your game

**Steps**:
1. **Install**: `pip install -r requirements.txt`
2. **Check System**: `python cli/main.py check`
3. **Open Game**: Launch your Tetris game
4. **Calibrate**: `python cli/main.py --calibrate`
5. **Start**: `python cli/main.py`

**Expected Result**: Analyzer detects your board and shows suggestions

---

### Tutorial 2: Performance Optimization (10 minutes)

**Goal**: Achieve smooth 30 FPS analysis

**Steps**:
1. **Benchmark**: `python cli/main.py benchmark --duration 30`
2. **Check Results**: Note current FPS and CPU usage
3. **Adjust Settings**: Edit config file to reduce FPS if needed
4. **Test Again**: Run benchmark with new settings
5. **Fine-tune**: Adjust detection method and quality

**Expected Result**: Stable 20-30 FPS with <15% CPU usage

---

### Tutorial 3: Advanced Configuration (15 minutes)

**Goal**: Customize analyzer for your playstyle

**Steps**:
1. **Create Config**: `python cli/main.py config create`
2. **Edit Settings**: Open `sample_config.json`
3. **Adjust Weights**: Modify prediction weights
4. **Set Preferences**: Configure coaching hints
5. **Test**: Run with `--config sample_config.json`

**Expected Result**: Analyzer tailored to your preferences

---

### Tutorial 4: Runtime Hub Integration (20 minutes)

**Goal**: Connect analyzer to Runtime Hub

**Steps**:
1. **Install Runtime Hub**: Follow Runtime Hub setup guide
2. **Start Integration**: `python cli/main.py --runtime-hub`
3. **Test Connection**: Check Runtime Hub interface
4. **Configure Nodes**: Set up Runtime Hub workflow
5. **Monitor**: Use Runtime Hub dashboard

**Expected Result**: Analyzer controlled through Runtime Hub

---

## 📊 Performance Benchmarks

### Expected Performance by Hardware

| Hardware | Capture FPS | CPU Usage | Accuracy |
|----------|-------------|-----------|----------|
| Low-end (4GB RAM, 2 cores) | 15-20 | 15-20% | 85-90% |
| Mid-range (8GB RAM, 4 cores) | 25-30 | 8-12% | 90-95% |
| High-end (16GB RAM, 8+ cores) | 30-60 | 5-8% | 95-98% |

### Optimization Targets
- **Target FPS**: 30 (minimum 20)
- **Target CPU**: <15% (maximum 20%)
- **Target Accuracy**: >90% (minimum 85%)
- **Target Latency**: <50ms (maximum 100ms)

---

## 🔗 Additional Resources

### Documentation
- [Complete API Documentation](DOCUMENTATION.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Configuration Reference](docs/CONFIGURATION.md)

### Community
- [GitHub Repository](https://github.com/gainey666/tetris-analyzer-plugin)
- [Issues and Bug Reports](https://github.com/gainey666/tetris-analyzer-plugin/issues)
- [Discussions and Q&A](https://github.com/gainey666/tetris-analyzer-plugin/discussions)

### Development
- [Contributing Guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Development Setup](docs/DEVELOPMENT.md)

---

## 🎯 Next Steps

Now that you've mastered the basics:

1. **Explore Advanced Features**: Try Runtime Hub integration
2. **Customize Configuration**: Fine-tune for your playstyle
3. **Contribute**: Help improve the project
4. **Share Feedback**: Report issues and suggestions

---

**Happy Analyzing! 🎮**

*Last Updated: 2026-02-22*  
*Version: 1.0.0*
