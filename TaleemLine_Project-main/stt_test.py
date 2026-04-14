# Converts live microphone input into text using Whisper
# SPEECH → TEXT

def record_audio(filename="user_input.wav", duration=5, fs=44100):
    """Record audio from microphone"""
    try:
        import sounddevice as sd
        from scipy.io.wavfile import write
        
        print("🎤 Speak now...")
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        write(filename, fs, audio)
        print(f"--- Audio saved as {filename} ---")
        return filename
        
    except ImportError:
        print("ERROR: sounddevice not installed. Run: pip install sounddevice scipy")
        return None
    except Exception as e:
        print(f"ERROR recording audio: {e}")
        return None


def recognize_speech(duration=5):
    """Main function: Record audio and convert to text"""
    import os
    
    # Step 1: Record from user
    audio_path = record_audio(duration=duration)
    
    if audio_path is None or not os.path.exists(audio_path):
        print("No audio recorded. Returning empty text.")
        return ""
    
    # Step 2: Load Whisper and transcribe
    try:
        import whisper
        print(f"--- Transcribing: {audio_path} ---")
        
        # Load model
        model = whisper.load_model("small")
        
        # Transcribe in Urdu
        result = model.transcribe(
            audio_path,
            language="ur",
            task="transcribe",
            initial_prompt="یہ اردو زبان میں تعلیمی گفتگو ہے"
        )
        
        captured_text = result["text"]
        print(f"--- Heard: {captured_text} ---")
        
        # Step 3: Save result
        with open("transcription.txt", "w", encoding="utf-8") as f:
            f.write(captured_text)
        
        return captured_text
        
    except ImportError:
        print("ERROR: whisper not installed. Run: pip install openai-whisper")
        return ""
    except Exception as e:
        print(f"ERROR transcribing: {e}")
        return ""


def recognize_speech_text_input():
    """Fallback: Get text input from keyboard instead of microphone"""
    print("\n⌨️  (Type your question and press Enter)")
    text = input("Student: ")
    
    # Save to file
    with open("transcription.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"--- Input: {text} ---")
    return text


if __name__ == "__main__":
    # Test with microphone
    result = recognize_speech()
    if result:
        print(f"Result: {result}")
    else:
        print("Microphone failed. Use keyboard input instead.")