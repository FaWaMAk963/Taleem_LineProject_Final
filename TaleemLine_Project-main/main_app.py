# Main Application Entry Point
# Integrates UI with Ollama backend

import sys


def run_gui():
    """Run with Phone UI"""
    try:
        from PyQt6.QtWidgets import QApplication
        from dial_screen import DialScreen
        
        app = QApplication(sys.argv)
        window = DialScreen()
        window.show()
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"GUI Error: {e}")
        print("Run: pip install PyQt6")
        print("\nFalling back to console mode...\n")
        run_console()


def run_console():
    """Run in Console Mode (no GUI)"""
    try:
        import taleem_main
        agent = taleem_main.TaleemAgent()
        agent.start_session()
    except ImportError as e:
        print(f"Missing: {e}")
        print("\nInstall all packages:")
        print("pip install PyQt6 sounddevice scipy whisper gtts playsound requests transitions")


def test_system():
    """Test Ollama connection"""
    print("Testing TaleemLine System...\n")
    
    # Test 1: Ollama
    print("1. Testing Ollama...")
    try:
        import requests
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": "Say hello in Urdu", "stream": False},
            timeout=30
        )
        print(f"   ✅ Ollama: {r.json().get('response', '')[:50]}...")
    except Exception as e:
        print(f"   ❌ Ollama Error: {e}")
    
    # Test 2: TTS
    print("\n2. Testing Text-to-Speech...")
    try:
        import voice_generator
        voice_generator.speak_response("Test")
        print("   ✅ TTS Working")
    except Exception as e:
        print(f"   ❌ TTS Error: {e}")
    
    # Test 3: STT
    print("\n3. Testing Speech-to-Text...")
    try:
        import stt_test
        print("   ⚠️ STT requires microphone (will test when recording)")
    except Exception as e:
        print(f"   ❌ STT Error: {e}")
    
    print("\n" + "="*40)
    print("Test complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TaleemLine - Voice Learning Agent")
    parser.add_argument('--console', action='store_true', help='Console mode (no GUI)')
    parser.add_argument('--test', action='store_true', help='Test system components')
    
    args = parser.parse_args()
    
    if args.test:
        test_system()
    elif args.console:
        run_console()
    else:
        run_gui()