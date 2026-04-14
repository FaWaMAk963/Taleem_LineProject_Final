# Converts AI response to voice using pyttsx3
# TEXT → SPEECH (100% Offline - uses Windows built-in voices)

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
        
        # Try to select a good voice (Windows usually has Hindi/Urdu compatible voices)
        voices = engine.getProperty('voices')
        for voice in voices:
            # Look for a voice that supports Urdu/Hindi (usually Microsoft Hazel or Zira)
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
    speak_response("Assalam-o-Alaikum! Main aapki ustad hoon.")
    print("Test complete!")