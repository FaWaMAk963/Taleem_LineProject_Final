
# ─────────────────────────────────────────────────────────────────────────────
# ui.py
# ─────────────────────────────────────────────────────────────────────────────
# TaleemLine – Phone Shell UI
#
# Purpose:
#   Provides all PyQt5 visual components. Renders a realistic mobile phone
#   chassis with three screens: Idle, Ringing, and Active Call.
#   Contains NO business logic — all session decisions live in dial_screen.py.
#
# Key classes:
#   PhoneShell  – draws the phone body (chassis, camera notch, buttons) via
#                 paintEvent using QPainter gradients and rounded rects.
#   TTSWorker   – queues pyttsx3 speech in a background thread so TTS never
#                 freezes the UI.
#   PhoneUI     – main widget; hosts the QStackedWidget with all three screens,
#                 the dial-pad grid, and a basic local state machine for the
#                 selection flow (overridden by DialScreen in GUI+agent mode).
#
# Screens:
#   0 – Idle       (avatar, "Tap to call" button)
#   1 – Ringing    (animated pulse rings, cancel button)
#   2 – Active     (prompt label, digit buffer display, dial-pad, hang-up)
#
# Imported by: dial_screen.py
#
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os
import threading
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QFrame, QStackedWidget, QGridLayout,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QUrl, QSize, pyqtSignal, QObject
from PyQt5.QtGui import QColor, QFont, QPainter, QLinearGradient, QPen, QBrush, QRadialGradient
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import pyttsx3


# ── TTS worker: run blocking speak() in a background thread ──────────────────
class TTSWorker(QObject):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 145)
        self.engine.setProperty('volume', 0.95)
        self._queue = []
        self._running = False

    def speak(self, text):
        """Queue text; starts worker thread if not already running."""
        self._queue.append(text)
        if not self._running:
            self._flush()

    def _flush(self):
        if not self._queue:
            self._running = False
            self.finished.emit()
            return
        self._running = True
        text = self._queue.pop(0)
        t = threading.Thread(target=self._do_speak, args=(text,), daemon=True)
        t.start()

    def _do_speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
        # schedule next chunk on main thread via zero-delay timer trick
        QTimer.singleShot(0, self._flush)


# ── Decorative phone-case widget ──────────────────────────────────────────────
class PhoneShell(QFrame):
    """Draws a realistic phone shell: chassis, camera, speaker, buttons."""

    SHELL_W  = 440
    SHELL_H  = 900
    CORNER_R = 56
    SCREEN_W = 360
    SCREEN_H = 720
    SCREEN_X = 40          # (SHELL_W - SCREEN_W) // 2
    SCREEN_Y = 90

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.SHELL_W, self.SHELL_H)
        # drop shadow for the whole phone
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(60)
        shadow.setOffset(0, 18)
        shadow.setColor(QColor(0, 0, 0, 130))
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        W, H, R = self.SHELL_W, self.SHELL_H, self.CORNER_R

        # ── Chassis body ─────────────────────────────────────────────────────
        chassis_grad = QLinearGradient(0, 0, W, H)
        chassis_grad.setColorAt(0.00, QColor("#1a1a2e"))
        chassis_grad.setColorAt(0.35, QColor("#16213e"))
        chassis_grad.setColorAt(0.70, QColor("#0f3460"))
        chassis_grad.setColorAt(1.00, QColor("#1a1a2e"))
        p.setBrush(QBrush(chassis_grad))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(0, 0, W, H, R, R)

        # ── Edge highlight (simulated metal rim) ─────────────────────────────
        rim_pen = QPen(QColor(255, 255, 255, 35))
        rim_pen.setWidth(2)
        p.setPen(rim_pen)
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(1, 1, W-2, H-2, R-1, R-1)

        # ── Screen cutout (slightly recessed look) ────────────────────────────
        # Outer bezel glow
        bezel_pen = QPen(QColor(255, 255, 255, 18))
        bezel_pen.setWidth(3)
        p.setPen(bezel_pen)
        p.setBrush(QColor(0, 0, 0))
        sx, sy = self.SCREEN_X, self.SCREEN_Y
        sw, sh = self.SCREEN_W, self.SCREEN_H
        p.drawRoundedRect(sx-2, sy-2, sw+4, sh+4, 24, 24)

        # ── Front camera (pill notch area) ────────────────────────────────────
        notch_x = W//2 - 55
        notch_y = sy - 44
        # Notch pill
        p.setBrush(QColor(10, 10, 18))
        p.setPen(QPen(QColor(255,255,255,15), 1))
        p.drawRoundedRect(notch_x, notch_y, 110, 28, 14, 14)

        # Camera lens
        p.setBrush(QColor(20, 20, 35))
        p.setPen(QPen(QColor(255,255,255,30), 1))
        p.drawEllipse(notch_x + 70, notch_y + 5, 18, 18)
        # Lens inner ring
        p.setBrush(QColor(5, 5, 15))
        p.setPen(Qt.NoPen)
        p.drawEllipse(notch_x + 73, notch_y + 8, 12, 12)
        # Lens glint
        p.setBrush(QColor(255, 255, 255, 80))
        p.drawEllipse(notch_x + 77, notch_y + 10, 4, 4)
        # Speaker grille (dots)
        for i in range(7):
            p.setBrush(QColor(255,255,255,50))
            p.drawEllipse(notch_x + 8 + i*7, notch_y + 10, 3, 3)

        # ── Bottom chin ───────────────────────────────────────────────────────
        # Home indicator bar
        bar_x = W//2 - 55
        bar_y = sy + sh + 24
        p.setBrush(QColor(255, 255, 255, 60))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(bar_x, bar_y, 110, 5, 3, 3)

        # ── Side buttons ─────────────────────────────────────────────────────
        # Power button (right side)
        p.setBrush(QColor(255,255,255,20))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(W-6, 240, 6, 80, 3, 3)

        # Volume buttons (left side)
        p.drawRoundedRect(0, 200, 6, 55, 3, 3)
        p.drawRoundedRect(0, 270, 6, 55, 3, 3)

        p.end()


# ── Main phone UI ─────────────────────────────────────────────────────────────
class PhoneUI(QWidget):
    def __init__(self):
        super().__init__()
        self.tts = TTSWorker()
        self.init_ui()
        self.init_audio()
        self.state = "IDLE"
        self.selected_lang = None
        self.selected_grade = None
        self.selected_subject = None
        self.digit_buffer = ""
        self.grade_timer = QTimer()
        self.grade_timer.setSingleShot(True)
        self.grade_timer.timeout.connect(self.submit_grade)
        self.show_idle_screen()

    # ── Window / layout ───────────────────────────────────────────────────────
    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        shell_w = PhoneShell.SHELL_W
        shell_h = PhoneShell.SHELL_H
        self.setFixedSize(shell_w + 40, shell_h + 40)   # padding for shadow

        outer = QVBoxLayout()
        outer.setContentsMargins(20, 20, 20, 20)
        self.setLayout(outer)

        self.shell = PhoneShell(self)

        # The stacked screens sit inside the screen area of the shell
        self.stacked = QStackedWidget(self.shell)
        sx = PhoneShell.SCREEN_X
        sy = PhoneShell.SCREEN_Y
        sw = PhoneShell.SCREEN_W
        sh = PhoneShell.SCREEN_H
        self.stacked.setGeometry(sx, sy, sw, sh)
        self.stacked.setStyleSheet("background: #0d0d1a; border-radius: 22px;")

        self.idle_screen    = self.create_idle_screen()
        self.ringing_screen = self.create_ringing_screen()
        self.call_screen    = self.create_call_screen()
        self.stacked.addWidget(self.idle_screen)
        self.stacked.addWidget(self.ringing_screen)
        self.stacked.addWidget(self.call_screen)

        outer.addWidget(self.shell)
        self.drag_pos = None

    # ── Screen builders ───────────────────────────────────────────────────────
    def _avatar(self, size=110, font=42):
        av = QFrame()
        av.setFixedSize(size, size)
        r = size // 2
        av.setStyleSheet(f"""
            QFrame {{
                background: qradialgradient(cx:0.4,cy:0.3,radius:0.7,
                    fx:0.4,fy:0.3, stop:0 #4fc3f7, stop:1 #0277bd);
                border-radius: {r}px;
                border: 2px solid rgba(255,255,255,0.25);
            }}
        """)
        lbl = QLabel("TL", av)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setGeometry(0, 0, size, size)
        lbl.setStyleSheet(f"color: white; font-size: {font}px; font-weight: 700; background: transparent;")
        return av

    def create_idle_screen(self):
        screen = QWidget()
        screen.setStyleSheet("background: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setContentsMargins(24, 50, 24, 40)

        layout.addWidget(self._avatar(), 0, Qt.AlignCenter)

        name = QLabel("TaleemLine")
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: 1px; background: transparent;")
        layout.addWidget(name)

        num = QLabel("Helpline · 17")
        num.setAlignment(Qt.AlignCenter)
        num.setStyleSheet("color: rgba(255,255,255,0.45); font-size: 14px; background: transparent;")
        layout.addWidget(num)

        # status dots
        dot_row = QHBoxLayout()
        dot_row.setSpacing(6)
        dot_row.addStretch()
        for color in ["#4caf50", "#4fc3f7", "#ff9800"]:
            d = QFrame()
            d.setFixedSize(8, 8)
            d.setStyleSheet(f"background:{color}; border-radius:4px;")
            dot_row.addWidget(d)
        dot_row.addStretch()
        layout.addLayout(dot_row)

        layout.addStretch()

        # call button – glowing green circle
        call_btn = QPushButton("📞")
        call_btn.setFixedSize(80, 80)
        call_btn.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5,cy:0.4,radius:0.6,
                    fx:0.5,fy:0.4, stop:0 #66bb6a, stop:1 #2e7d32);
                color: white; font-size: 32px;
                border-radius: 40px;
                border: 3px solid rgba(255,255,255,0.25);
            }
            QPushButton:hover  { background: #4caf50; }
            QPushButton:pressed{ background: #1b5e20; }
        """)
        call_btn.clicked.connect(self.make_call)
        layout.addWidget(call_btn, 0, Qt.AlignCenter)

        hint = QLabel("Tap to call")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: rgba(255,255,255,0.3); font-size: 12px; background:transparent;")
        layout.addWidget(hint)

        screen.setLayout(layout)
        return screen

    def create_ringing_screen(self):
        screen = QWidget()
        screen.setStyleSheet("background: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(24, 50, 24, 40)

        layout.addWidget(self._avatar(), 0, Qt.AlignCenter)

        name = QLabel("TaleemLine")
        name.setAlignment(Qt.AlignCenter)
        name.setStyleSheet("color:#ffffff; font-size:28px; font-weight:700; background:transparent;")
        layout.addWidget(name)

        num = QLabel("17")
        num.setAlignment(Qt.AlignCenter)
        num.setStyleSheet("color:rgba(255,255,255,0.45); font-size:14px; background:transparent;")
        layout.addWidget(num)

        self.ringing_status = QLabel("Calling…")
        self.ringing_status.setAlignment(Qt.AlignCenter)
        self.ringing_status.setStyleSheet("""
            color: #4fc3f7; font-size: 15px; font-weight: 600;
            letter-spacing: 2px; background: transparent;
        """)
        layout.addWidget(self.ringing_status)

        # animated ring rings
        ring_frame = QWidget()
        ring_frame.setFixedSize(200, 200)
        ring_frame.setStyleSheet("background: transparent;")
        self.ring_anim_state = 0
        self.ring_labels = []
        for i in range(3):
            rl = QLabel(ring_frame)
            size = 80 + i * 34
            offset = (200 - size) // 2
            rl.setGeometry(offset, offset, size, size)
            alpha = 80 - i * 22
            rl.setStyleSheet(f"""
                border-radius:{size//2}px;
                border: 2px solid rgba(79,195,247,{alpha});
                background: transparent;
            """)
            self.ring_labels.append(rl)
        layout.addWidget(ring_frame, 0, Qt.AlignCenter)

        self.ring_timer = QTimer()
        self.ring_timer.timeout.connect(self._pulse_rings)
        self.ring_timer.start(600)

        layout.addStretch()

        # end button while ringing
        end_btn = QPushButton("✕")
        end_btn.setFixedSize(70, 70)
        end_btn.setStyleSheet("""
            QPushButton {
                background:#c62828; color:white; font-size:26px;
                border-radius:35px; border:none;
            }
            QPushButton:hover  { background:#e53935; }
            QPushButton:pressed{ background:#b71c1c; }
        """)
        end_btn.clicked.connect(self.end_call)
        layout.addWidget(end_btn, 0, Qt.AlignCenter)

        screen.setLayout(layout)
        return screen

    def _pulse_rings(self):
        opacities = [
            [80, 55, 30],
            [30, 80, 55],
            [55, 30, 80],
        ]
        state = self.ring_anim_state % 3
        for i, rl in enumerate(self.ring_labels):
            size = 80 + i * 34
            alpha = opacities[state][i]
            rl.setStyleSheet(f"""
                border-radius:{size//2}px;
                border: 2px solid rgba(79,195,247,{alpha});
                background: transparent;
            """)
        self.ring_anim_state += 1

    def create_call_screen(self):
        screen = QWidget()
        screen.setStyleSheet("background: transparent;")
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(16, 20, 16, 16)

        # ── Contact strip ──────────────────────────────────────────────────────
        top = QHBoxLayout()
        top.setSpacing(12)
        top.addWidget(self._avatar(60, 24))
        info = QVBoxLayout()
        n = QLabel("TaleemLine")
        n.setStyleSheet("color:#fff; font-size:18px; font-weight:700; background:transparent;")
        s = QLabel("Connected · 17")
        s.setStyleSheet("color:rgba(255,255,255,0.4); font-size:12px; background:transparent;")
        info.addWidget(n)
        info.addWidget(s)
        top.addLayout(info)
        top.addStretch()
        layout.addLayout(top)

        # ── Prompt display ─────────────────────────────────────────────────────
        self.prompt_label = QLabel("Welcome")
        self.prompt_label.setAlignment(Qt.AlignCenter)
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setStyleSheet("""
            color: rgba(255,255,255,0.75);
            font-size: 13px;
            background: rgba(255,255,255,0.06);
            border-radius: 12px;
            padding: 10px 14px;
        """)
        self.prompt_label.setFixedHeight(70)
        layout.addWidget(self.prompt_label)

        # ── Buffer / typed digits display ──────────────────────────────────────
        self.buffer_label = QLabel("")
        self.buffer_label.setAlignment(Qt.AlignCenter)
        self.buffer_label.setStyleSheet("""
            color: #4fc3f7;
            font-size: 34px; font-weight: 700;
            background: rgba(79,195,247,0.07);
            border: 1px solid rgba(79,195,247,0.18);
            border-radius: 14px;
            padding: 4px;
        """)
        self.buffer_label.setFixedHeight(58)
        layout.addWidget(self.buffer_label)

        # ── Dial pad ───────────────────────────────────────────────────────────
        grid = QGridLayout()
        grid.setSpacing(10)
        buttons = [
            ('1',0,0,''), ('2',0,1,'ABC'), ('3',0,2,'DEF'),
            ('4',1,0,'GHI'), ('5',1,1,'JKL'), ('6',1,2,'MNO'),
            ('7',2,0,'PQRS'), ('8',2,1,'TUV'), ('9',2,2,'WXYZ'),
            ('*',3,0,''), ('0',3,1,'+'), ('#',3,2,''),
        ]
        for text, row, col, sub in buttons:
            btn_w = QWidget()
            btn_w.setFixedSize(90, 70)
            vb = QVBoxLayout(btn_w)
            vb.setContentsMargins(0,0,0,0)
            vb.setSpacing(1)

            btn = QPushButton(text)
            btn.setFixedSize(90, 70)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.07);
                    color: #fff;
                    font-size: 24px; font-weight: 600;
                    border-radius: 14px;
                    border: 1px solid rgba(255,255,255,0.10);
                }
                QPushButton:hover  { background: rgba(255,255,255,0.14); }
                QPushButton:pressed{ background: rgba(79,195,247,0.22); color:#4fc3f7; }
            """)
            if sub:
                btn.setToolTip(sub)
            btn.clicked.connect(self.dial_press)
            vb.addWidget(btn)
            grid.addWidget(btn_w, row, col)

        layout.addLayout(grid)

        # ── Bottom row: mute / speaker / end ──────────────────────────────────
        btm = QHBoxLayout()
        btm.setSpacing(12)

        for icon, tip in [("🎤", "Mute"), ("🔊", "Speaker")]:
            b = QPushButton(icon)
            b.setFixedSize(60, 60)
            b.setToolTip(tip)
            b.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.09);
                    font-size: 22px;
                    border-radius: 30px;
                    border: 1px solid rgba(255,255,255,0.12);
                }
                QPushButton:hover  { background: rgba(255,255,255,0.18); }
            """)
            btm.addWidget(b)

        end_btn = QPushButton("📵")
        end_btn.setFixedSize(70, 70)
        end_btn.setStyleSheet("""
            QPushButton {
                background: qradialgradient(cx:0.5,cy:0.4,radius:0.6,
                    fx:0.5,fy:0.4, stop:0 #ef5350, stop:1 #b71c1c);
                font-size: 26px;
                border-radius: 35px;
                border: 2px solid rgba(255,255,255,0.20);
            }
            QPushButton:hover  { background: #e53935; }
            QPushButton:pressed{ background: #c62828; }
        """)
        end_btn.clicked.connect(self.end_call)
        btm.addWidget(end_btn)
        layout.addLayout(btm)

        screen.setLayout(layout)
        return screen

    # ── Audio ─────────────────────────────────────────────────────────────────
    def init_audio(self):
        self.player = QMediaPlayer()
        if os.path.exists("ring.wav"):
            url = QUrl.fromLocalFile(os.path.abspath("ring.wav"))
            self.player.setMedia(QMediaContent(url))
            self.player.setVolume(75)

    # ── TTS wrapper ───────────────────────────────────────────────────────────
    def speak(self, text):
        """Queue text for TTS. Updates the prompt label too."""
        self.prompt_label.setText(text)
        self.tts.speak(text)

    # ── State machine ─────────────────────────────────────────────────────────
    def show_idle_screen(self):
        self.stacked.setCurrentIndex(0)
        self.state = "IDLE"

    def make_call(self):
        self.stacked.setCurrentIndex(1)
        self.state = "RINGING"
        if self.player.state() != QMediaPlayer.PlayingState:
            self.player.play()
        QTimer.singleShot(4000, self.connect_call)

    def connect_call(self):
        self._stop_ringtone()
        self.stacked.setCurrentIndex(2)
        self.state = "SELECT_LANG"
        self.digit_buffer = ""
        self.buffer_label.setText("")
        # Delay slightly so screen transition completes before TTS fires
        QTimer.singleShot(300, self.start_selection_flow)

    def _stop_ringtone(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.stop()

    def start_selection_flow(self):
        self.speak("Welcome to TaleemLine. Please select language: Press 1 for English, 2 for Urdu")

    def dial_press(self):
        if self.state not in ["SELECT_LANG", "SELECT_GRADE", "SELECT_SUBJECT", "DUMMY_CALL"]:
            return
        btn = self.sender()
        digit = btn.text()
        self.digit_buffer += digit
        self.buffer_label.setText(self.digit_buffer)

        if self.state == "SELECT_LANG":
            self.submit_language()
        elif self.state == "SELECT_SUBJECT":
            self.submit_subject()
        elif self.state == "SELECT_GRADE":
            self.grade_timer.start(800)
        elif self.state == "DUMMY_CALL":
            self.submit_dummy()

    def submit_language(self):
        digit = self.digit_buffer
        if not digit:
            return
        if digit in ['1', '2', '3']:
            self.selected_lang = digit
            self.state = "SELECT_GRADE"
            self.digit_buffer = ""
            self.buffer_label.setText("")
            # ── FIX: speak grade prompt AFTER updating state ──────────────────
            QTimer.singleShot(50, lambda: self.speak(
                f"Language set to {self._lang_name(digit)}. "
                "Now select your grade. Press 1 through 9, or 10, 11, 12."
            ))
        else:
            self.digit_buffer = ""
            self.buffer_label.setText("")
            QTimer.singleShot(50, lambda: self.speak("Invalid choice. Please press 1 for English, 2 for Urdu"))

    def submit_grade(self):
        digit = self.digit_buffer
        if not digit:
            return
        if digit.isdigit() and 1 <= int(digit) <= 12:
            self.selected_grade = digit
            self.state = "SELECT_SUBJECT"
            self.digit_buffer = ""
            self.buffer_label.setText("")
            # ── FIX: speak subject prompt AFTER updating state ────────────────
            QTimer.singleShot(50, lambda: self.speak(
                f"Grade {digit} selected. Now choose your subject: "
                "1 for Maths, 2 for English, 3 for Science, "
                "4 for Urdu, 5 for Physics, 6 for Chemistry."
            ))
        else:
            self.digit_buffer = ""
            self.buffer_label.setText("")
            QTimer.singleShot(50, lambda: self.speak("Invalid grade. Please enter a number between 1 and 12."))

    def submit_subject(self):
        digit = self.digit_buffer
        if not digit:
            return
        if digit in ['1', '2', '3', '4', '5', '6']:
            self.selected_subject = digit
            self.state = "DUMMY_CALL"
            self.digit_buffer = ""
            self.buffer_label.setText("")
            QTimer.singleShot(50, lambda: self.speak(
                f"{self._subject_name(digit)} selected. Your session has started. "
                "You may ask questions or press End Call when finished."
            ))
        else:
            self.digit_buffer = ""
            self.buffer_label.setText("")
            QTimer.singleShot(50, lambda: self.speak("Invalid choice. Please press 1 to 6 for your subject."))

    def submit_dummy(self):
        if self.digit_buffer:
            d = self.digit_buffer
            self.digit_buffer = ""
            self.buffer_label.setText("")
            QTimer.singleShot(50, lambda: self.speak(f"You pressed {d}. This is a placeholder session."))

    def _lang_name(self, d):
        return {'1': 'English', '2': 'Urdu', '3': 'Pashto'}.get(d, '')

    def _subject_name(self, d):
        return {'1':'Maths','2':'English','3':'Science','4':'Urdu','5':'Physics','6':'Chemistry'}.get(d,'')

    def end_call(self):
        self.grade_timer.stop()
        self.ring_timer.stop()
        self.state = "IDLE"
        self.selected_lang = self.selected_grade = self.selected_subject = None
        self.digit_buffer = ""
        self.buffer_label.setText("")
        self._stop_ringtone()
        self.show_idle_screen()

    # ── Draggable window ──────────────────────────────────────────────────────
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag_pos = e.globalPos()

    def mouseMoveEvent(self, e):
        if self.drag_pos is not None:
            self.move(self.pos() + e.globalPos() - self.drag_pos)
            self.drag_pos = e.globalPos()

    def mouseReleaseEvent(self, e):
        self.drag_pos = None


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PhoneUI()
    window.show()
    sys.exit(app.exec_())