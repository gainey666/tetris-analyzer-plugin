/**
 * Comprehensive Endpoint Auditor
 * Tests all HTTP endpoints and verifies functionality
 */

const http = require('http');

class EndpointAuditor {
    constructor(baseURL = 'http://localhost:3001') {
        this.baseURL = baseURL;
        this.results = [];
    }

    async testEndpoint(method, path, body = null) {
        return new Promise((resolve) => {
            const url = new URL(path, this.baseURL);
            const options = {
                hostname: url.hostname,
                port: url.port,
                path: url.pathname,
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            };

            const req = http.request(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        const parsed = data ? JSON.parse(data) : {};
                        resolve({
                            method,
                            path,
                            status: res.statusCode,
                            success: res.statusCode >= 200 && res.statusCode < 300,
                            data: parsed,
                            headers: res.headers
                        });
                    } catch (e) {
                        resolve({
                            method,
                            path,
                            status: res.statusCode,
                            success: res.statusCode >= 200 && res.statusCode < 300,
                            data: data,
                            error: 'JSON parse error'
                        });
                    }
                });
            });

            req.on('error', (error) => {
                resolve({
                    method,
                    path,
                    status: 0,
                    success: false,
                    error: error.message
                });
            });

            if (body) {
                req.write(JSON.stringify(body));
            }
            req.end();
        });
    }

    async runFullAudit() {
        console.log('🔍 STARTING COMPREHENSIVE ENDPOINT AUDIT...\n');

        // Test all endpoints
        const tests = [
            // Health endpoint
            { method: 'GET', path: '/health' },
            
            // Auto-clicker endpoints
            { method: 'GET', path: '/api/auto-clicker/status' },
            { method: 'POST', path: '/api/auto-clicker/start', body: {
                area: { x: 0, y: 0, width: 800, height: 600 },
                click: { button: 'left', clickType: 'single' },
                interval: 1000
            }},
            { method: 'POST', path: '/api/auto-clicker/stop' },
            
            // Test click endpoint
            { method: 'POST', path: '/api/test-click', body: { x: 100, y: 100 } },
            
            // Root endpoint
            { method: 'GET', path: '/' },
            
            // Invalid endpoint (should 404)
            { method: 'GET', path: '/invalid-endpoint' }
        ];

        console.log('📊 Testing endpoints...\n');
        
        for (const test of tests) {
            console.log(`🧪 ${test.method} ${test.path}`);
            const result = await this.testEndpoint(test.method, test.path, test.body);
            
            if (result.success) {
                console.log(`✅ ${result.status} - SUCCESS`);
            } else {
                console.log(`❌ ${result.status} - FAILED: ${result.error || 'Request failed'}`);
            }
            
            if (result.data && Object.keys(result.data).length > 0) {
                console.log(`📄 Response: ${JSON.stringify(result.data, null, 2)}`);
            }
            
            console.log('');
            this.results.push(result);
        }

        // Generate summary
        this.generateSummary();
    }

    generateSummary() {
        console.log('📊 AUDIT SUMMARY\n');
        console.log('='.repeat(50));
        
        const total = this.results.length;
        const successful = this.results.filter(r => r.success).length;
        const failed = total - successful;
        
        console.log(`Total endpoints tested: ${total}`);
        console.log(`✅ Successful: ${successful}`);
        console.log(`❌ Failed: ${failed}`);
        console.log(`📈 Success rate: ${((successful / total) * 100).toFixed(1)}%\n`);
        
        // List failed endpoints
        const failedTests = this.results.filter(r => !r.success);
        if (failedTests.length > 0) {
            console.log('❌ FAILED ENDPOINTS:');
            failedTests.forEach(test => {
                console.log(`   ${test.method} ${test.path} - ${test.status}: ${test.error || 'Request failed'}`);
            });
        }
        
        // List working endpoints
        const workingTests = this.results.filter(r => r.success);
        if (workingTests.length > 0) {
            console.log('\n✅ WORKING ENDPOINTS:');
            workingTests.forEach(test => {
                console.log(`   ${test.method} ${test.path} - ${test.status}`);
            });
        }
        
        console.log('\n🎯 RECOMMENDATIONS:');
        if (failed === 0) {
            console.log('✅ All endpoints are working correctly!');
        } else {
            console.log('❌ Fix the failed endpoints before proceeding');
            console.log('🔧 Check server logs for detailed error information');
        }
    }
}

// Run the audit
if (require.main === module) {
    const auditor = new EndpointAuditor();
    auditor.runFullAudit().catch(console.error);
}

module.exports = EndpointAuditor;
