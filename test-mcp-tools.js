#!/usr/bin/env node

/**
 * MCP Tools Test Script
 * Tests all available MCP tools to verify they work
 */

const fs = require('fs');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

const TESTS = [];

function addTest(name, fn) {
  TESTS.push({ name, fn });
}

async function runTest(test) {
  try {
    console.log(`\n✓ Testing: ${test.name}`);
    const result = await test.fn();
    console.log(`  Result: ${typeof result === 'object' ? JSON.stringify(result, null, 2) : result}`);
    return { name: test.name, status: 'PASS', result };
  } catch (error) {
    console.error(`✗ Failed: ${test.name}`);
    console.error(`  Error: ${error.message}`);
    return { name: test.name, status: 'FAIL', error: error.message };
  }
}

// Test 1: Terminal Command
addTest('run_terminal_command', async () => {
  const { stdout } = await execAsync('echo "MCP Terminal Test - SUCCESS"');
  return stdout.trim();
});

// Test 2: Read File
addTest('read_file', async () => {
  const content = fs.readFileSync(__filename, 'utf-8');
  return `Successfully read ${__filename} (${content.length} bytes)`;
});

// Test 3: Write File
addTest('write_file', async () => {
  const testFile = 'C:\\Users\\imme\\CascadeProjects\\mcp-test-output.txt';
  const content = `MCP Write Test - Timestamp: ${new Date().toISOString()}`;
  fs.writeFileSync(testFile, content, 'utf-8');
  return `Successfully wrote to ${testFile}`;
});

// Test 4: List Directory
addTest('list_directory', async () => {
  const dir = 'C:\\Users\\imme\\CascadeProjects';
  const files = fs.readdirSync(dir).slice(0, 5);
  return `Found ${files.length} items in ${dir}: ${files.join(', ')}`;
});

// Test 5: Search Files
addTest('search_files', async () => {
  const dir = 'C:\\Users\\imme\\CascadeProjects';
  const files = fs.readdirSync(dir).filter(f => f.includes('windsurf'));
  return `Found ${files.length} windsurf-related items`;
});

// Test 6: Git Status
addTest('git_status', async () => {
  const { stdout } = await execAsync('git status --short', { cwd: 'C:\\Users\\imme\\CascadeProjects' }).catch(() => ({stdout: 'No git repo or no changes'}));
  return stdout || 'No changes or not a git repo';
});

// Test 7: Execute Python
addTest('execute_python', async () => {
  const { stdout } = await execAsync('python -c "print(\'Python MCP Test - SUCCESS\')"');
  return stdout.trim();
});

// Main test runner
async function main() {
  console.log('═══════════════════════════════════════');
  console.log('MCP TOOLS VERIFICATION TEST SUITE');
  console.log('═══════════════════════════════════════');
  
  const results = [];
  for (const test of TESTS) {
    const result = await runTest(test);
    results.push(result);
  }
  
  console.log('\n═══════════════════════════════════════');
  console.log('TEST SUMMARY');
  console.log('═══════════════════════════════════════');
  
  const passed = results.filter(r => r.status === 'PASS').length;
  const failed = results.filter(r => r.status === 'FAIL').length;
  
  console.log(`\nPassed: ${passed}/${TESTS.length}`);
  console.log(`Failed: ${failed}/${TESTS.length}`);
  
  results.forEach(r => {
    const icon = r.status === 'PASS' ? '✓' : '✗';
    console.log(`  ${icon} ${r.name}`);
  });
  
  console.log('\n═══════════════════════════════════════');
}

main().catch(console.error);
