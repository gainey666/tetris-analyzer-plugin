/**
 * Auto-Clicker API Server
 * REST API for controlling the auto-clicker tool
 */

const express = require('express');
const cors = require('cors');
const path = require('path');
const { AutoClickerEngine } = require('C:/Users/imme/CascadeProjects/windsurf-project-13/src/core/auto-clicker/auto-clicker-engine');
const { v4: uuidv4 } = require('uuid');

class APIServer {
    constructor(port = 3001) {
        this.app = express();
        this.port = port;
        this.server = null;
        this.autoClicker = new AutoClickerEngine();
        this.sessions = new Map();
        this.webhooks = new Map();
        
        this.setupMiddleware();
        this.setupRoutes();
        this.setupEventHandlers();
    }

    setupMiddleware() {
        this.app.use(cors());
        this.app.use(express.json());
        this.app.use(express.static(path.join(__dirname, '..', 'ui')));
        
        // Request logging
        this.app.use((req, res, next) => {
            console.log(`📡 ${req.method} ${req.path} - ${new Date().toISOString()}`);
            next();
        });
    }

    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                version: '1.0.0',
                activeSessions: this.sessions.size
            });
        });

        // Start auto-clicker
        this.app.post('/api/auto-clicker/start', async (req, res) => {
            try {
                const config = this.validateConfig(req.body);
                
                // Generate session ID
                const sessionId = uuidv4();
                
                // Create auto-clicker instance for this session
                const clicker = new AutoClickerEngine();
                
                // Store session
                this.sessions.set(sessionId, {
                    clicker: clicker,
                    config: config,
                    startTime: Date.now(),
                    status: 'starting'
                });
                
                // Start the auto-clicker
                await clicker.start(config);
                
                // Update session status
                this.sessions.get(sessionId).status = 'running';
                
                res.json({
                    success: true,
                    sessionId: sessionId,
                    status: 'started',
                    config: config
                });
                
            } catch (error) {
                console.error('❌ Start failed:', error);
                res.status(400).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // Get status
        this.app.get('/api/auto-clicker/status/:sessionId?', (req, res) => {
            try {
                const sessionId = req.params.sessionId;
                
                if (sessionId) {
                    // Get specific session status
                    const session = this.sessions.get(sessionId);
                    if (!session) {
                        return res.status(404).json({
                            success: false,
                            error: 'Session not found'
                        });
                    }
                    
                    const status = session.clicker.getStatus();
                    res.json({
                        success: true,
                        sessionId: sessionId,
                        ...status
                    });
                    
                } else {
                    // Get all sessions status
                    const allStatus = {};
                    for (const [id, session] of this.sessions) {
                        allStatus[id] = {
                            status: session.status,
                            startTime: session.startTime,
                            ...session.clicker.getStatus()
                        };
                    }
                    
                    res.json({
                        success: true,
                        sessions: allStatus,
                        totalSessions: this.sessions.size
                    });
                }
                
            } catch (error) {
                console.error('❌ Status check failed:', error);
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // Stop auto-clicker
        this.app.post('/api/auto-clicker/stop/:sessionId?', async (req, res) => {
            try {
                const sessionId = req.params.sessionId;
                
                if (sessionId) {
                    // Stop specific session
                    const session = this.sessions.get(sessionId);
                    if (!session) {
                        return res.status(404).json({
                            success: false,
                            error: 'Session not found'
                        });
                    }
                    
                    const finalStats = session.clicker.stop();
                    this.sessions.delete(sessionId);
                    
                    res.json({
                        success: true,
                        status: 'stopped',
                        sessionId: sessionId,
                        finalStats: finalStats
                    });
                    
                } else {
                    // Stop all sessions
                    const finalStats = {};
                    for (const [id, session] of this.sessions) {
                        finalStats[id] = session.clicker.stop();
                    }
                    
                    this.sessions.clear();
                    
                    res.json({
                        success: true,
                        status: 'all_stopped',
                        finalStats: finalStats
                    });
                }
                
            } catch (error) {
                console.error('❌ Stop failed:', error);
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // Save configuration
        this.app.post('/api/config/:name', async (req, res) => {
            try {
                const name = req.params.name;
                const config = this.validateConfig(req.body);
                
                const clicker = new AutoClickerEngine();
                const saved = await clicker.saveConfig(name, config);
                
                if (saved) {
                    res.json({
                        success: true,
                        message: `Configuration ${name} saved successfully`
                    });
                } else {
                    res.status(500).json({
                        success: false,
                        error: 'Failed to save configuration'
                    });
                }
                
            } catch (error) {
                console.error('❌ Save config failed:', error);
                res.status(400).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // Load configuration
        this.app.get('/api/config/:name', async (req, res) => {
            try {
                const name = req.params.name;
                
                const clicker = new AutoClickerEngine();
                const config = await clicker.loadConfig(name);
                
                if (config) {
                    res.json({
                        success: true,
                        name: name,
                        config: config
                    });
                } else {
                    res.status(404).json({
                        success: false,
                        error: 'Configuration not found'
                    });
                }
                
            } catch (error) {
                console.error('❌ Load config failed:', error);
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // List configurations
        this.app.get('/api/config', async (req, res) => {
            try {
                const fs = require('fs').promises;
                const configDir = path.join(__dirname, '..', 'config');
                
                try {
                    const files = await fs.readdir(configDir);
                    const configs = files.filter(file => file.endsWith('.json'))
                        .map(file => file.replace('.json', ''));
                    
                    res.json({
                        success: true,
                        configurations: configs
                    });
                    
                } catch (error) {
                    res.json({
                        success: true,
                        configurations: []
                    });
                }
                
            } catch (error) {
                console.error('❌ List configs failed:', error);
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // Webhook registration
        this.app.post('/api/webhook/:sessionId', async (req, res) => {
            try {
                const sessionId = req.params.sessionId;
                const webhookUrl = req.body.url;
                
                if (!webhookUrl) {
                    return res.status(400).json({
                        success: false,
                        error: 'Webhook URL is required'
                    });
                }
                
                this.webhooks.set(sessionId, webhookUrl);
                
                res.json({
                    success: true,
                    message: 'Webhook registered successfully',
                    sessionId: sessionId,
                    webhookUrl: webhookUrl
                });
                
            } catch (error) {
                console.error('❌ Webhook registration failed:', error);
                res.status(400).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // Serve UI
        this.app.get('/', (req, res) => {
            res.sendFile(path.join(__dirname, '..', 'ui', 'index.html'));
        });
    }

    setupEventHandlers() {
        // Handle auto-clicker events
        this.autoClicker.on('click', async (data) => {
            console.log('🖱️ Click detected:', data);
            
            // Send webhook if registered
            await this.sendWebhook(data.sessionId, {
                event: 'click_detected',
                data: data
            });
        });

        this.autoClicker.on('error', async (data) => {
            console.error('❌ Auto-clicker error:', data);
            
            // Send webhook if registered
            await this.sendWebhook(data.sessionId, {
                event: 'error',
                data: data
            });
        });

        this.autoClicker.on('started', async (data) => {
            console.log('🚀 Auto-clicker started:', data);
            
            // Send webhook if registered
            await this.sendWebhook(data.sessionId, {
                event: 'started',
                data: data
            });
        });

        this.autoClicker.on('stopped', async (data) => {
            console.log('🛑 Auto-clicker stopped:', data);
            
            // Send webhook if registered
            await this.sendWebhook(data.sessionId, {
                event: 'stopped',
                data: data
            });
        });
    }

    validateConfig(config) {
        const required = ['area'];
        const missing = required.filter(field => !config[field]);
        
        if (missing.length > 0) {
            throw new Error(`Missing required fields: ${missing.join(', ')}`);
        }
        
        // Validate area
        const { x, y, width, height } = config.area;
        if (typeof x !== 'number' || typeof y !== 'number' || 
            typeof width !== 'number' || typeof height !== 'number') {
            throw new Error('Area coordinates must be numbers');
        }
        
        if (width <= 0 || height <= 0) {
            throw new Error('Area width and height must be positive');
        }
        
        // Set defaults
        return {
            area: config.area,
            targetPattern: config.targetPattern || 'yes|no',
            confidence: config.confidence || 0.9,
            clickAction: config.clickAction || 'left',
            refreshRate: config.refreshRate || 500,
            name: config.name || 'unnamed'
        };
    }

    async sendWebhook(sessionId, data) {
        const webhookUrl = this.webhooks.get(sessionId);
        if (!webhookUrl) return;
        
        try {
            const response = await fetch(webhookUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                console.error('❌ Webhook failed:', response.status);
            }
        } catch (error) {
            console.error('❌ Webhook error:', error);
        }
    }

    start() {
        try {
            console.log(`🔧 Attempting to listen on port ${this.port}...`);
            
            // Try different binding approaches
            const options = [
                { host: '127.0.0.1', port: this.port },
                { host: 'localhost', port: this.port },
                { port: this.port }
            ];
            
            let attempt = 0;
            const tryListen = () => {
                if (attempt >= options.length) {
                    console.error('❌ All binding attempts failed');
                    return;
                }
                
                const option = options[attempt];
                console.log(`🔄 Attempt ${attempt + 1}: binding to ${option.host || 'default'}:${option.port}`);
                
                this.server = this.app.listen(option, () => {
                    console.log(`🌐 Auto-Clicker API Server running on http://localhost:${this.port}`);
                    console.log('📊 API Documentation: http://localhost:' + this.port + '/api');
                    console.log('🎮 Web Interface: http://localhost:' + this.port);
                    console.log('✅ Server successfully started and listening');
                    console.log('🎉 SERVER IS READY! Press Ctrl+C to stop');
                    console.log('📝 Test with: curl http://localhost:3001/health');
                });
                
                this.server.on('error', (error) => {
                    console.error(`❌ Attempt ${attempt + 1} failed:`, error.message);
                    attempt++;
                    if (attempt < options.length) {
                        tryListen();
                    } else {
                        console.error('❌ All binding attempts exhausted');
                        throw error;
                    }
                });
                
                console.log(`🎯 listen() called for attempt ${attempt + 1}...`);
            };
            
            tryListen();
            
        } catch (error) {
            console.error('❌ FAILED TO START LISTENING:', error);
            console.error('❌ ERROR STACK:', error.stack);
            throw error;
        }
    }

    stop() {
        if (this.server) {
            this.server.close();
            console.log('🛑 API Server stopped');
        }
    }
}

module.exports = APIServer;

// Auto-start the server when this file is run directly
if (require.main === module) {
    try {
        console.log('🚀 Starting API Server...');
        console.log('📦 Loading dependencies...');
        
        // Test dependencies
        const express = require('express');
        console.log('✅ Express loaded');
        
        const { AutoClickerEngine } = require('C:/Users/imme/CascadeProjects/windsurf-project-13/src/core/auto-clicker/auto-clicker-engine');
        console.log('✅ AutoClickerEngine loaded');
        
        console.log('🏗️ Creating server instance...');
        const server = new APIServer();
        console.log('✅ Server instance created');
        
        console.log('🔧 Starting server...');
        server.start();
        console.log('🎯 Server start() called');
        
        // Add unhandled error handlers
        process.on('uncaughtException', (error) => {
            console.error('❌ UNCAUGHT EXCEPTION:', error);
            console.error('❌ ERROR STACK:', error.stack);
            process.exit(1);
        });
        
        process.on('unhandledRejection', (reason, promise) => {
            console.error('❌ UNHANDLED REJECTION:', reason);
            console.error('❌ PROMISE:', promise);
            process.exit(1);
        });
        
    } catch (error) {
        console.error('❌ FAILED TO START SERVER:', error);
        console.error('❌ ERROR STACK:', error.stack);
        process.exit(1);
    }
}
