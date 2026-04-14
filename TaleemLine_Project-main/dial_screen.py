import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QGridLayout, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


# -----------------------------
# CALL SCREEN PLACEHOLDER
# -----------------------------
class CallScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(290, 600)
        self.setStyleSheet("background-color: black;")

        label = QLabel("CALL SCREEN", self)
        label.setStyleSheet("color: white; font-size: 20px;")
        label.move(60, 250)


# -----------------------------
# DIAL SCREEN
# -----------------------------
class DialScreen(QWidget):

    def __init__(self):
        super().__init__()

        # 📱 FIXED PHONE SIZE
        self.setFixedSize(290, 600)

        self.number = ""

        self.init_ui()

    # -------------------------
    # BACKGROUND
    # -------------------------
    def set_bg(self):
        self.bg = QLabel(self)
        pixmap = QPixmap("bg.png")

        self.bg.setPixmap(
            pixmap.scaled(
                290,
                600,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        self.bg.setGeometry(0, 0, 290, 600)
        self.bg.lower()

    # -------------------------
    # UI SETUP
    # -------------------------
    def init_ui(self):

        self.set_bg()

        # MAIN LAYOUT
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # TOP SPACER (pushes content down from top)
        main_layout.addStretch()

        # -------------------------
        # DIAL PAD CONTAINER (with number display above)
        # -------------------------
        dial_container = QWidget()
        dial_container.setFixedWidth(290)
        dial_container.setStyleSheet("""
            background-color: rgba(0, 0, 0, 180);
            border-radius: 20px;
        """)
        
        dial_layout = QVBoxLayout()
        dial_layout.setSpacing(15)
        dial_layout.setContentsMargins(15, 20, 15, 25)

        # NUMBER DISPLAY (directly above dial pad)
        self.display = QLabel("")
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display.setFixedHeight(60)
        self.display.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 100);
            border-radius: 10px;
            padding: 10px;
        """)
        
        dial_layout.addWidget(self.display)

        # GRID for numbers
        grid = QGridLayout()
        grid.setSpacing(10)

        buttons = [
            "1", "2", "3",
            "4", "5", "6",
            "7", "8", "9"
        ]

        positions = [(i, j) for i in range(3) for j in range(3)]

        for pos, num in zip(positions, buttons):
            btn = QPushButton(num)
            btn.setFixedSize(70, 70)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #222;
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                    border-radius: 35px;
                    border: 1px solid #444;
                }
                QPushButton:hover {
                    background-color: #333;
                }
                QPushButton:pressed {
                    background-color: #444;
                }
            """)
            btn.clicked.connect(lambda _, n=num: self.press(n))
            grid.addWidget(btn, *pos)

        # Add grid to dial layout
        dial_layout.addLayout(grid)

        # Add 0 button (centered)
        zero_layout = QHBoxLayout()
        zero_layout.addStretch()
        
        btn0 = QPushButton("0")
        btn0.setFixedSize(70, 70)
        btn0.setStyleSheet("""
            QPushButton {
                background-color: #222;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 35px;
                border: 1px solid #444;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        btn0.clicked.connect(lambda: self.press("0"))
        
        zero_layout.addWidget(btn0)
        zero_layout.addStretch()
        
        dial_layout.addLayout(zero_layout)

        # -------------------------
        # CALL BUTTON (below dial pad)
        # -------------------------
        call_layout = QHBoxLayout()
        call_layout.addStretch()
        
        self.call_btn = QPushButton("📞 CALL")
        self.call_btn.setFixedSize(120, 55)
        self.call_btn.setStyleSheet("""
            QPushButton {
                background-color: #2e7d32;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 27px;
                border: none;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:pressed {
                background-color: #1b5e20;
            }
        """)
        
        call_layout.addWidget(self.call_btn)
        call_layout.addStretch()
        
        dial_layout.addLayout(call_layout)
        dial_container.setLayout(dial_layout)
        
        main_layout.addWidget(dial_container)
        
        # BOTTOM SPACER
        main_layout.addStretch()

        # Apply main layout
        self.setLayout(main_layout)

    # -------------------------
    # NUMBER INPUT
    # -------------------------
    def press(self, num):
        self.number += num
        # Format display with spaces for better readability
        if len(self.number) <= 3:
            self.display.setText(self.number)
        else:
            formatted = ' '.join([self.number[i:i+3] for i in range(0, len(self.number), 3)])
            self.display.setText(formatted)

    # -------------------------
    # CLEAR BUTTON FUNCTIONALITY (Optional)
    # -------------------------
    def clear_number(self):
        self.number = ""
        self.display.setText("")

    # -------------------------
    # DELETE LAST DIGIT (Optional)
    # -------------------------
    def delete_last(self):
        self.number = self.number[:-1]
        if self.number:
            if len(self.number) <= 3:
                self.display.setText(self.number)
            else:
                formatted = ' '.join([self.number[i:i+3] for i in range(0, len(self.number), 3)])
                self.display.setText(formatted)
        else:
            self.display.setText("")

    # -------------------------
    # CALL ACTION
    # -------------------------
    def start_call(self):
        if self.number:
            print("Dialed:", self.number)

            self.call_window = CallScreen()
            self.call_window.show()

            self.close()
        else:
            print("Please enter a number to call")


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = DialScreen()
    window.show()

    sys.exit(app.exec())