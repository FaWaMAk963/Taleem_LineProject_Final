import sys
import numpy as np
import pyttsx3
import sounddevice as sd
from scipy.io.wavfile import write
from playsound import playsound
import threading

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QGridLayout, QVBoxLayout, QApplication
)
from PyQt6.QtCore import Qt, QTimer


class CallScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedSize(290, 600)

        self.stage = "language"
        self.call_active = True   # 🔴 control call loop

        self.init_ui()
        self.start_ringing()

    # -------------------------
    # UI
    # -------------------------
    def init_ui(self):

        self.setStyleSheet("background-color: black;")

        layout = QVBoxLayout()

        self.title = QLabel("TaleemLine")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")

        self.status = QLabel("Ringing...")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("color: green; font-size: 18px;")

        self.timer = QLabel("")
        self.timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer.setStyleSheet("color: white;")

        layout.addWidget(self.title)
        layout.addWidget(self.status)
        layout.addWidget(self.timer)

        self.pad = self.create_dial_pad()
        self.pad.setVisible(False)
        layout.addWidget(self.pad)

        # 🔴 END CALL BUTTON
        self.end_btn = QPushButton("End Call")
        self.end_btn.setStyleSheet("background-color: red; color: white; font-size: 16px;")
        self.end_btn.clicked.connect(self.end_call)
        self.end_btn.setVisible(False)

        layout.addWidget(self.end_btn)

        self.setLayout(layout)

    # -------------------------
    # RINGING
    # -------------------------
    def start_ringing(self):

        self.ringing = True

        def play_ring():
            while self.ringing:
                playsound("ring.mp3")

        threading.Thread(target=play_ring, daemon=True).start()

        QTimer.singleShot(8000, self.connect_call)

    # -------------------------
    def connect_call(self):

        self.ringing = False   # 🔥 STOP ringing immediately

        self.status.setText("📡 Connected")
        self.timer.setText("00:00")

        self.pad.setVisible(True)
        self.end_btn.setVisible(True)

        self.seconds = 0
        self.call_timer = QTimer()
        self.call_timer.timeout.connect(self.update_timer)
        self.call_timer.start(1000)

        self.play_ivr_stage_1()

    # -------------------------
    def update_timer(self):
        self.seconds += 1
        self.timer.setText(f"{self.seconds//60:02d}:{self.seconds%60:02d}")

    # -------------------------
    def play_ivr_stage_1(self):

        text = "Press 1 for English, 2 for Urdu, 3 for Pashto"
        self.status.setText("Select Language (1-3)")

        threading.Thread(target=self.speak, args=(text,), daemon=True).start()


    def play_ivr_stage_2(self):

        text = "Press 4 for Learning, 5 for Test, 6 for Game"
        self.status.setText("Select Mode (4-6)")

        threading.Thread(target=self.speak, args=(text,), daemon=True).start()

    # -------------------------
    def create_dial_pad(self):

        widget = QWidget()
        grid = QGridLayout()

        nums = ["1","2","3","4","5","6","7","8","9"]

        for i, num in enumerate(nums):
            btn = QPushButton(num)
            btn.setFixedSize(70, 70)
            btn.setStyleSheet("background:#222; color:white; font-size:18px;")
            btn.clicked.connect(lambda _, n=num: self.handle_input(n))
            grid.addWidget(btn, i//3, i%3)

        widget.setLayout(grid)
        return widget

    # -------------------------
    def handle_input(self, value):

        if self.stage == "language":
            if value in ["1","2","3"]:
                self.stage = "mode"
                self.play_ivr_stage_2()

        elif self.stage == "mode":
            if value in ["4","5","6"]:
                self.stage = "conversation"
                self.start_conversation()

    # -------------------------
    # SPEAK
    # -------------------------
    def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    # -------------------------
    # 🎤 SMART RECORD (SILENCE DETECTION)
    # -------------------------
    def record_until_silence(self, filename="user.wav", fs=16000):

        self.status.setText("🎤 Listening...")

        silence_threshold = 0.01
        silence_duration = 2  # seconds
        max_duration = 10     # 🔥 MAX LIMIT

        chunk = 1024
        audio = []
        silent_chunks = 0

        max_silent_chunks = int(silence_duration * fs / chunk)
        max_chunks = int(max_duration * fs / chunk)

        stream = sd.InputStream(samplerate=fs, channels=1, blocksize=chunk)
        stream.start()

        print("🎤 Listening (auto stop OR 10s max)...")

        for i in range(max_chunks):

            if not self.call_active:
                break

            data, _ = stream.read(chunk)
            audio.append(data)

            volume = np.linalg.norm(data)

            if volume < silence_threshold:
                silent_chunks += 1
            else:
                silent_chunks = 0

        # 🔥 STOP if silence detected
            if silent_chunks > max_silent_chunks:
                print("⏹️ Stopped due to silence")
                break

        stream.stop()

        audio = np.concatenate(audio)
        write(filename, fs, audio)

        print("✅ Recording saved")
        return filename

    # -------------------------
    # START CONVERSATION LOOP
    # -------------------------
    def start_conversation(self):

        threading.Thread(target=self.conversation_loop, daemon=True).start()

    def conversation_loop(self):

        welcome = "Welcome to TaleemLine, mein aap ki kesay madad karoon"
        self.speak(welcome)

        while self.call_active:

            audio = self.record_until_silence()

            try:
                import taleem_main
                response = taleem_main.process(audio)
                print("🤖:", response)

                if response:
                    self.speak(response)

            except Exception as e:
                print("❌ Error:", e)

    # -------------------------
    # END CALL
    # -------------------------
    def end_call(self):

        self.call_active = False
        self.status.setText("📴 Call Ended")
        self.pad.setVisible(False)
        self.end_btn.setVisible(False)


# -------------------------
if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = CallScreen()
    window.show()
    sys.exit(app.exec())