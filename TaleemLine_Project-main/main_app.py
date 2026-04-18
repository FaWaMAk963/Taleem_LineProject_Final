# ─────────────────────────────────────────────────────────────────────────────
#  main_app.py
# ─────────────────────────────────────────────────────────────────────────────
# TaleemLine – Application Entry Point
#
# Purpose:
#   Single launch file for all run modes. Parses CLI arguments and delegates
#   to the correct mode. No business logic lives here.
#
# Run modes:
#   python main_app.py            →  GUI  (DialScreen phone shell)
#   python main_app.py --console  →  Terminal / voice-only mode
#   python main_app.py --test     →  System component smoke-test
#
# Dependencies loaded here:
#   PyQt5          (GUI mode only)
#   dial_screen    (GUI mode only)
#   taleem_main    (console mode only)
#
# Part of: TaleemLine Voice Learning Agent
# ─────────────────────────────────────────────────────────────────────────────


import sys
import argparse


# ══════════════════════════════════════════════════════════════════════════════
#  GUI mode
# ══════════════════════════════════════════════════════════════════════════════

def run_gui():
    """Launch the phone-shell GUI with TaleemAgent wired in."""
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
    except ImportError:
        print("PyQt5 not found.")
        print("    Run:  pip install PyQt5")
        print("\nFalling back to console mode…\n")
        run_console()
        return

    try:
        from dial_screen import DialScreen
    except ImportError as e:
        print(f"Could not import DialScreen: {e}")
        print("    Make sure dial_screen.py and ui.py are in the same folder.")
        print("\nFalling back to console mode…\n")
        run_console()
        return

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # High-DPI support (PyQt5)
    try:
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps,    True)
    except AttributeError:
        pass   # older Qt versions may not have these

    window = DialScreen()
    window.setWindowTitle("TaleemLine")
    window.show()

    sys.exit(app.exec_())


# ══════════════════════════════════════════════════════════════════════════════
#  Console mode
# ══════════════════════════════════════════════════════════════════════════════

def run_console():
    """Run TaleemAgent in the terminal (voice + keyboard fallback)."""
    try:
        from taleem_main import TaleemAgent
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("\nInstall all required packages:")
        print("  pip install PyQt5 sounddevice scipy openai-whisper "
              "gtts playsound requests transitions")
        sys.exit(1)

    agent = TaleemAgent()
    agent.start_session()


# ══════════════════════════════════════════════════════════════════════════════
#  System test
# ══════════════════════════════════════════════════════════════════════════════

def test_system():
    """Quick smoke-test for every major component."""
    print("\n" + "=" * 50)
    print("   TaleemLine – System Component Test")
    print("=" * 50)

    results = {}

    # ── 1. Ollama ─────────────────────────────────────────────────────────────
    print("\n[1] Ollama (LLM backend)")
    try:
        import requests
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3", "prompt": "Say hello in Urdu", "stream": False},
            timeout=30,
        )
        snippet = r.json().get("response", "")[:60]
        print(f"     Response: {snippet}…")
        results["Ollama"] = "OK"
    except Exception as e:
        print(f"     {e}")
        results["Ollama"] = "FAIL"

    # ── 2. brain_processor ────────────────────────────────────────────────────
    print("\n[2] brain_processor")
    try:
        import brain_processor
        print("      Imported successfully")
        results["brain_processor"] = "OK"
    except ImportError as e:
        print(f"      {e}")
        results["brain_processor"] = "FAIL"

    # ── 3. Text-to-Speech ─────────────────────────────────────────────────────
    print("\n[3] Text-to-Speech (voice_generator)")
    try:
        import voice_generator
        voice_generator.speak_response("TaleemLine test")
        print("      TTS working")
        results["TTS"] = "OK"
    except Exception as e:
        print(f"      {e}")
        results["TTS"] = "FAIL"

    # ── 4. Speech-to-Text ─────────────────────────────────────────────────────
    print("\n[4] Speech-to-Text (stt_test)")
    try:
        import stt_test        # noqa: F401
        print("      Module imported (live mic test skipped)")
        results["STT"] = "OK"
    except Exception as e:
        print(f"      {e}")
        results["STT"] = "FAIL"

    # ── 5. PyQt5 ──────────────────────────────────────────────────────────────
    print("\n[5] PyQt5 (GUI)")
    try:
        from PyQt5.QtWidgets import QApplication   # noqa: F401
        print("     PyQt5 available")
        results["PyQt5"] = "OK"
    except ImportError as e:
        print(f"   ❌   {e}")
        results["PyQt5"] = "FAIL"

    # ── 6. dial_screen / ui ───────────────────────────────────────────────────
    print("\n[6] dial_screen + ui")
    try:
        from dial_screen import DialScreen   # noqa: F401
        print("      DialScreen imported")
        results["DialScreen"] = "OK"
    except Exception as e:
        print(f"    ❌  {e}")
        results["DialScreen"] = "FAIL"

    # ── 7. FSM (transitions) ──────────────────────────────────────────────────
    print("\n[7] FSM (transitions library)")
    try:
        from taleem_main import TaleemAgent
        agent = TaleemAgent()
        agent.start()                  # IDLE → LANG_SELECT
        assert agent.state == "LANG_SELECT"
        print("      FSM transitions working")
        results["FSM"] = "OK"
    except Exception as e:
        print(f"    ❌  {e}")
        results["FSM"] = "FAIL"

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("Results:")
    for component, status in results.items():
        icon = "✅" if status == "OK" else "❌"
        print(f"  {icon}  {component}: {status}")

    failed = [k for k, v in results.items() if v != "OK"]
    if failed:
        print(f"\n⚠️  {len(failed)} component(s) need attention: {', '.join(failed)}")
    else:
        print("\n🎉  All components OK! Run  python main_app.py  to start.")
    print("=" * 50 + "\n")


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="main_app.py",
        description="TaleemLine – AI-powered Voice Learning Agent",
    )
    parser.add_argument(
        "--console", action="store_true",
        help="Run in terminal / console mode (no GUI)",
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Run system component checks and exit",
    )
    args = parser.parse_args()

    if args.test:
        test_system()
    elif args.console:
        run_console()
    else:
        run_gui()