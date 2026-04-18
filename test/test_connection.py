
# ─────────────────────────────────────────────────────────────────────────────
# FILE: test_connection.py
# ─────────────────────────────────────────────────────────────────────────────
# TaleemLine – Ollama Connectivity Check
#
# Purpose:
#   Standalone script to verify that the Ollama server is running and that
#   the llama3 model responds correctly before launching the full app.
#   Run this first if you suspect Ollama is not working.
#
# Usage:
#   python test_connection.py
#
# Expected output (when Ollama is running):
#   Checking if Llama-3 is awake...
#   Response from AI: TaleemLine tayyar hai! ...
#
# If it fails:
#   Make sure Ollama is installed and run: ollama serve
#
# Part of: TaleemLine Voice Learning Agent
# ─────────────────────────────────────────────────────────────────────────────

import requests

def test_brain():
    print("Checking if Llama-3 is awake...")
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": "Say 'TaleemLine is ready' in Urdu", "stream": False}
        )
        print("Response from AI:", response.json()['response'])
    except Exception as e:
        print("Error: Make sure the Ollama app is running in your system tray!")

test_brain()