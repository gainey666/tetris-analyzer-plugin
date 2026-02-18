# Auto-Clicker Tool

A powerful screen capture, OCR, and automated clicking tool that integrates with your main applications via REST API.

## 🎯 Features

- **Screen Area Selection**: User-defined region capture (like sniping tool)
- **OCR Text Recognition**: Detect Yes/No buttons and other text patterns
- **Auto-Click Automation**: Click when text changes or matches patterns
- **REST API Integration**: Control from your main Tetris overlay app
- **Real-time Monitoring**: Web interface for status and configuration
- **Webhook Support**: Real-time event notifications

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd auto-clicker-tool

# Install dependencies
npm install

# Start the application
npm start
```

### Usage

1. **Open Web Interface**: Navigate to `http://localhost:3001`
2. **Select Screen Area**: Use the area selector to define the region to monitor
3. **Configure OCR**: Set target patterns (e.g., "yes|no") and confidence thresholds
4. **Start Auto-Clicker**: Click "Start" to begin monitoring and clicking
5. **Monitor Activity**: Watch real-time status and activity logs

## 🌐 API Documentation

### Start Auto-Clicker
```http
POST /api/auto-clicker/start
Content-Type: application/json

{
  "area": {
    "x": 100,
    "y": 200,
    "width": 300,
    "height": 100
  },
  "targetPattern": "yes|no",
  "confidence": 0.9,
  "clickAction": "left",
  "refreshRate": 500,
  "name": "MyAutoClicker"
}
```

### Get Status
```http
GET /api/auto-clicker/status/:sessionId
```

### Stop Auto-Clicker
```http
POST /api/auto-clicker/stop/:sessionId
```

## 🔧 Configuration

### OCR Settings
- **Target Pattern**: Regex pattern for text detection (default: "yes|no")
- **Confidence Threshold**: Minimum confidence for text recognition (0.5-1.0)
- **Refresh Rate**: How often to check the screen area (100-2000ms)

### Click Settings
- **Click Action**: left, right, or double click
- **Delay**: Wait time between clicks
- **Hold Duration**: How long to hold the mouse button

## 🎮 Integration with Main App

### Tetris Overlay Integration
```javascript
// Start monitoring yes/no buttons
const response = await fetch('http://localhost:3001/api/auto-clicker/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    area: { x: 400, y: 300, width: 200, height: 100 },
    targetPattern: 'yes|no',
    confidence: 0.9,
    clickAction: 'left'
  })
});

const result = await response.json();
console.log('Auto-clicker started:', result.sessionId);
```

### Webhook Events
```javascript
// Listen for click events
app.post('/webhook/autoclicker', (req, res) => {
  const { event, data } = req.body;
  
  if (event === 'click_detected') {
    console.log(`Auto-clicker detected: ${data.text} at ${data.timestamp}`);
    // Update your Tetris overlay state
  }
});
```

## 📁 Project Structure

```
auto-clicker-tool/
├── src/
│   ├── index.js              # Main entry point
│   ├── auto-clicker.js      # Core engine
│   ├── api-server.js        # REST API server
│   ├── screen-capture.js    # Screen capture module
│   ├── ocr-engine.js        # OCR processing
│   └── click-controller.js  # Mouse automation
├── ui/
│   └── index.html           # Web interface
├── config/                  # Configuration files
├── tests/                   # Test files
├── docs/                    # Documentation
└── package.json
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

## 📊 Monitoring

### Web Interface Features
- **Real-time Status**: See current session status and statistics
- **Activity Log**: Monitor all clicks and detections
- **Configuration Panel**: Adjust settings on the fly
- **Statistics Dashboard**: Track success rates and performance

### API Monitoring
- **Health Check**: `GET /health`
- **Session Status**: `GET /api/auto-clicker/status`
- **Performance Metrics**: Response times and success rates

## 🔒 Security Considerations

- **Local Only**: Runs on localhost by default
- **Session Isolation**: Each session has unique ID
- **Input Validation**: All API inputs are validated
- **Error Handling**: Graceful error recovery

## 🐛 Troubleshooting

### Common Issues

1. **Screen Capture Fails**
   - Ensure the application has screen recording permissions
   - Check if the area coordinates are within screen bounds

2. **OCR Not Working**
   - Verify the target pattern matches the actual text
   - Adjust confidence threshold if text is not being recognized

3. **Clicks Not Working**
   - Check if the application has accessibility permissions
   - Verify the click coordinates are correct

### Debug Mode
```bash
# Start with debug logging
DEBUG=* npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: See `/docs` folder for detailed guides
- **API Reference**: Full API documentation at `/api` endpoint

---

**Built with ❤️ for automation enthusiasts!**
