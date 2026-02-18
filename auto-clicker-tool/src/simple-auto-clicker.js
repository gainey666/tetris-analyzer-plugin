/**
 * Simple Auto-Clicker - Just clicks at coordinates without OCR
 */

const { EventEmitter } = require('events');
const { exec } = require('child_process');

class SimpleAutoClicker extends EventEmitter {
    constructor() {
        super();
        this.isRunning = false;
        this.config = {};
        this.sessionId = null;
        this.totalClicks = 0;
        this.startTime = null;
        this.intervalId = null;
    }

    async start(config) {
        console.log('🚀 Starting Simple Auto-Clicker...');
        
        this.config = config;
        this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.isRunning = true;
        this.startTime = Date.now();
        this.totalClicks = 0;
        
        this.emit('started', { sessionId: this.sessionId, config });
        
        try {
            await this.runClickLoop();
        } catch (error) {
            console.error('❌ Simple Auto-Clicker error:', error);
            this.emit('error', error);
            this.stop();
        }
    }

    async runClickLoop() {
        const { area, refreshRate = 1000 } = this.config;
        const { x, y, width, height } = area;
        
        console.log(`🖱️ Starting click loop in area: ${x},${y} ${width}x${height}`);
        
        while (this.isRunning) {
            try {
                // Generate random coordinates within the area
                const clickX = x + Math.floor(Math.random() * width);
                const clickY = y + Math.floor(Math.random() * height);
                
                // Perform the click
                await this.performClick(clickX, clickY);
                this.totalClicks++;
                
                console.log(`✅ Clicked at (${clickX}, ${clickY}) - Total clicks: ${this.totalClicks}`);
                
                // Emit click event
                this.emit('click', {
                    sessionId: this.sessionId,
                    x: clickX,
                    y: clickY,
                    timestamp: Date.now(),
                    totalClicks: this.totalClicks
                });
                
                // Wait for next iteration
                await new Promise(resolve => setTimeout(resolve, refreshRate));
                
            } catch (error) {
                console.error('❌ Click loop error:', error);
                this.emit('error', error);
                break;
            }
        }
    }

    async performClick(x, y) {
        return new Promise((resolve, reject) => {
            const psCommand = `
                Add-Type -TypeDefinition '
                    using System;
                    using System.Runtime.InteropServices;
                    public class Mouse {
                        [DllImport("user32.dll")]
                        public static extern void SetCursorPos(int x, int y);
                        [DllImport("user32.dll")]
                        public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo);
                        public const uint MOUSEEVENTF_LEFTDOWN = 0x02;
                        public const uint MOUSEEVENTF_LEFTUP = 0x04;
                        public const uint MOUSEEVENTF_RIGHTDOWN = 0x08;
                        public const uint MOUSEEVENTF_RIGHTUP = 0x10;
                    }
                ';
                
                # Move mouse to position
                [Mouse]::SetCursorPos(${x}, ${y});
                Start-Sleep -Milliseconds 50;
                
                # Left click
                [Mouse]::mouse_event([Mouse]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
                Start-Sleep -Milliseconds 25;
                [Mouse]::mouse_event([Mouse]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
                
                Write-Output "Clicked at (${x}, ${y})";
            `;
            
            exec(`powershell -Command "${psCommand}"`, (error, stdout, stderr) => {
                if (error) {
                    reject(error);
                } else {
                    resolve(stdout.trim());
                }
            });
        });
    }

    stop() {
        console.log('🛑 Stopping Simple Auto-Clicker...');
        
        this.isRunning = false;
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        const duration = Date.now() - this.startTime;
        
        this.emit('stopped', {
            sessionId: this.sessionId,
            totalClicks: this.totalClicks,
            duration: duration,
            averageRate: this.totalClicks / (duration / 1000)
        });
        
        console.log(`✅ Stopped. Total clicks: ${this.totalClicks}, Duration: ${duration}ms`);
    }

    getStatus() {
        return {
            isRunning: this.isRunning,
            sessionId: this.sessionId,
            totalClicks: this.totalClicks,
            startTime: this.startTime,
            uptime: this.startTime ? Date.now() - this.startTime : 0,
            config: this.config
        };
    }

    async saveConfig(name, config) {
        try {
            // For now, just store in memory
            // In production, would save to file/database
            this.config = config;
            console.log(`💾 Configuration "${name}" saved`);
            return true;
        } catch (error) {
            console.error('❌ Failed to save config:', error);
            return false;
        }
    }

    async loadConfig(name) {
        try {
            // For now, return default config
            // In production, would load from file/database
            const defaultConfig = {
                area: { x: 0, y: 0, width: 800, height: 600 },
                click: { button: 'left', clickType: 'single' },
                interval: 1000
            };
            console.log(`📂 Configuration "${name}" loaded`);
            return defaultConfig;
        } catch (error) {
            console.error('❌ Failed to load config:', error);
            return null;
        }
    }

    async testClick() {
        try {
            console.log('🖱️ Performing test click...');
            
            // Use PowerShell to perform a test click
            const { exec } = require('child_process');
            
            return new Promise((resolve, reject) => {
                const psCommand = `
                    Add-Type -TypeDefinition '
                        using System;
                        using System.Runtime.InteropServices;
                        public class Mouse {
                            [DllImport("user32.dll")]
                            public static extern void SetCursorPos(int x, int y);
                            [DllImport("user32.dll")]
                            public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo);
                            public const uint MOUSEEVENTF_LEFTDOWN = 0x02;
                            public const uint MOUSEEVENTF_LEFTUP = 0x04;
                            public const uint MOUSEEVENTF_RIGHTDOWN = 0x08;
                            public const uint MOUSEEVENTF_RIGHTUP = 0x10;
                        }
                    ';
                    
                    # Get current mouse position
                    $pos = [System.Windows.Forms.Cursor]::Position;
                    $x = $pos.X;
                    $y = $pos.Y;
                    
                    # Move mouse to test position (100, 100)
                    [Mouse]::SetCursorPos(100, 100);
                    Start-Sleep -Milliseconds 100;
                    
                    # Perform left click
                    [Mouse]::mouse_event([Mouse]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
                    Start-Sleep -Milliseconds 50;
                    [Mouse]::mouse_event([Mouse]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
                    
                    # Move back to original position
                    [Mouse]::SetCursorPos($x, $y);
                    
                    Write-Host "Test click executed at (100, 100)";
                `;
                
                exec(`powershell -Command "${psCommand}"`, (error, stdout, stderr) => {
                    if (error) {
                        console.error('❌ Test click failed:', error);
                        reject(error);
                    } else {
                        console.log('✅ Test click successful');
                        resolve({
                            success: true,
                            position: { x: 100, y: 100 },
                            message: 'Test click executed'
                        });
                    }
                });
            });
            
        } catch (error) {
            console.error('❌ Test click error:', error);
            throw error;
        }
    }
}

// Export for CommonJS
module.exports = { SimpleAutoClicker };
