#!/usr/bin/env node

/**
 * COMPREHENSIVE MCP TOOLS TEST SESSION
 * Run this test sequentially - each test will verify one MCP tool
 * All tests use REAL paths and valid operations
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

const BASE_DIR = 'C:\\Users\\imme\\CascadeProjects';
const DATA_DIR = path.join(BASE_DIR, 'data');
const TEMP_DIR = path.join(BASE_DIR, 'temp');

// Ensure directories exist
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
if (!fs.existsSync(TEMP_DIR)) fs.mkdirSync(TEMP_DIR, { recursive: true });

const TESTS = [];
let testResults = [];

function test(name, tool, instructions, expectedBehavior) {
  TESTS.push({ name, tool, instructions, expectedBehavior });
}

// ============================================
// COMPREHENSIVE MCP TOOL TESTS
// ============================================

// 1. TERMINAL COMMANDS
test(
  '1. run_terminal_command',
  'run_terminal_command',
  'Ask Claude to run: echo "Testing MCP Terminal"',
  'Should output: "Testing MCP Terminal"'
);

// 2. FILE OPERATIONS
test(
  '2. read_file',
  'read_file',
  `Ask Claude to read: ${BASE_DIR}\\package.json`,
  'Should show package.json contents'
);

test(
  '3. write_file',
  'write_file',
  `Ask Claude to create a file: ${TEMP_DIR}\\test.txt with content "MCP Test Success"`,
  'Should create file and confirm'
);

test(
  '4. list_directory',
  'list_directory',
  `Ask Claude to list files in: ${BASE_DIR}`,
  'Should show contents of CascadeProjects folder'
);

test(
  '5. search_files',
  'search_files',
  `Ask Claude to find all files with "windsurf" in the name in: ${BASE_DIR}`,
  'Should find windsurf-project folders'
);

// 3. GIT OPERATIONS
test(
  '6. git_status',
  'git_status',
  `Ask Claude to check git status of: ${BASE_DIR}`,
  'Should show git status (modified files, untracked files, etc)'
);

test(
  '7. git_log',
  'git_log',
  `Ask Claude to show last 5 commits in: ${BASE_DIR}`,
  'Should display recent commit history'
);

test(
  '8. git_diff',
  'git_diff',
  `Ask Claude to show git diff in: ${BASE_DIR}`,
  'Should show changes between last commit and current state'
);

// 4. PYTHON OPERATIONS
test(
  '9. execute_python',
  'execute_python',
  'Ask Claude to run Python: print("Python MCP Test")',
  'Should output: Python MCP Test'
);

test(
  '10. execute_python_file',
  'execute_python_file',
  `Create a test.py file in ${TEMP_DIR} and ask Claude to execute it`,
  'Should run the Python script and show output'
);

// 5. NPM/NODE.JS OPERATIONS
test(
  '11. npm_install',
  'npm_install',
  `Ask Claude to install a package (e.g., npm install inquirer) in: ${BASE_DIR}`,
  'Should install package and confirm'
);

test(
  '12. npm_run',
  'npm_run',
  `Ask Claude to run: npm run test`,
  'Should execute test script'
);

test(
  '13. npm_list',
  'npm_list',
  `Ask Claude to list packages installed in: ${BASE_DIR}`,
  'Should show installed dependencies'
);

// 6. DATABASE OPERATIONS
test(
  '14. sqlite_query',
  'sqlite_query',
  `Ask Claude to first create a test database at ${DATA_DIR}\\test.db with a users table, then query: SELECT * FROM users`,
  'Should return query results (empty or with data)'
);

test(
  '15. sqlite_execute',
  'sqlite_execute',
  `Ask Claude to insert data: INSERT INTO users (name) VALUES ('Test User') into ${DATA_DIR}\\test.db`,
  'Should confirm insertion'
);

// 7. API/HTTP OPERATIONS
test(
  '16. http_request',
  'http_request',
  'Ask Claude to perform a GET request to: https://api.github.com/users/github',
  'Should return GitHub API response as JSON'
);

test(
  '17. curl_command',
  'curl_command',
  'Ask Claude to run: -X GET https://httpbin.org/get',
  'Should return HTTP response with request details'
);

// 8. CODE QUALITY
test(
  '18. lint_file',
  'lint_file',
  `Ask Claude to lint: ${BASE_DIR}\\package.json`,
  'Should check file and report any issues'
);

test(
  '19. format_file',
  'format_file',
  `Ask Claude to format: ${BASE_DIR}\\package.json`,
  'Should format with Prettier'
);

test(
  '20. tsc_check',
  'tsc_check',
  `Ask Claude to check TypeScript in: ${BASE_DIR}`,
  'Should validate TypeScript (may show no config message)'
);

// 9. BUILD OPERATIONS
test(
  '21. build_project',
  'build_project',
  `Ask Claude to build project in: ${BASE_DIR}`,
  'Should run build command'
);

// 10. ENVIRONMENT VARIABLES
test(
  '22. get_env_var',
  'get_env_var',
  'Ask Claude to get environment variable: PATH',
  'Should return PATH environment variable'
);

test(
  '23. list_env_vars',
  'list_env_vars',
  'Ask Claude to list all environment variables',
  'Should show all environment variables'
);

// 11. UI/AUTOMATION (These may not work in all environments)
test(
  '24. get_window_info',
  'get_window_info',
  'Ask Claude to get window information about VS Code',
  'Should list VS Code window details'
);

test(
  '25. screenshot',
  'screenshot',
  `Ask Claude to take a screenshot and save to: ${TEMP_DIR}\\screenshot.png`,
  'Should capture screenshot'
);

test(
  '26. mouse_click',
  'mouse_click',
  'Ask Claude to click at coordinates (500, 300)',
  'Should move mouse and click'
);

test(
  '27. type_text',
  'type_text',
  'Ask Claude to type "MCP Test" with 50ms delay',
  'Should type text to active window'
);

// 12. AI/LLM OPERATIONS
test(
  '28. list_models',
  'list_models',
  'Ask Claude to list available Ollama models',
  'Should show available LLM models'
);

test(
  '29. ollama_chat',
  'ollama_chat',
  'Ask Claude to chat with Ollama: "What is 2+2?"',
  'Should return LLM response'
);

// 13. WEB SEARCH
test(
  '30. web_search',
  'web_search',
  'Ask Claude to search: "JavaScript async await best practices"',
  'Should return web search results'
);

// Display all tests
async function main() {
  console.log('\n╔════════════════════════════════════════════════════════════════╗');
  console.log('║           MCP TOOLS COMPREHENSIVE TEST SESSION                  ║');
  console.log('║      Follow instructions below to test all tools one by one     ║');
  console.log('╚════════════════════════════════════════════════════════════════╝\n');

  console.log('📋 INSTRUCTIONS:');
  console.log('1. Copy each test instruction below');
  console.log('2. Send it to Claude/Continue in one big chat');
  console.log('3. For each tool, verify the expected behavior');
  console.log('4. Check if the output matches expectations\n');

  console.log('═══════════════════════════════════════════════════════════════════\n');

  for (let i = 0; i < TESTS.length; i++) {
    const t = TESTS[i];
    console.log(`TEST ${i + 1}: ${t.name}`);
    console.log(`Tool: ${t.tool}`);
    console.log(`\n📝 INSTRUCTION:\n"${t.instructions}"\n`);
    console.log(`✓ EXPECTED:\n${t.expectedBehavior}\n`);
    console.log('─'.repeat(67) + '\n');
  }

  console.log('═══════════════════════════════════════════════════════════════════\n');
  
  console.log('🎯 TESTING IN ONE CHAT:');
  console.log(`
You can test all ${TESTS.length} tools in ONE continuous chat by sending this prompt to Claude:

---START PROMPT---

"I have ${TESTS.length} MCP tools configured. Please test each one sequentially:

${TESTS.map((t, i) => 
  `${i + 1}. ${t.name}: ${t.instructions}`
).join('\n\n')}

For each test, please:
1. Execute the tool
2. Show the result
3. Confirm if output matches expected behavior
4. Move to next test

Let's go through all ${TESTS.length} tests!"

---END PROMPT---
`);

  console.log('═══════════════════════════════════════════════════════════════════\n');
  
  console.log('✅ ALTERNATIVE: Test by Category\n');
  
  const categories = {
    'TERMINAL': [1],
    'FILE_OPS': [2, 3, 4, 5],
    'GIT': [6, 7, 8],
    'PYTHON': [9, 10],
    'NPM': [11, 12, 13],
    'DATABASE': [14, 15],
    'API': [16, 17],
    'CODE_QUALITY': [18, 19, 20],
    'BUILD': [21],
    'ENVIRONMENT': [22, 23],
    'UI_AUTOMATION': [24, 25, 26, 27],
    'AI_LLM': [28, 29],
    'WEB_SEARCH': [30]
  };

  for (const [cat, indices] of Object.entries(categories)) {
    const testNames = indices.map(i => TESTS[i-1].name).join(', ');
    console.log(`${cat}: Tests ${testNames}`);
  }

  console.log('\n═══════════════════════════════════════════════════════════════════\n');
  
  console.log('💡 TIPS:');
  console.log('• Use absolute paths like C:\\Users\\imme\\CascadeProjects');
  console.log('• Some tests create files in temp/ directory');
  console.log('• UI/Automation tests may not work in headless environments');
  console.log('• Database tests need sqlite3 installed');
  console.log('• API tests require internet connection');
  console.log('• LLM tests require working Ollama server\n');
  
  console.log('🚀 Ready to test! Copy the prompt above and send to Claude in Continue.\n');
}

main().catch(console.error);
