/**
 * Auto-Clicker Tool - Main Entry Point
 * Starts the API server and initializes the application
 */

const APIServer = require('./api-server');
const path = require('path');

// Configuration
const PORT = process.env.PORT || 3001;
const NODE_ENV = process.env.NODE_ENV || 'development';

// Create and start the API server
const server = new APIServer(PORT);

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Received SIGINT, shutting down gracefully...');
    server.stop();
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Received SIGTERM, shutting down gracefully...');
    server.stop();
    process.exit(0);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('❌ Uncaught Exception:', error);
    server.stop();
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
    server.stop();
    process.exit(1);
});

// Start the server
console.log('🚀 Starting Auto-Clicker Tool...');
console.log(`🌍 Environment: ${NODE_ENV}`);
console.log(`📡 Port: ${PORT}`);
console.log(`📁 Working Directory: ${process.cwd()}`);

server.start();

console.log('✅ Auto-Clicker Tool started successfully!');
console.log('📊 API Documentation: http://localhost:' + PORT + '/api');
console.log('🎮 Web Interface: http://localhost:' + PORT);
console.log('🔍 Health Check: http://localhost:' + PORT + '/health');
