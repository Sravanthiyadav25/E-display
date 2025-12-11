import sys
import json
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject
from edisplay_demo7 import TimetableApp

class Communicate(QObject):
    update_gui = pyqtSignal(list)

class SubscriberApp(TimetableApp):
    def _init_(self):
        super()._init_()
        # Disable editing
        for button in self.buttons.values():
            button.mouseDoubleClickEvent = lambda event: None
        # MQTT update signal
        self.comm = Communicate()
        self.comm.update_gui.connect(self.update_timetable_from_mqtt)

    def update_timetable_from_mqtt(self, new_data):
        for row, day_data in enumerate(new_data):
            for col, subject_info in enumerate(day_data):
                subject, professor = subject_info if isinstance(subject_info, (list, tuple)) else (subject_info, "")
                button = self.buttons.get((row, col))
                if button:
                    button.setText(f"{subject}\n{professor}")

# MQTT setup
client = mqtt.Client()
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        app_window.comm.update_gui.emit(data)
    except Exception as e:
        print("Error:", e)

client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("timetable/section/C")
client.loop_start()

# Run PyQt app
app = QApplication(sys.argv)
app_window = SubscriberApp()
app_window.setWindowTitle("Section C Timetable Display - Readonly")
app_window.showMaximized()
sys.exit(app.exec_())