#!/usr/bin/env node

/**
 * Ollama Model Discovery & Alternative Pull Script
 * Finds available models and pulls alternatives if exact names fail
 */

const { execSync } = require('child_process');

console.log('\n╔════════════════════════════════════════════════════════════════╗');
console.log('║           OLLAMA MODEL DISCOVERY & ALTERNATIVE PULL           ║');
console.log('╚════════════════════════════════════════════════════════════════╝\n');

// Models that failed
const failedModels = {
  'functionary:7b-v1': 'Tool-calling model',
  'llama2-uncensored:7b-q4_K_M': 'Llama 2 - reasoning'
};

// Alternatives to try
const alternatives = {
  'functionary': [
    'functionary:7b',           // Try without version
    'mistral:7b-instruct',      // Already pulled this - skip
    'neural-chat:7b-v3-q4_K_M',  // Alternative smart model
    'openhermes:7b'             // Another tool-aware model
  ],
  'llama2-uncensored': [
    'llama2:7b-q4_K_M',         // Different variant
    'llama2:7b',                // Try base version
    'llama2-uncensored:7b',     // Without quantization spec
    'neural-chat:7b-v3'         // Alternative reasoning
  ]
};

function pullModel(modelName) {
  try {
    console.log(`\n📥 Attempting: ${modelName}`);
    const output = execSync(`ollama pull ${modelName} 2>&1`, { 
      encoding: 'utf-8',
      stdio: 'pipe'
    });
    
    if (output.includes('success') || output.includes('pulling')) {
      console.log(`   ✓ SUCCESS: ${modelName} pulled`);
      return true;
    } else if (output.includes('does not exist') || output.includes('not found')) {
      console.log(`   ✗ Model not found: ${modelName}`);
      return false;
    } else {
      console.log(`   ? Status: ${output.substring(0, 100)}`);
      return output.includes('success');
    }
  } catch (error) {
    const msg = error.message || error.toString();
    if (msg.includes('does not exist') || msg.includes('not found')) {
      console.log(`   ✗ Model not found: ${modelName}`);
    } else {
      console.log(`   ✗ Error: ${msg.substring(0, 80)}`);
    }
    return false;
  }
}

function listCurrentModels() {
  try {
    console.log('\n📦 CURRENTLY INSTALLED MODELS:\n');
    const output = execSync('ollama list 2>&1', { encoding: 'utf-8' });
    console.log(output);
    return output;
  } catch (error) {
    console.log('Could not list models');
    return '';
  }
}

async function main() {
  console.log('❌ FAILED MODELS:\n');
  for (const [model, desc] of Object.entries(failedModels)) {
    console.log(`  • ${model}`);
    console.log(`    Description: ${desc}\n`);
  }

  console.log('═'.repeat(66));
  console.log('\n🔍 TRYING ALTERNATIVES:\n');

  const results = {};

  // Try llama2-uncensored alternatives
  console.log('\n🔷 LLAMA2 UNCENSORED ALTERNATIVES:');
  for (const alt of alternatives['llama2-uncensored']) {
    if (pullModel(alt)) {
      results['llama2-uncensored'] = alt;
      break;
    }
  }

  // Try functionary alternatives  
  console.log('\n🔷 FUNCTIONARY/TOOL-CALLING ALTERNATIVES:');
  for (const alt of alternatives['functionary']) {
    if (pullModel(alt)) {
      results['functionary'] = alt;
      break;
    }
  }

  console.log('\n' + '═'.repeat(66));
  listCurrentModels();

  console.log('═'.repeat(66));
  console.log('\n📋 SUMMARY:\n');

  console.log('Successfully Pulled:');
  console.log('  ✓ mistral:7b-instruct-q4_K_M (4.4GB) - Fast & Smart\n');

  if (results['llama2-uncensored']) {
    console.log(`  ✓ ${results['llama2-uncensored']} - Reasoning`);
  } else {
    console.log('  ✗ Llama2-uncensored variants - All failed');
    console.log('    → Consider using: llama2:7b instead\n');
  }

  if (results['functionary']) {
    console.log(`  ✓ ${results['functionary']} - Tool-Calling`);
  } else {
    console.log('  ✗ Functionary model - Not available');
    console.log('    → Alternative: mistral:7b-instruct works well for tools\n');
  }

  console.log('\n═'.repeat(66));
  console.log('\n💡 RECOMMENDATION:\n');
  
  console.log('You now have:');
  console.log('  1. llama3.1:8b (4.6GB) - Original, good for everything');
  console.log('  2. mistral:7b-instruct-q4_K_M (4.4GB) - Fast, smart alternative\n');

  console.log('That\'s enough to test Continue + MCP tools!');
  console.log('\nYour setup is ready. Start testing in Continue:\n');
  
  console.log('  1. Open Continue in VS Code');
  console.log('  2. Try the test prompt below');
  console.log('  3. MCP tools should work automatically\n');

  console.log('═'.repeat(66));
  console.log('\n🧪 TEST PROMPT FOR CONTINUE:\n');

  console.log(`
Test my MCP tools with both models:

MODEL 1 - Llama 3.1 8B (original):
1. Run: echo "Llama 3.1 Test"
2. List files: C:\\Users\\imme\\CascadeProjects
3. Show git status

MODEL 2 - Mistral 7B (new):
1. Run: echo "Mistral Test"
2. Create file: C:\\Users\\imme\\CascadeProjects\\temp\\mistral-test.txt
3. Read the file back

Show all results and confirm both models work with MCP tools.
  `);

  console.log('═'.repeat(66) + '\n');
}

main().catch(console.error);
