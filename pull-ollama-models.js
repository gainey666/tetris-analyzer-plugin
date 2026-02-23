#!/usr/bin/env node

/**
 * Pull Ollama Models Script
 * Pulls the 3 recommended models to the remote Ollama instance
 */

const https = require('https');
const http = require('http');

const OLLAMA_URL = 'http://192.168.0.94:11434';

const models = [
  'mistral:7b-instruct-q4_K_M',
  'llama2-uncensored:7b-q4_K_M',
  'functionary:7b-v1'
];

async function pullModel(model) {
  return new Promise((resolve, reject) => {
    console.log(`\n📥 Pulling ${model}...`);
    
    const body = JSON.stringify({ name: model });
    
    const options = {
      hostname: '192.168.0.94',
      port: 11434,
      path: '/api/pull',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      let lastStatus = '';
      
      res.on('data', (chunk) => {
        data += chunk.toString();
        
        // Parse streaming JSON responses
        const lines = data.split('\n');
        for (const line of lines) {
          if (line.trim()) {
            try {
              const json = JSON.parse(line);
              if (json.status) {
                process.stdout.write(`\r  ${json.status}`);
                lastStatus = json.status;
              }
            } catch (e) {
              // Not JSON, skip
            }
          }
        }
        data = lines[lines.length - 1]; // Keep last incomplete line
      });

      res.on('end', () => {
        console.log('\n  ✓ Done');
        resolve();
      });
    });

    req.on('error', (e) => {
      reject(e);
    });

    req.write(body);
    req.end();
  });
}

async function verifyModels() {
  return new Promise((resolve, reject) => {
    http.get(`${OLLAMA_URL}/api/tags`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.models || []);
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function main() {
  console.log('\n╔════════════════════════════════════════════════════════════════╗');
  console.log('║           OLLAMA MODEL PULL MANAGER                            ║');
  console.log('║        Pulling recommended models to 192.168.0.94              ║');
  console.log('╚════════════════════════════════════════════════════════════════╝\n');

  try {
    console.log('Checking Ollama connection...');
    const existing = await verifyModels();
    console.log(`✓ Connected! Found ${existing.length} existing models\n`);

    console.log('Models to pull:');
    models.forEach((m, i) => {
      const alreadyExists = existing.some(e => e.name.includes(m.split(':')[0]));
      console.log(`  ${i + 1}. ${m} ${alreadyExists ? '(already installed)' : '(new)'}`);
    });

    console.log('\n⏳ This may take 10-30 minutes depending on your connection...\n');
    console.log('═'.repeat(66) + '\n');

    for (const model of models) {
      try {
        await pullModel(model);
      } catch (error) {
        console.error(`✗ Error pulling ${model}: ${error.message}`);
      }
    }

    console.log('\n' + '═'.repeat(66));
    console.log('\n✓ All done! Verifying models...\n');

    const final = await verifyModels();
    console.log('Current models on Ollama:');
    final.forEach(m => {
      const size = (m.size / 1024 / 1024 / 1024).toFixed(1);
      const quant = m.details?.quantization_level || 'unknown';
      console.log(`  • ${m.name.padEnd(40)} ${size}GB (${quant})`);
    });

    console.log('\n╔════════════════════════════════════════════════════════════════╗');
    console.log('║                  ✓ READY FOR CONTINUE!                        ║');
    console.log('╚════════════════════════════════════════════════════════════════╝\n');

  } catch (error) {
    console.error('✗ Error:', error.message);
    console.log('\nℹ️  Troubleshooting:');
    console.log('   1. Make sure Ollama is running on 192.168.0.94:11434');
    console.log('   2. Check network connectivity to that machine');
    console.log('   3. Try manually: ollama pull mistral:7b-instruct-q4_K_M');
    console.log('   4. Then run this script again\n');
  }
}

main().catch(console.error);
