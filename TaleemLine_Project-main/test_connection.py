# hecks if Ollama is working

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