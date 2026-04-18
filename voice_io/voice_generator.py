# ─────────────────────────────────────────────────────────────────────────────
# FILE: voice_generator.py
# ─────────────────────────────────────────────────────────────────────────────
# TaleemLine – Text-to-Speech (Offline)
#
# Purpose:
#   Converts any text string to spoken audio using pyttsx3, which wraps the
#   platform's built-in TTS engine (Windows SAPI / macOS NSSpeech / eSpeak).
#   No network calls — fully offline.
#
# Key function:
#   speak_response(text)
#     • Initialises a pyttsx3 engine, sets rate (160 wpm) and volume (1.0).
#     • Prefers Microsoft Hazel / Zira / Hindi voices for Urdu-friendly output.
#     • Prints the text as fallback if pyttsx3 is unavailable.
#
# Note:
#   In GUI mode, pyttsx3 is also used inside ui.TTSWorker (background thread).
#   This module is used directly in console mode and by taleem_main.speak().
#
# Imported by: taleem_main.TaleemAgent (console mode), ui.TTSWorker
#
# Part of: TaleemLine Voice Learning Agent
# ─────────────────────────────────────────────────────────────────────────────


def speak_response(text):
    """Convert text to speech and play it"""
    if not text or len(text) < 2:
        return
        
    try:
        import pyttsx3
        
        print("--- Generating Voice ---")
        
        # Initialize engine
        engine = pyttsx3.init()
        
        # Set properties for a friendly teacher voice
        engine.setProperty('rate', 160)  # Speed (lower = slower/clearer)
        engine.setProperty('volume', 1.0)  # Max volume
  
        voices = engine.getProperty('voices')
        for voice in voices:
           
            if 'hazel' in voice.name.lower() or 'zira' in voice.name.lower() or 'hindi' in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
                
        # Speak the text
        engine.say(text)
        engine.runAndWait()
        
    except ImportError:
        print("ERROR: pyttsx3 not installed.")
        print("Please run: pip install pyttsx3")
        print(f"[Text Response]: {text}")
    except Exception as e:
        print(f"Speech error: {e}")
        print(f"[Text Response]: {text}")


if __name__ == "__main__":
    
    print("Testing voice...")
    speak_response("Mein app ki ustaad taleemLine hoon!")
    print("Test complete!")