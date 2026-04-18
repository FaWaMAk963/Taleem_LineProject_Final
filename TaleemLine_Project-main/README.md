# TaleemLine – AI-Powered Voice Learning Agent

TaleemLine is a fully offline, voice-based educational assistant make keeping in mind Pakistani school students (Grades 1–12), prominently those with limited to no access to wi-fi.
Right now runs as a phone-shell GUI on the desktop and teaches through conversation in **Urdu or English**,  
powered entirely by a local **Ollama / Llama3** model — no internet required.

In the future, we would like to extend the project as a phone service that can be called using a network number.

---

## Features

- **Phone-shell UI** — realistic mobile interface built with PyQt5
- **Voice I/O** — speak questions, hear answers (Whisper STT + pyttsx3 TTS)
- **Three learning modes** — Learning, Test (MCQ), and Game (riddles)
- **FSM-driven flow** — structured session: Language → Grade → Subject → Mode → Session
- **Fully offline** — Ollama runs locally; no API keys, no data sent to the cloud
- **Performance tracking** — session history saved per student to a local JSON file
- **Console fallback** — runs without a GUI if PyQt5 is unavailable

---

## Project Structure

```
TaleemLine/
│
├── core/                      ← business logic, no UI
│   ├── taleem_main.py         # FSM agent (TaleemAgent) — core session logic
│   ├── brain_processor.py     # Sends student text to Ollama, returns AI response
│   ├── performance_tracker.py # Records and reports per-student session history
│   └── sample_dataset.py      # Curated Q&A dataset for Math, Science, English
│
├── gui/                        ← everything visual
│   ├── ui.py                  # PyQt5 phone-shell widget (PhoneUI, PhoneShell, TTSWorker)
│   ├── dial_screen.py         # Bridges PhoneUI ↔ TaleemAgent via QThread + signals
│   └── assets/
│       └── ring.wav
│
├── io/                        ← voice in / voice out
│   ├── voice_generator.py     # Text-to-speech via pyttsx3 (offline, Windows voices)
│   └── stt_test.py            # Speech-to-text via Whisper + sounddevice
│
├── tests/                     ← all test scripts
│   ├── test_connection.py     # Quick Ollama connectivity smoke test
│  
│
├── data/                      ← auto-generated at runtime
│   └── performance_*.json
│
├── main_app.py                # Entry point — GUI / console / test modes
├── requirements.txt
├── README.md
└── .gitignore
```

---

## How It Works

```
User taps 
     │
     ▼
PhoneUI (ui.py)  ──►  DialScreen (dial_screen.py)
                              │
                              │  starts
                              ▼
                       AgentThread (QThread)
                              │
                              │  drives
                              ▼
                       TaleemAgent FSM (taleem_main.py)
                         │              │
                         ▼              ▼
                  brain_processor   stt_test / voice_generator
                  (Ollama/Llama3)   (Whisper / pyttsx3)
```

### FSM States

```
IDLE → LANG_SELECT → GRADE_SELECT → SUBJECT_SELECT → MODE_SELECT
                                                           │
                              ┌────────────────┬──────────┘
                              ▼                ▼           ▼
                       LEARNING_SESSION  TEST_SESSION  GAME_SESSION
                              └────────────────┴──────────┘
                                                  │
                                            END_SESSION
                                                  │
                                               (IDLE)
```

---

## Prerequisites

### 1. Python
Python **3.10 or higher** is required (uses `match` syntax and `X | Y` type hints).

### 2. Ollama (local LLM)
Download and install from [https://ollama.com](https://ollama.com), then pull the model:

```bash
ollama pull llama3
ollama serve          # must be running before launching TaleemLine
```

### 3. Windows TTS voices
`voice_generator.py` uses `pyttsx3` with Windows SAPI voices.  
For best Urdu/Hindi support install the **Microsoft Hazel** or **Microsoft Zira** voice  
from Windows Settings → Time & Language → Speech → Add voices.

---

## Installation

```bash
# 1. Clone or copy the project folder
cd TaleemLine

# 2. (Recommended) create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Running the App

| Command | What it does |
|---|---|
| `python main_app.py` | Launch GUI (default) |
| `python main_app.py --console` | Terminal / voice-only mode |
| `python main_app.py --test` | Check all system components |
| `python test_connection.py` | Quick Ollama ping test |

---

## Usage — GUI Mode

1. Run `python main_app.py`
2. Tap the **green ☎ button** — a ringing animation plays
3. After connecting, the agent guides you step by step:
   - Press **1** English · **2** Urdu · **3** Pashto
   - Press your **grade number** (1–9 auto-confirms; 10–12 press digits then **#**)
   - Press **1–6** for subject
   - Press **4** Learning · **5** Test · **6** Game
4. During the session:
   - Press **1** to ask a question (voice recording starts)
   - Press **0** to end the session
5. Tap **📵** at any time to hang up

---

## Usage — Console Mode

```bash
python main_app.py --console
```

Follow the numbered prompts. If the microphone fails, the agent automatically  
switches to keyboard input — just type your question and press Enter.

---

## Performance Tracking

Each session is automatically saved to `performance_<student_id>.json`.  
The default student ID is `default_student`.  
To use named profiles, instantiate `PerformanceTracker` with a custom ID:

```python
from performance_tracker import PerformanceTracker
tracker = PerformanceTracker("ali_grade5")
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Ollama is not running` | Run `ollama serve` in a terminal first |
| `No module named 'whisper'` | `pip install openai-whisper` |
| `No module named 'sounddevice'` | `pip install sounddevice scipy` |
| `No module named 'PyQt5'` | `pip install PyQt5` |
| Mic not detected | App auto-falls back to keyboard input |
| Slow first response | Llama3 loads into memory on first query — normal |
| Urdu TTS sounds wrong | Install Microsoft Hazel/Zira voice in Windows Settings |

---

## Supported Subjects & Grades

| Subject | Grades |
|---|---|
| Math | 1 – 12 |
| English | 1 – 12 |
| Science | 1 – 12 |
| Urdu | 1 – 12 |
| Physics | 9 – 12 |
| Chemistry | 9 – 12 |

---

## License

This project was built for educational purposes. Free to use and modify.