# ─────────────────────────────────────────────────────────────────────────────
#  dial_screen.py
# ─────────────────────────────────────────────────────────────────────────────
# TaleemLine – GUI ↔ Agent Bridge
#
# Purpose:
#   Connects the PyQt5 phone-shell UI (ui.py) to the FSM learning agent
#   (taleem_main.py) without blocking the Qt event loop.
#
# Key classes:
#   AgentThread  – runs TaleemAgent in a QThread; communicates with the UI
#                  exclusively through Qt signals so the GUI stays responsive.
#   DialScreen   – subclass of PhoneUI; overrides connect_call(), dial_press(),
#                  and end_call() to wire the agent thread in and out.
#
# Signal flow:
#   dial-pad key pressed
#     → DialScreen.dial_press()
#     → AgentThread.feed_digit()      (unblocks the FSM)
#     → AgentThread.agent_says        (signal → UI speaks response)
#     → AgentThread.request_input     (signal → UI shows next prompt)
#
# Imported by: main_app.py  (run_gui)
# Imports:     ui.PhoneUI, taleem_main.TaleemAgent
#
# Part of: TaleemLine Voice Learning Agent
# ─────────────────────────────────────────────────────────────────────────────

import sys
import threading
import queue

from PyQt5.QtCore  import QThread, pyqtSignal, QObject, QTimer
from PyQt5.QtWidgets import QApplication

# ── import the existing UI shell ──────────────────────────────────────────────
try:
    from ui import PhoneUI
except ImportError as e:
    raise ImportError(
        "ui.py not found – make sure ui.py is in the same directory."
    ) from e

# ── import the agent (optional – graceful fallback if deps missing) ───────────
try:
    from core.taleem_main import TaleemAgent
    AGENT_AVAILABLE = True
except ImportError:
    AGENT_AVAILABLE = False
    print("[dial_screen] WARNING: taleem_main.py or its dependencies not found.")
    print("             Running in UI-only / demo mode.")


# ══════════════════════════════════════════════════════════════════════════════
#  AgentThread  –  runs TaleemAgent FSM without blocking Qt event loop
# ══════════════════════════════════════════════════════════════════════════════

class AgentThread(QThread):
    """
    Runs the TaleemAgent FSM in a background thread.

    Signals
    -------
    agent_says(str)        – agent produced text (speak + show in prompt label)
    request_input(str)     – agent needs a digit; pass the prompt to display
    session_ended(str)     – FSM reached END_SESSION; payload = summary text
    ollama_error(str)      – Ollama not reachable
    """

    agent_says    = pyqtSignal(str)
    request_input = pyqtSignal(str)
    session_ended = pyqtSignal(str)
    ollama_error  = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._input_queue: queue.Queue = queue.Queue()
        self._abort = False

    # ── called by UI when user presses a digit ────────────────────────────────
    def feed_digit(self, digit: str):
        self._input_queue.put(digit)

    def abort(self):
        self._abort = True
        self._input_queue.put(None)   # unblock any waiting get()

    # ── helpers ───────────────────────────────────────────────────────────────
    def _speak(self, text: str):
        """Emit text to UI (non-blocking)."""
        self.agent_says.emit(text)

    def _ask(self, prompt: str) -> str:
        """
        Emit request_input, then BLOCK until UI feeds a digit back.
        Returns the digit string (or empty string if aborted).
        """
        self.request_input.emit(prompt)
        digit = self._input_queue.get()       # blocks thread (not Qt main thread)
        if digit is None or self._abort:
            return ""
        return digit

    # ── main FSM flow ─────────────────────────────────────────────────────────
    def run(self):
        """
        Mirrors the console flow in taleem_main.TaleemAgent.start_session()
        but uses signals instead of print/input/voice_generator.
        """
        if not AGENT_AVAILABLE:
            self._speak("Demo mode: TaleemAgent not available.")
            self.session_ended.emit("Install required packages to enable AI.")
            return

        # ── check Ollama ──────────────────────────────────────────────────────
        try:
            import requests as _req
            _req.get("http://localhost:11434/api/tags", timeout=3)
        except Exception:
            self.ollama_error.emit(
                "Ollama is not running. Please start Ollama and try again."
            )
            return

        agent = TaleemAgent()

        # ── STATE: IDLE → LANG_SELECT ─────────────────────────────────────────
        agent.start()

        lang_digit = self._ask(
            "Welcome to TaleemLine!\n"
            "Select language:\n1 English  2 Urdu  3 Pashto"
        )
        if not lang_digit or self._abort:
            return
        agent.language = agent.languages.get(lang_digit, "Urdu")
        agent.select_language()
        self._speak(f"Language: {agent.language}")

        # ── STATE: GRADE_SELECT ───────────────────────────────────────────────
        # Grade can be 1-12; user may press two digits (e.g. 1 then 2 → "12")
        grade_digit = ""
        self.request_input.emit(
            f"{agent.language} selected.\n"
            "Enter grade (1–12).\nPress # to confirm two-digit grades."
        )

        while True:
            if self._abort:
                return
            d = self._input_queue.get()
            if d is None or self._abort:
                return
            if d == '#':
                # confirm multi-digit grade
                break
            grade_digit += d
            if grade_digit.isdigit() and 1 <= int(grade_digit) <= 9:
                # single-digit grade: auto-confirm after one press
                break
            # show accumulated digits in prompt area (re-emit)
            self.request_input.emit(
                f"Grade so far: {grade_digit}\nPress # to confirm or keep entering."
            )

        if not grade_digit.isdigit() or not (1 <= int(grade_digit) <= 12):
            grade_digit = "5"
        agent.grade = agent.grades.get(grade_digit, "Grade 5")
        agent.select_grade()
        self._speak(f"Grade: {agent.grade}")

        # ── STATE: SUBJECT_SELECT ─────────────────────────────────────────────
        subj_digit = self._ask(
            "Choose subject:\n"
            "1 Math  2 English  3 Science\n"
            "4 Urdu  5 Physics  6 Chemistry"
        )
        if not subj_digit or self._abort:
            return
        agent.subject = agent.subjects.get(subj_digit, "Math")
        agent.select_subject()
        self._speak(f"Subject: {agent.subject}")

        # ── STATE: MODE_SELECT ────────────────────────────────────────────────
        mode_digit = self._ask(
            "Choose mode:\n"
            "4 Learning  5 Test  6 Game"
        )
        if not mode_digit or self._abort:
            return

        if mode_digit == '5':
            agent.select_test()
            agent.mode = 'Test'
        elif mode_digit == '6':
            agent.select_game()
            agent.mode = 'Game'
        else:
            agent.select_learning()
            agent.mode = 'Learning'

        self._speak(f"Mode: {agent.mode}")

        # ── STATE: Active session ─────────────────────────────────────────────
        greeting = agent.get_greeting()
        self._speak(greeting)

        # In voice-session state the dial-pad is repurposed:
        #   pressing any digit triggers a voice recording via stt_test,
        #   OR the user can type via the OS keyboard (fallback in stt_test).
        # We notify UI to switch dial-pad into "voice mode" prompt.
        self.request_input.emit(
            "Session active!\n"
            "Press 1 to ask a question.\nPress 0 to end session."
        )

        while not self._abort:
            d = self._input_queue.get()
            if d is None or self._abort:
                break
            if d == '0':
                break

            # Get student's voice/text input
            self._speak("Listening…")
            try:
                student_text = agent.get_student_input()
            except Exception as exc:
                student_text = ""
                self._speak(f"Mic error: {exc}")

            if not student_text.strip():
                self.request_input.emit(
                    "Didn't catch that.\nPress 1 to try again  0 to end."
                )
                continue

            # Check end keywords
            end_words = ['bye', 'allah', 'khuda', 'end', 'stop',
                         'bas', 'theek hai', 'quit']
            if any(w in student_text.lower() for w in end_words):
                break

            # Send to Ollama
            self._speak("Thinking…")
            try:
                response = agent.process_with_ollama(student_text)
            except Exception as exc:
                response = f"Error: {exc}"

            agent.total_questions += 1
            self._speak(response)

            if agent.mode == 'Test':
                if any(w in response.lower()
                       for w in ['correct', 'sahi', 'theek', 'right']):
                    agent.score += 1

            self.request_input.emit(
                "Press 1 to ask another question.\nPress 0 to end session."
            )

        # ── STATE: END_SESSION ────────────────────────────────────────────────
        if not self._abort:
            agent.end_session()
            summary = agent.get_summary()
            agent.reset()
            self.session_ended.emit(summary)


# ══════════════════════════════════════════════════════════════════════════════
#  DialScreen  –  subclass of PhoneUI that wires the agent thread
# ══════════════════════════════════════════════════════════════════════════════

class DialScreen(PhoneUI):
    """
    Drop-in replacement for the plain PhoneUI.
    Overrides connect_call() and end_call() to attach AgentThread.

    main_app.py does:
        from dial_screen import DialScreen
        window = DialScreen()
    """

    def __init__(self):
        super().__init__()
        self._agent_thread: AgentThread | None = None

    # ── override: called after ringing animation completes ────────────────────
    def connect_call(self):
        """Start the agent thread instead of just speaking a static prompt."""
        self._stop_ringtone()
        self.stacked.setCurrentIndex(2)   # show call screen
        self.state = "AGENT_RUNNING"
        self.digit_buffer = ""
        self.buffer_label.setText("")

        # ── wire up a fresh agent thread ──────────────────────────────────────
        self._agent_thread = AgentThread(self)
        self._agent_thread.agent_says.connect(self._on_agent_says)
        self._agent_thread.request_input.connect(self._on_request_input)
        self._agent_thread.session_ended.connect(self._on_session_ended)
        self._agent_thread.ollama_error.connect(self._on_ollama_error)
        self._agent_thread.start()

    # ── override: intercept dial-pad presses and route to agent ───────────────
    def dial_press(self):
        """Forward pressed digit to agent thread (instead of local FSM)."""
        if self.state != "AGENT_RUNNING":
            # fall back to original behaviour for non-agent states
            super().dial_press()
            return

        btn = self.sender()
        if btn is None:
            return
        digit = btn.text()
        # Only forward numeric digits (ignore *, #, 0 special handling above)
        self.digit_buffer = digit
        self.buffer_label.setText(digit)
        QTimer.singleShot(300, lambda: self.buffer_label.setText(""))

        if self._agent_thread and self._agent_thread.isRunning():
            self._agent_thread.feed_digit(digit)

    # ── override: clean up agent thread on hang-up ────────────────────────────
    def end_call(self):
        """Abort agent thread, then delegate to original end_call."""
        if self._agent_thread and self._agent_thread.isRunning():
            self._agent_thread.abort()
            self._agent_thread.wait(3000)   # give it 3 s to finish
        self._agent_thread = None
        super().end_call()

    # ── agent signal handlers (run on Qt main thread) ─────────────────────────
    def _on_agent_says(self, text: str):
        """Agent produced output – update label and speak via TTS."""
        self.speak(text)   # PhoneUI.speak() → prompt_label + TTSWorker

    def _on_request_input(self, prompt: str):
        """Agent is waiting for a digit – show the prompt."""
        self.prompt_label.setText(prompt)
        self.tts.speak(prompt)

    def _on_session_ended(self, summary: str):
        """FSM finished – speak summary then return to idle after 4 s."""
        self.speak(summary)
        QTimer.singleShot(4000, self.end_call)

    def _on_ollama_error(self, msg: str):
        """Ollama not running – show error and hang up."""
        self.speak(msg)
        QTimer.singleShot(5000, self.end_call)


# ── standalone entry (optional) ───────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DialScreen()
    window.show()
    sys.exit(app.exec_())