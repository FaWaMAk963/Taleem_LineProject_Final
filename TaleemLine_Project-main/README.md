# TaleemLine: Voice-Based Socratic Learning Agent

TaleemLine is an offline AI-powered tutor designed to bridge the educational gap in Pakistan. It uses a Finite State Machine (FSM) to guide students through Socratic learning in Urdu and English.

## Quick Start for Teammates

To get this project running on your machine exactly like the development build, follow these steps in order.

### 1. System Requirements (The Foundation)
You must have these two non-Python tools installed first:
* **Python 3.10+**: Download from [python.org](https://www.python.org/). **(Check "Add Python to PATH" during install!)**
* **FFmpeg**: Required for audio processing. 
  * *Windows:* Open PowerShell as Admin and run: `winget install ffmpeg`

### 2. The Brain (Ollama & Llama-3)
The AI reasoning happens offline via Ollama.
1. Download and install **Ollama** from [ollama.com](https://ollama.com/).
2. Open your terminal and run:
   ```bash
   ollama pull llama3
### 3. Install Python Libraries
Once Python is installed, open your terminal and run this single command to install every "skill" the project needs:

```bash
pip install openai-whisper requests transitions pyttsx3 gtts


### 4. How to Check if You're Ready

Run these commands one by one. If they don't show an error, you are good to go!

1. **Check Whisper:** `pip show openai-whisper`
2. **Check States:** `pip show transitions`
3. **Check Connection:** Run `python test_connection.py` 
   *(This confirms if your Llama-3 brain is awake and talking!)*


Tip
You could also just install by running the following the terminal:
pip install -r requirements.txt
