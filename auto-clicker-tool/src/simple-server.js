/**
 * Simple Working Auto-Clicker Server
 * No complex dependencies, just basic HTTP server
 */

const http = require('http');
const { SimpleAutoClicker } = require('./simple-auto-clicker');

class SimpleServer {
    constructor(port = 3001) {
        this.port = port;
        this.autoClicker = new SimpleAutoClicker();
        this.sessions = new Map();
    }

    start() {
        console.log('🚀 Starting Simple Auto-Clicker Server...');
        
        this.server = http.createServer((req, res) => {
            console.log(`📝 ${req.method} ${req.url}`);
            
            // Set CORS headers
            res.setHeader('Access-Control-Allow-Origin', '*');
            res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
            res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
            
            if (req.method === 'OPTIONS') {
                res.writeHead(200);
                res.end();
                return;
            }
            
            // Parse URL
            const url = new URL(req.url, `http://localhost:${this.port}`);
            const path = url.pathname;
            
            try {
                if (path === '/health') {
                    this.handleHealth(req, res);
                } else if (path === '/api/auto-clicker/start') {
                    this.handleStart(req, res);
                } else if (path === '/api/auto-clicker/stop') {
                    this.handleStop(req, res);
                } else if (path === '/api/auto-clicker/status') {
                    this.handleStatus(req, res);
                } else if (path === '/api/test-click') {
                    this.handleTestClick(req, res);
                } else if (path === '/test') {
                    this.handleTestPage(req, res);
                } else if (path === '/') {
                    this.handleMainPage(req, res);
                } else {
                    res.writeHead(404, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Not found' }));
                }
            } catch (error) {
                console.error('❌ Request error:', error);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: error.message }));
            }
        });
        
        this.server.listen(this.port, '127.0.0.1', () => {
            console.log(`🌐 Simple Server running on http://localhost:${this.port}`);
            console.log('🎉 SERVER IS READY! Press Ctrl+C to stop');
            console.log('📝 Test with: curl http://localhost:3001/health');
        });
        
        this.server.on('error', (error) => {
            console.error('❌ Server error:', error);
        });
    }
    
    handleHealth(req, res) {
        const health = {
            status: 'healthy',
            timestamp: new Date().toISOString(),
            version: '1.0.0',
            activeSessions: this.sessions.size
        };
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(health));
    }
    
    async handleStart(req, res) {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const config = JSON.parse(body);
                console.log('🎯 Starting auto-clicker with config:', config);
                
                // Start the auto-clicker
                await this.autoClicker.start(config);
                
                const response = {
                    success: true,
                    sessionId: 'simple-session-' + Date.now(),
                    message: 'Auto-clicker started'
                };
                
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(response));
                
            } catch (error) {
                console.error('❌ Start error:', error);
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, error: error.message }));
            }
        });
    }
    
    async handleStop(req, res) {
        try {
            await this.autoClicker.stop();
            
            const response = {
                success: true,
                message: 'Auto-clicker stopped'
            };
            
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify(response));
            
        } catch (error) {
            console.error('❌ Stop error:', error);
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: false, error: error.message }));
        }
    }
    
    handleStatus(req, res) {
        const status = this.autoClicker.getStatus();
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            success: true,
            sessions: [status]
        }));
    }
    
    handleTestPage(req, res) {
        const fs = require('fs');
        const path = require('path');
        
        try {
            const htmlPath = path.join(__dirname, '..', 'test_all_endpoints.html');
            const html = fs.readFileSync(htmlPath, 'utf8');
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(html);
        } catch (error) {
            res.writeHead(500, { 'Content-Type': 'text/html' });
            res.end(`
                <html>
                <body>
                    <h1>❌ Test Page Error</h1>
                    <p>Could not load test page: ${error.message}</p>
                    <p>Please ensure test_all_endpoints.html exists in the auto-clicker-tool directory</p>
                </body>
                </html>
            `);
        }
    }
    
    async handleTestClick(req, res) {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const config = JSON.parse(body);
                console.log('🖱️ Test click at:', config);
                
                // Perform a simple test click
                await this.autoClicker.testClick();
                
                const response = {
                    success: true,
                    message: 'Test click executed',
                    position: config || { x: 100, y: 100 }
                };
                
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(response));
                
            } catch (error) {
                console.error('❌ Test click error:', error);
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, error: error.message }));
            }
        });
    }
    
    handleMainPage(req, res) {
        const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto-Clicker Control Center</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        header { 
            background: rgba(255,255,255,0.1); 
            backdrop-filter: blur(10px); 
            padding: 20px; 
            border-radius: 15px; 
            margin-bottom: 30px;
            text-align: center;
        }
        h1 { font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { opacity: 0.8; font-size: 1.1em; }
        .card { 
            background: rgba(255,255,255,0.1); 
            backdrop-filter: blur(10px); 
            padding: 30px; 
            border-radius: 15px; 
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .status-item { text-align: center; padding: 20px; }
        .status-value { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .status-label { opacity: 0.8; }
        .button { 
            background: linear-gradient(45deg, #ff6b6b, #ff8e53); 
            color: white; 
            border: none; 
            padding: 15px 30px; 
            border-radius: 10px; 
            font-size: 1.1em; 
            cursor: pointer; 
            transition: all 0.3s ease;
            margin: 10px;
        }
        .button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
        .button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .button.success { background: linear-gradient(45deg, #4ecdc4, #44a08d); }
        .button.danger { background: linear-gradient(45deg, #ff6b6b, #c0392b); }
        .controls { display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; }
        .log { 
            background: rgba(0,0,0,0.3); 
            padding: 20px; 
            border-radius: 10px; 
            font-family: 'Courier New', monospace; 
            max-height: 300px; 
            overflow-y: auto;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .log-entry { margin-bottom: 5px; padding: 5px; border-radius: 5px; }
        .log-success { background: rgba(76, 175, 80, 0.2); }
        .log-error { background: rgba(244, 67, 54, 0.2); }
        .log-info { background: rgba(33, 150, 243, 0.2); }
        .indicator { 
            display: inline-block; 
            width: 12px; 
            height: 12px; 
            border-radius: 50%; 
            margin-right: 8px;
        }
        .indicator.running { background: #4caf50; }
        .indicator.stopped { background: #f44336; }
        .indicator.error { background: #ff9800; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🖱️ Auto-Clicker Control Center</h1>
            <p class="subtitle">Real-time automation and monitoring system</p>
        </header>
        
        <div class="card">
            <div class="status-grid">
                <div class="status-item">
                    <div class="status-value" id="status">🔴 Stopped</div>
                    <div class="status-label">Status</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="clicks">0</div>
                    <div class="status-label">Total Clicks</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="uptime">0s</div>
                    <div class="status-label">Uptime</div>
                </div>
                <div class="status-item">
                    <div class="status-value" id="health">✅ Healthy</div>
                    <div class="status-label">System</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🎮 Controls</h2>
            <div class="controls">
                <button class="button success" onclick="startAutoClicker()">▶️ Start Auto-Clicker</button>
                <button class="button danger" onclick="stopAutoClicker()">⏹️ Stop Auto-Clicker</button>
                <button class="button" onclick="testClick()">🖱️ Test Click</button>
                <button class="button" onclick="checkStatus()">📊 Check Status</button>
            </div>
        </div>
        
        <div class="card">
            <h2>📋 Event Log</h2>
            <div class="log" id="eventLog">
                <div class="log-entry log-info">🔍 System initialized. Ready for automation.</div>
            </div>
        </div>
        
        <div class="card">
            <h2>🔗 Quick Links</h2>
            <div class="controls">
                <button class="button" onclick="window.open('/test', '_blank')">🧪 Run Tests</button>
                <button class="button" onclick="window.open('/health', '_blank')">💚 Health Check</button>
            </div>
        </div>
    </div>
    
    <script>
        let isRunning = false;
        let clickCount = 0;
        let startTime = null;
        
        function addLog(message, type = 'info') {
            const log = document.getElementById('eventLog');
            const entry = document.createElement('div');
            entry.className = \`log-entry log-\${type}\`;
            entry.innerHTML = \`[\${new Date().toLocaleTimeString()}] \${message}\`;
            log.appendChild(entry);
            log.scrollTop = log.scrollHeight;
        }
        
        function updateStatus(running) {
            isRunning = running;
            const statusEl = document.getElementById('status');
            if (running) {
                statusEl.innerHTML = '<span class="indicator running"></span>🟢 Running';
                addLog('🚀 Auto-clicker started', 'success');
            } else {
                statusEl.innerHTML = '<span class="indicator stopped"></span>🔴 Stopped';
                addLog('⏹️ Auto-clicker stopped', 'info');
            }
        }
        
        async function startAutoClicker() {
            if (isRunning) {
                addLog('⚠️ Auto-clicker already running', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/auto-clicker/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        area: { x: 0, y: 0, width: 800, height: 600 },
                        click: { button: 'left', clickType: 'single' },
                        interval: 1000
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    startTime = Date.now();
                    updateStatus(true);
                    updateUptime();
                } else {
                    addLog(\`❌ Failed to start: \${result.error}\`, 'error');
                }
            } catch (error) {
                addLog(\`❌ Start error: \${error.message}\`, 'error');
            }
        }
        
        async function stopAutoClicker() {
            if (!isRunning) {
                addLog('⚠️ Auto-clicker not running', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/auto-clicker/stop', {
                    method: 'POST'
                });
                
                const result = await response.json();
                if (result.success) {
                    updateStatus(false);
                } else {
                    addLog(\`❌ Failed to stop: \${result.error}\`, 'error');
                }
            } catch (error) {
                addLog(\`❌ Stop error: \${error.message}\`, 'error');
            }
        }
        
        async function testClick() {
            try {
                addLog('🖱️ Executing test click...', 'info');
                const response = await fetch('/api/test-click', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ x: 100, y: 100 })
                });
                
                const result = await response.json();
                if (result.success) {
                    clickCount++;
                    document.getElementById('clicks').textContent = clickCount;
                    addLog(\`✅ Test click successful at (\${result.position.x}, \${result.position.y})\`, 'success');
                } else {
                    addLog(\`❌ Test click failed: \${result.error}\`, 'error');
                }
            } catch (error) {
                addLog(\`❌ Test click error: \${error.message}\`, 'error');
            }
        }
        
        async function checkStatus() {
            try {
                const response = await fetch('/api/auto-clicker/status');
                const result = await response.json();
                if (result.success && result.sessions.length > 0) {
                    const session = result.sessions[0];
                    updateStatus(session.isRunning);
                    clickCount = session.totalClicks || 0;
                    document.getElementById('clicks').textContent = clickCount;
                    addLog('📊 Status updated', 'info');
                }
            } catch (error) {
                addLog(\`❌ Status check error: \${error.message}\`, 'error');
            }
        }
        
        function updateUptime() {
            if (isRunning && startTime) {
                const uptime = Math.floor((Date.now() - startTime) / 1000);
                document.getElementById('uptime').textContent = uptime + 's';
                setTimeout(updateUptime, 1000);
            }
        }
        
        // Check initial status
        checkStatus();
        
        // Auto-refresh status every 5 seconds
        setInterval(checkStatus, 5000);
    </script>
</body>
</html>`;
        
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(html);
    }
}

// Auto-start the server
if (require.main === module) {
    try {
        console.log('🚀 Starting Simple Server...');
        const server = new SimpleServer();
        server.start();
    } catch (error) {
        console.error('❌ Failed to start:', error);
        process.exit(1);
    }
}

module.exports = SimpleServer;
