═══════════════════════════════════════════════════════════════════
              MCP TOOLS - COMPLETE TEST SESSION
             Test All 30 Tools in One Big Chat
═══════════════════════════════════════════════════════════════════

📋 INSTRUCTIONS:
Copy and paste this entire prompt into Continue and send to Claude.
Claude will test each tool one by one in sequence.

═══════════════════════════════════════════════════════════════════
🚀 COPY THIS PROMPT AND SEND TO CLAUDE:
═══════════════════════════════════════════════════════════════════

I need to test all 30 MCP tools I have configured. Please execute each test
sequentially. For each one, show the result and confirm if it works.

BASE_DIR = C:\Users\imme\CascadeProjects
DATA_DIR = C:\Users\imme\CascadeProjects\data
TEMP_DIR = C:\Users\imme\CascadeProjects\temp

TEST 1: run_terminal_command
- Command: echo "MCP Terminal Test"
- Expected: Should output "MCP Terminal Test"

TEST 2: read_file
- Path: C:\Users\imme\CascadeProjects\package.json
- Expected: Should display package.json contents
- Run now and show output

TEST 3: write_file
- Path: C:\Users\imme\CascadeProjects\temp\test1.txt
- Content: "MCP Write Test - Success"
- Expected: Should create file
- Confirm after writing

TEST 4: list_directory
- Directory: C:\Users\imme\CascadeProjects
- Expected: Should list 20+ items
- Show first 10 items

TEST 5: search_files
- Directory: C:\Users\imme\CascadeProjects
- Pattern: "windsurf"
- Expected: Find windsurf-project folders
- Show results

TEST 6: git_status
- Directory: C:\Users\imme\CascadeProjects
- Expected: Show git status (modified/untracked files)
- Show output

TEST 7: git_log
- Directory: C:\Users\imme\CascadeProjects
- Count: 5
- Expected: Show last 5 commits
- Show output

TEST 8: git_diff
- Directory: C:\Users\imme\CascadeProjects
- Expected: Show changes or "No changes"
- Show output

TEST 9: execute_python
- Script: print("Python MCP Working")
- Expected: Output "Python MCP Working"
- Test now

TEST 10: execute_python_file
- Create a test file first: C:\Users\imme\CascadeProjects\temp\test.py
- Content: print("Python File Test Success")
- Then execute it
- Expected: Show output

TEST 11: npm_install
- Package: inquirer
- Directory: C:\Users\imme\CascadeProjects
- Expected: Package installed successfully
- Confirm

TEST 12: npm_run
- Script: test
- Directory: C:\Users\imme\CascadeProjects
- Expected: npm test script runs
- Show output

TEST 13: npm_list
- Directory: C:\Users\imme\CascadeProjects
- Expected: List installed packages
- Show first 5 packages

TEST 14: sqlite_query
- Database: C:\Users\imme\CascadeProjects\data\test.db
- First create table: CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)
- Then query: SELECT * FROM users
- Expected: Show results (empty is OK)

TEST 15: sqlite_execute
- Database: C:\Users\imme\CascadeProjects\data\test.db
- SQL: INSERT INTO users (name) VALUES ('Test User')
- Expected: SQL executed successfully
- Confirm

TEST 16: http_request
- URL: https://api.github.com/users/github
- Method: GET
- Expected: Return JSON with user data
- Show status and first 100 chars

TEST 17: curl_command
- Command: -X GET https://httpbin.org/ip
- Expected: Return JSON with IP
- Show output

TEST 18: lint_file
- File: C:\Users\imme\CascadeProjects\package.json
- Expected: File linted successfully
- Show any issues

TEST 19: format_file
- File: C:\Users\imme\CascadeProjects\package.json
- Expected: File formatted successfully
- Confirm

TEST 20: tsc_check
- Directory: C:\Users\imme\CascadeProjects
- Expected: TypeScript check (may show "no config" - that's OK)
- Show output

TEST 21: build_project
- Directory: C:\Users\imme\CascadeProjects
- Command: npm run build
- Expected: Build command executes
- Show output

TEST 22: get_env_var
- Variable: PATH
- Expected: Show PATH contents
- Confirm PATH exists

TEST 23: list_env_vars
- Expected: Show environment variables
- Show 5 examples

TEST 24: get_window_info
- Search for: VS Code
- Expected: Show window information
- Confirm if found

TEST 25: screenshot
- File: C:\Users\imme\CascadeProjects\temp\screen.png
- Expected: Screenshot created or message
- Confirm

TEST 26: mouse_click
- X: 500, Y: 300
- Button: left
- Expected: Move and click
- Confirm action

TEST 27: type_text
- Text: "MCP Test String"
- Delay: 50ms
- Expected: Text typed to active window
- Confirm action

TEST 28: list_models
- Expected: Show available Ollama models
- List model names

TEST 29: ollama_chat
- Prompt: "What is 2+2? Answer in one sentence."
- Model: llama3.1:8b
- Expected: LLM response
- Show response

TEST 30: web_search
- Query: "Node.js async await"
- Count: 3
- Expected: Show 3 search results
- Display titles and URLs

═══════════════════════════════════════════════════════════════════

After all tests, please provide a summary:
- How many tests PASSED (✓)
- How many tests FAILED (✗)
- Any tools that need fixes
- Overall status

Let's start with TEST 1 and work through all 30. Go!

═══════════════════════════════════════════════════════════════════
