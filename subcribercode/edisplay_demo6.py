import sys
import ssl
import json
import paho.mqtt.client as mqtt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QPoint


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setup_mqtt()     # <---- MQTT Starts Running
        self.startScrolling() # <---- Scrolling Text  (optional)

    # ----------------------  MAIN UI  ----------------------
    def initUI(self):
        self.setWindowTitle("E-Display System")
        self.setGeometry(150, 150, 900, 600)

        main_layout = QVBoxLayout()

        # ---------- SCROLLING NOTICE TEXT ----------
        self.scroll_button = QPushButton(" Welcome to E-Display Notice Board ")
        self.scroll_button.setStyleSheet(
            "background-color: yellow; color: black; font-size: 20px; font-weight: bold;"
        )
        self.scroll_button.setFixedHeight(45)
        self.scroll_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # scrolling timer
        self.scroll_pos = 0
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.scrollText)

        main_layout.addWidget(self.scroll_button)

        # ---------- TIMETABLE JSON LOAD ----------
        try:
            with open("subjects.json", "r") as file:
                self.timetable = json.load(file)
        except:
            self.timetable = {
                "Monday": ["Maths", "Physics", "Chemistry", "Break", "English", "Lab"]
            }

        # ---------- TIMETABLE GRID ----------
        grid = QGridLayout()
        row = 0
        for period in self.timetable.get("Monday", []):
            label = QLabel(period)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 18px; padding: 10px; border: 1px solid black;")
            grid.addWidget(label, row, 0)
            row += 1

        main_layout.addLayout(grid)
        self.setLayout(main_layout)

    # ----------------------  MQTT SUBSCRIBER  ----------------------
    def setup_mqtt(self):
        self.mqtt_client = mqtt.Client()

        # Set username and password
        self.mqtt_client.username_pw_set("E-display", "Sphoorthy1")

        # TLS / SSL enable
        self.mqtt_client.tls_set(
            ca_certs="/etc/ssl/certs",
            tls_version=ssl.PROTOCOL_TLS
        )

        # message received callback
        def on_message(client, userdata, msg):
            incoming = msg.payload.decode()
            print("MQTT Message:", incoming)

            # update the scrolling notice with MQTT message
            self.scroll_button.setText("   " + incoming + "   ")

        self.mqtt_client.on_message = on_message

        # connect to HiveMQ cloud
        self.mqtt_client.connect(
            "db89b31f17b343648adedb9f54f0aa40.s1.eu.hivemq.cloud",
            8883
        )

        # subscribe to topic
        self.mqtt_client.subscribe("test/topic")

        # start mqtt thread
        self.mqtt_client.loop_start()

    # ----------------------  SCROLLING EFFECT  ----------------------
    def startScrolling(self):
        self.scroll_timer.start(80)

    def scrollText(self):
        text = self.scroll_button.text()
        text = text[1:] + text[0]  # rotate left
        self.scroll_button.setText(text)


# ----------------------  RUN APP  ----------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
