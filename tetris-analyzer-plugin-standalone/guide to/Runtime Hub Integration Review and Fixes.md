Runtime Hub Integration Fix Plan and Tool Call Guidance

Filename guides back/DECISION_2026-02-22_1902_TETRIS-ARCHITECTURE.md  
Below is a ready-to-copy Markdown document that (1) lists the immediate fixes in priority order, (2) provides the corrected JSON and requirements content, (3) includes a minimal health-check snippet, and (4) explains how to resolve the tool call error you reported (the system expecting a string for CodeContent).
Immediate Fixes Priority Order

    Fix JSON node definition — remove comments and validate JSON.

    Update requirements — add Flask, CORS, Socket.IO client, requests.

    Implement health-check and registration handshake — minimal HTTP + Socket.IO example.

    Make port configurable and add health-check — accept env var or CLI arg.

    Stabilize IPC — temporarily simplify shared-memory path until tests pass.

Corrected JSON Node Definition (copy this exact block)
json

{
  "id": "tetris-analyzer-node",
  "name": "Tetris Analyzer",
  "version": "0.1.0",
  "description": "Runtime Hub node for Tetris Analyzer",
  "entrypoint": "tetris_analyzer_node.py",
  "author": "gainey666",
  "schema": {
    "inputs": [
      { "name": "start", "type": "trigger" },
      { "name": "stop", "type": "trigger" }
    ],
    "outputs": [
      { "name": "status", "type": "json" },
      { "name": "coaching", "type": "json" }
    ]
  },
  "config": {
    "default_port": 3002,
    "use_socketio": true
  }
}

Validation command
bash

python -m json.tool runtime_hub/tetris_analyzer_node.json

requirements.txt Patch (append these lines)
Code

flask>=2.0.0
flask-cors>=3.0.0
python-socketio>=5.0.0
requests>=2.28.0

Minimal Health-Check and Registration Snippet (copyable Python)
python

# runtime_hub/entrypoint_health.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import socketio
import os
import threading
import time
import requests

PORT = int(os.environ.get("TETRIS_PORT", "3002"))
HUB_REG_URL = os.environ.get("RUNTIME_HUB_REG_URL", None)
TOKEN = os.environ.get("RUNTIME_HUB_TOKEN", "")

app = Flask(__name__)
CORS(app)
sio = socketio.Client()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "pid": os.getpid()})

@app.route("/start", methods=["POST"])
def start():
    return jsonify({"status": "started"})

@app.route("/stop", methods=["POST"])
def stop():
    return jsonify({"status": "stopped"})

def register_with_hub():
    if not HUB_REG_URL:
        return
    payload = {"id": "tetris-analyzer-node", "port": PORT}
    try:
        requests.post(HUB_REG_URL, json=payload, timeout=5)
    except Exception:
        pass

def heartbeat_loop():
    while True:
        try:
            if sio.connected:
                sio.emit("heartbeat", {"pid": os.getpid(), "ts": int(time.time()*1000)})
        except Exception:
            pass
        time.sleep(3)

if __name__ == "__main__":
    try:
        sio.connect(os.environ.get("RUNTIME_HUB_SOCKET_URL", "http://127.0.0.1:3000"))
    except Exception:
        pass

    threading.Thread(target=heartbeat_loop, daemon=True).start()
    register_with_hub()
    app.run(host="127.0.0.1", port=PORT)

Why the Tool Call Error Happened and How to Fix It

Symptom: The system/tool expected a string for CodeContent but you provided an object.
Cause: Many file-write APIs or automation tools require the file body to be a single string (raw file content). Passing a parsed object (e.g., a JSON object or Python dict) triggers a type error.

Fix options

A. If you are calling a tool or API that expects CodeContent as a string

    Serialize the object to a string before sending. For JSON, use a JSON serializer so the payload is a string containing the JSON text.

Python example
python

import json

node_obj = {
  "id": "tetris-analyzer-node",
  "name": "Tetris Analyzer",
  "version": "0.1.0",
  # ...
}

code_content = json.dumps(node_obj, indent=2)  # string
# pass code_content to the tool as the CodeContent field

B. If you are using a CLI or shell to write the file

    Use a here-doc or echo with proper quoting.

Shell example
bash

cat > runtime_hub/tetris_analyzer_node.json <<'JSON'
{
  "id": "tetris-analyzer-node",
  "name": "Tetris Analyzer",
  "version": "0.1.0",
  "description": "Runtime Hub node for Tetris Analyzer",
  "entrypoint": "tetris_analyzer_node.py",
  "author": "gainey666",
  "schema": {
    "inputs": [
      { "name": "start", "type": "trigger" },
      { "name": "stop", "type": "trigger" }
    ],
    "outputs": [
      { "name": "status", "type": "json" },
      { "name": "coaching", "type": "json" }
    ]
  },
  "config": {
    "default_port": 3002,
    "use_socketio": true
  }
}
JSON

C. If the tool requires escaped newlines

    Replace newline characters with \n or use the tool’s documented escaping rules. Many APIs accept raw strings with newlines; some require explicit \n sequences.

Practical Next Steps I Recommend You Run Now

    Fix the JSON file using one of the methods above (serialize to string or use shell here-doc). Validate with python -m json.tool.

    Update requirements.txt by appending the four lines shown above. Run pip install -r runtime_hub/requirements.txt in a virtualenv.

    Drop the health-check file into runtime_hub/entrypoint_health.py and run it locally to confirm GET /health returns {"status":"ok"}.

    If you use an automated tool to write files, ensure you pass CodeContent as a string (use json.dumps for JSON).

    Run the integration tests after steps 1–3 to see which failures remain; capture logs for the failing tests.

Quick Decision Guidance

    Handle the tool call error first if it blocks writing the corrected JSON or requirements files. Once you can write files programmatically, apply the JSON and requirements fixes immediately.

    After those two blockers are resolved, implement the health-check and registration handshake and re-run tests.

