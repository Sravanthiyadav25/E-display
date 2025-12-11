import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Window settings
        self.setWindowTitle("MQTT Timetable - Sections Control Panel")
        self.setFixedSize(600, 400)

        # Gradient Background
        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0.0, QColor(60, 150, 255))
        gradient.setColorAt(1.0, QColor(0, 50, 140))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        # Layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Title
        title = QLabel("Select Section")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setStyleSheet("color: white; margin-bottom: 25px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Button Style
        button_style = """
            QPushButton {
                background-color: white;
                color: #003366;
                border-radius: 15px;
                font-size: 22px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #00c3ff;
                color: white;
                font-weight: bold;
            }
        """

        # Section A button
        btn_a = QPushButton("Section A")
        btn_a.setStyleSheet(button_style)
        btn_a.clicked.connect(lambda: self.open_window("publisher_A.py"))
        layout.addWidget(btn_a)

        # Section B button
        btn_b = QPushButton("Section B")
        btn_b.setStyleSheet(button_style)
        btn_b.clicked.connect(lambda: self.open_window("publisher_B.py"))
        layout.addWidget(btn_b)

        # Section C button
        btn_c = QPushButton("Section C")
        btn_c.setStyleSheet(button_style)
        btn_c.clicked.connect(lambda: self.open_window("publisher_C.py"))
        layout.addWidget(btn_c)

        self.setLayout(layout)

        # Animations
        self.apply_animation(btn_a)
        self.apply_animation(btn_b)
        self.apply_animation(btn_c)

    # Animation function
    def apply_animation(self, widget):
        anim = QPropertyAnimation(widget, b"geometry")
        anim.setDuration(600)
        anim.setStartValue(QRect(widget.x(), widget.y() + 50, widget.width(), widget.height()))
        anim.setEndValue(QRect(widget.x(), widget.y(), widget.width(), widget.height()))
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()

    # Open respective publisher file
    def open_window(self, file):
        subprocess.Popen(["python", file])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
