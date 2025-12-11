import sys
import json
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLineEdit, QSizePolicy
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor, QPalette
from timetable_data import days, times, timetable_data

# MQTT setup
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.connect("broker.hivemq.com", 1883, 60)
client.loop_start()

# Subject colors
subject_colors = {
    "JAVA": "#FFD700",    # Gold
    "COSM": "#7FFFD4",    # Aquamarine
    "COA": "#FFB6C1",     # Light Pink
    "DE": "#FFA500",      # Orange
    "DS": "#98FB98",      # Pale Green
    "BREAK": "#D3D3D3",   # Light Grey
    "LUNCH": "#D3D3D3",
    "LIBRARY": "#ADD8E6", # Light Blue
    "SDC LAB": "#FF69B4",
    "GS LAB": "#87CEFA",
    "JAVA / DS LAB": "#F0E68C"
}

class PublisherA(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Publisher - Section A")
        self.setGeometry(50, 50, 1200, 700)

        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.entries = {}
        self.original_text = {}  # store original text for change detection

        # Header row (times)
        for col, time in enumerate(times):
            header = QPushButton(time)
            header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.grid_layout.addWidget(header, 0, col)

        # Timetable grid
        for row, day in enumerate(days):
            day_button = QPushButton(day)
            day_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.grid_layout.addWidget(day_button, row + 1, 0)

            for col, (subject, prof) in enumerate(timetable_data[row]):
                text = f"{subject}\n{prof}" if subject or prof else ""
                entry = QLineEdit(text)
                entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

                # Highlight initial subject
                color = subject_colors.get(subject, "#FFFFFF")  # default white
                palette = entry.palette()
                palette.setColor(QPalette.Base, QColor(color))
                entry.setPalette(palette)

                self.grid_layout.addWidget(entry, row + 1, col + 1)
                self.entries[(row, col)] = entry
                self.original_text[(row, col)] = text

                # Connect change detection
                entry.textChanged.connect(lambda _, r=row, c=col: self.highlight_changes(r, c))

        # Auto publish every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.publish)
        self.timer.start(1000)

    def highlight_changes(self, row, col):
        """Highlight cell if changed from original"""
        entry = self.entries[(row, col)]
        current_text = entry.text()
        original = self.original_text[(row, col)]
        palette = entry.palette()

        if current_text != original:
            palette.setColor(QPalette.Base, QColor("#FF6347"))  # Tomato for changes
        else:
            # Reset to subject color
            subject = current_text.split("\n")[0] if "\n" in current_text else current_text
            color = subject_colors.get(subject, "#FFFFFF")
            palette.setColor(QPalette.Base, QColor(color))
        entry.setPalette(palette)

    def publish(self):
        """Publish timetable to MQTT broker"""
        data_to_publish = []
        for row in range(len(days)):
            row_data = []
            for col in range(len(timetable_data[row])):
                text = self.entries[(row, col)].text()
                if "\n" in text:
                    subject, prof = text.split("\n", 1)
                else:
                    subject, prof = text, ""
                row_data.append([subject, prof])
            data_to_publish.append(row_data)

        client.publish("timetable/section/A", json.dumps(data_to_publish))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PublisherA()
    window.showMaximized()
    sys.exit(app.exec_())
