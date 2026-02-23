#!/usr/bin/env node

/**
 * MCP Tools Usage Examples
 * Shows how to properly use the MCP tools with Continue
 */

// ============================================
// TERMINAL COMMANDS
// ============================================

// Run: npm install
console.log('✓ Install packages via npm_install tool');

// Run: npm test
console.log('✓ Run tests via npm_run with "test" script');

// Run: npm run build
console.log('✓ Build project via npm_run with "build" script');

// ============================================
// FILE OPERATIONS
// ============================================

// Read files
const fs = require('fs');
const path = require('path');

console.log('✓ Use read_file tool with absolute paths');
console.log('  Example: read_file({ filepath: "C:\\Users\\imme\\CascadeProjects\\file.js" })');

// Write files
console.log('✓ Use write_file tool to create/update files');
console.log('  Example: write_file({ filepath: "C:\\Users\\imme\\CascadeProjects\\output.txt", content: "..." })');

// List directory
console.log('✓ Use list_directory tool with absolute paths');
console.log('  Example: list_directory({ directory: "C:\\Users\\imme\\CascadeProjects" })');

// ============================================
// DATABASE OPERATIONS
// ============================================

console.log('✓ Use sqlite_query for SELECT operations');
console.log('  Example: sqlite_query(');
console.log('    { database: "C:\\Users\\imme\\CascadeProjects\\data\\app.db",');
console.log('      query: "SELECT * FROM users LIMIT 10" }');
console.log('  )');

console.log('✓ Use sqlite_execute for INSERT/UPDATE/DELETE');
console.log('  Example: sqlite_execute(');
console.log('    { database: "C:\\Users\\imme\\CascadeProjects\\data\\app.db",');
console.log('      sql: "INSERT INTO users (name) VALUES (\'John\')" }');
console.log('  )');

// ============================================
// API/HTTP OPERATIONS
// ============================================

console.log('✓ Use http_request for API calls');
console.log('  Example: http_request(');
console.log('    { url: "https://api.example.com/data",');
console.log('      method: "GET",');
console.log('      headers: { "Authorization": "Bearer token" } }');
console.log('  )');

console.log('✓ Use curl_command for curl operations');
console.log('  Example: curl_command(');
console.log('    { command: "-X GET https://api.example.com/data" }');
console.log('  )');

// ============================================
// CODE QUALITY
// ============================================

console.log('✓ Use lint_file to check code');
console.log('  Example: lint_file(');
console.log('    { filepath: "C:\\Users\\imme\\CascadeProjects\\file.js",');
console.log('      fix: true }');
console.log('  )');

console.log('✓ Use format_file to format code');
console.log('  Example: format_file(');
console.log('    { filepath: "C:\\Users\\imme\\CascadeProjects\\file.js" }');
console.log('  )');

console.log('✓ Use tsc_check for TypeScript validation');
console.log('  Example: tsc_check(');
console.log('    { cwd: "C:\\Users\\imme\\CascadeProjects",');
console.log('      noEmit: true }');
console.log('  )');

// ============================================
// GIT OPERATIONS
// ============================================

console.log('✓ Use git_status to check status');
console.log('  Example: git_status({ directory: "C:\\Users\\imme\\CascadeProjects" })');

console.log('✓ Use git_log to view history');
console.log('  Example: git_log({ directory: "C:\\Users\\imme\\CascadeProjects", count: 10 })');

console.log('✓ Use git_diff to see changes');
console.log('  Example: git_diff({ directory: "C:\\Users\\imme\\CascadeProjects" })');

console.log('✓ Use git_commit to commit changes');
console.log('  Example: git_commit({ directory: "C:\\Users\\imme\\CascadeProjects", message: "Fix: issue #123" })');

// ============================================
// PYTHON OPERATIONS
// ============================================

console.log('✓ Use execute_python for inline Python code');
console.log('  Example: execute_python({ script: "print(\'Hello from Python\')" })');

console.log('✓ Use execute_python_file to run Python files');
console.log('  Example: execute_python_file(');
console.log('    { filepath: "C:\\Users\\imme\\CascadeProjects\\script.py",');
console.log('      args: ["--verbose", "input.txt"] }');
console.log('  )');

// ============================================
// ENVIRONMENT VARIABLES
// ============================================

console.log('✓ Use get_env_var to read a variable');
console.log('  Example: get_env_var({ name: "OLLAMA_BASE_URL" })');

console.log('✓ Use list_env_vars to see all variables');
console.log('  Example: list_env_vars()');

// ============================================
// BUILD OPERATIONS
// ============================================

console.log('✓ Use build_project to build');
console.log('  Example: build_project(');
console.log('    { cwd: "C:\\Users\\imme\\CascadeProjects",');
console.log('      command: "npm run build" }');
console.log('  )');

// ============================================
// UI/AUTOMATION
// ============================================

console.log('✓ Use screenshot to capture screen');
console.log('  Example: screenshot({ filename: "C:\\Users\\imme\\Desktop\\screen.png" })');

console.log('✓ Use get_window_info to find windows');
console.log('  Example: get_window_info({ window_title: "VS Code" })');

console.log('✓ Use mouse_click to click');
console.log('  Example: mouse_click({ x: 500, y: 300, button: "left", count: 1 })');

console.log('✓ Use type_text to type');
console.log('  Example: type_text({ text: "Hello world", delay: 50 })');

// ============================================
// AI/LLM OPERATIONS
// ============================================

console.log('✓ Use list_models to see available Ollama models');
console.log('  Example: list_models()');

console.log('✓ Use ollama_chat to chat with LLM');
console.log('  Example: ollama_chat(');
console.log('    { prompt: "What is 2+2?",');
console.log('      model: "llama3.1:8b",');
console.log('      temperature: 0.0,');
console.log('      max_tokens: 1000 }');
console.log('  )');

// ============================================
// WEB SEARCH
// ============================================

console.log('✓ Use web_search to search');
console.log('  Example: web_search({ query: "JavaScript async await", count: 5 })');

console.log('\n📚 All MCP tools configured and ready! Use them with Continue in your prompts.');
