/**
 * Auto-Clicker Tool - Core Engine
 * Captures screen areas, performs OCR, and automates mouse clicks
 */

const { EventEmitter } = require('events');
const { execSync } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

class AutoClicker extends EventEmitter {
    constructor() {
        super();
        this.isRunning = false;
        this.lastText = '';
        this.config = {};
        this.sessionId = null;
        this.totalClicks = 0;
        this.startTime = null;
    }

    /**
     * Start the auto-clicker with configuration
     */
    async start(config) {
        console.log('🚀 Starting Auto-Clicker...');
        
        this.config = config;
        this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.isRunning = true;
        this.startTime = Date.now();
        this.totalClicks = 0;
        
        this.emit('started', { sessionId: this.sessionId, config });
        
        try {
            await this.runDetectionLoop();
        } catch (error) {
            console.error('❌ Auto-Clicker error:', error);
            this.emit('error', error);
            this.stop();
        }
    }

    /**
     * Main detection loop
     */
    async runDetectionLoop() {
        while (this.isRunning) {
            try {
                // Capture screen area
                const imageBuffer = await this.captureScreenArea();
                
                // Perform OCR
                const ocrResult = await this.performOCR(imageBuffer);
                
                // Check for changes and decide to click
                const shouldClick = this.shouldClick(ocrResult);
                
                if (shouldClick) {
                    await this.performClick();
                    this.totalClicks++;
                    
                    this.emit('click', {
                        sessionId: this.sessionId,
                        text: ocrResult.text,
                        confidence: ocrResult.confidence,
                        timestamp: Date.now(),
                        totalClicks: this.totalClicks
                    });
                }
                
                // Update last text
                this.lastText = ocrResult.text;
                
                // Wait before next capture
                await this.sleep(this.config.refreshRate || 500);
                
            } catch (error) {
                console.error('❌ Detection loop error:', error);
                this.emit('error', error);
                
                // Continue running even if one capture fails
                await this.sleep(1000);
            }
        }
    }

    /**
     * Capture screen area using Windows API
     */
    async captureScreenArea() {
        const { x, y, width, height } = this.config.area;
        
        // Create temporary file path
        const tempPath = path.join(__dirname, '..', 'temp', `capture_${Date.now()}.png`);
        
        try {
            // Ensure temp directory exists
            await fs.mkdir(path.dirname(tempPath), { recursive: true });
            
            // Use PowerShell to capture screen area
            const psCommand = `
                Add-Type -AssemblyName System.Drawing;
                Add-Type -AssemblyName System.Windows.Forms;
                $screen = [System.Windows.Forms.Screen]::PrimaryScreen;
                $bitmap = New-Object System.Drawing.Bitmap($screen.Bounds.Width, $screen.Bounds.Height);
                $graphics = [System.Drawing.Graphics]::FromImage($bitmap);
                $graphics.CopyFromScreen($screen.Bounds.Location, New-Object System.Drawing.Point(0, 0), $screen.Bounds.Size);
                $graphics.Dispose();
                $cropBitmap = $bitmap.Clone(New-Object System.Drawing.Rectangle(${x}, ${y}, ${width}, ${height}));
                $cropBitmap.Save("${tempPath.replace(/\\/g, '\\\\')}", [System.Drawing.Imaging.ImageFormat]::Png);
                $cropBitmap.Dispose();
                $bitmap.Dispose();
            `;
            
            execSync(`powershell -Command "${psCommand}"`);
            
            // Read the captured image
            const imageBuffer = await fs.readFile(tempPath);
            
            // Clean up temp file
            await fs.unlink(tempPath);
            
            return imageBuffer;
            
        } catch (error) {
            console.error('❌ Screen capture failed:', error);
            throw new Error(`Screen capture failed: ${error.message}`);
        }
    }

    /**
     * Perform OCR on image buffer
     */
    async performOCR(imageBuffer) {
        // For now, simulate OCR (we'll integrate Tesseract.js later)
        // This is a placeholder implementation
        
        try {
            // Simulate OCR processing time
            await this.sleep(50);
            
            // Simulate text detection
            const simulatedTexts = ['yes', 'no', 'ok', 'cancel', 'accept', 'reject', 'confirm'];
            const randomText = simulatedTexts[Math.floor(Math.random() * simulatedTexts.length)];
            
            return {
                text: randomText,
                confidence: 0.85 + Math.random() * 0.15, // 85-100% confidence
                matches: {
                    yes: /yes/i.test(randomText),
                    no: /no/i.test(randomText),
                    button: /ok|cancel|accept|reject|confirm/i.test(randomText)
                }
            };
            
        } catch (error) {
            console.error('❌ OCR failed:', error);
            throw new Error(`OCR failed: ${error.message}`);
        }
    }

    /**
     * Determine if we should click based on OCR result
     */
    shouldClick(ocrResult) {
        const { text, confidence, matches } = ocrResult;
        
        // Check confidence threshold
        if (confidence < (this.config.confidence || 0.9)) {
            return false;
        }
        
        // Check if text has changed
        if (text === this.lastText) {
            return false;
        }
        
        // Check if text matches target pattern
        const targetPattern = this.config.targetPattern || 'yes|no';
        const regex = new RegExp(targetPattern, 'i');
        return regex.test(text);
    }

    /**
     * Perform mouse click
     */
    async performClick() {
        const { x, y, width, height } = this.config.area;
        const centerX = x + Math.floor(width / 2);
        const centerY = y + Math.floor(height / 2);
        
        console.log(`🖱️ Clicking at (${centerX}, ${centerY})`);
        
        // For now, simulate click (we'll integrate robotjs later)
        try {
            // Simulate click action
            await this.sleep(50);
            
            console.log(`✅ Clicked at (${centerX}, ${centerY})`);
            
            return {
                x: centerX,
                y: centerY,
                action: this.config.clickAction || 'left',
                timestamp: Date.now()
            };
            
        } catch (error) {
            console.error('❌ Click failed:', error);
            throw new Error(`Click failed: ${error.message}`);
        }
    }

    /**
     * Stop the auto-clicker
     */
    stop() {
        console.log('🛑 Stopping Auto-Clicker...');
        
        this.isRunning = false;
        
        const duration = Date.now() - this.startTime;
        
        const finalStats = {
            sessionId: this.sessionId,
            totalClicks: this.totalClicks,
            duration: duration,
            averageConfidence: 0.9, // Placeholder
            lastText: this.lastText
        };
        
        this.emit('stopped', finalStats);
        
        return finalStats;
    }

    /**
     * Get current status
     */
    getStatus() {
        return {
            running: this.isRunning,
            sessionId: this.sessionId,
            lastDetection: {
                text: this.lastText,
                timestamp: this.lastText ? Date.now() : null
            },
            totalClicks: this.totalClicks,
            lastClick: this.totalClicks > 0 ? Date.now() : null,
            config: this.config,
            uptime: this.startTime ? Date.now() - this.startTime : 0
        };
    }

    /**
     * Save configuration
     */
    async saveConfig(name, config) {
        const configPath = path.join(__dirname, '..', 'config', `${name}.json`);
        
        try {
            await fs.mkdir(path.dirname(configPath), { recursive: true });
            await fs.writeFile(configPath, JSON.stringify(config, null, 2));
            
            console.log(`💾 Configuration saved to ${name}.json`);
            return true;
        } catch (error) {
            console.error('❌ Failed to save config:', error);
            return false;
        }
    }

    /**
     * Load configuration
     */
    async loadConfig(name) {
        const configPath = path.join(__dirname, '..', 'config', `${name}.json`);
        
        try {
            const configData = await fs.readFile(configPath, 'utf8');
            const config = JSON.parse(configData);
            
            console.log(`📖 Configuration loaded from ${name}.json`);
            return config;
        } catch (error) {
            console.error('❌ Failed to load config:', error);
            return null;
        }
    }

    /**
     * Utility function to sleep
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

module.exports = AutoClicker;
