from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QLabel,
    QSizePolicy,
    QStackedWidget,
    QGraphicsDropShadowEffect,
    QInputDialog,
    QScrollArea,
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QTimer, QTime, QEvent, QDateTime, QDate, QPropertyAnimation, QPoint
import datetime
import time
import sys

# Prefer QTextToSpeech if available; fall back to pyttsx3
try:
    from PyQt5.QtTextToSpeech import QTextToSpeech  # type: ignore
    _HAS_QT_TTS = True
except Exception:
    _HAS_QT_TTS = False
    import pyttsx3  # type: ignore


class TimetableApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timetable - Editable")
        self.setMinimumSize(600, 600)
        self.showMaximized()

        # Text-to-speech setup (use Qt TTS when available otherwise pyttsx3)
        if _HAS_QT_TTS:
            self.speech_engine = QTextToSpeech()
            try:
                self.speech_engine.setVolume(1.0)
            except Exception:
                pass
        else:
            self.speech_engine = None  # we'll use pyttsx3 when needed

        # Notice and scheduling flags
        self.notice_text = "Tomorrow is a holiday"
        self.notice_read = False
        self.schedule_time = "01:04:00 PM"  # example scheduled time (hh:mm:ss AP)
        self.start_schedule_timer()
        self.start_midnight_reset_timer()

        # Timetable/highlight state
        self.current_subject_slot = None
        self.last_subject_read = None

        # Keep original styles for resetting
        self.original_styles = {}
        self.buttons = {}

        # Build UI
        self.initUI()

        # Timer to update highlight and timetable frequently
        self.highlight_timer = QTimer(self)
        self.highlight_timer.timeout.connect(self.update_highlight)
        self.highlight_timer.start(1000)  # every second

        # Periodic timetable update (once per minute)
        self.timetable_update_timer = QTimer(self)
        self.timetable_update_timer.timeout.connect(self.update_timetable)
        self.timetable_update_timer.start(60 * 1000)  # every 60 seconds
        self.update_timetable()

    def initUI(self):
        main__layout = QVBoxLayout()
        # Header: logo + college name + images
        logo_row_layout = QHBoxLayout()
        logo_row_layout.setSpacing(0)
        logo_row_layout.setContentsMargins(0, 0, 0, 0)

        # College Logo (left)
        self.logo__label = QLabel(self)
        try:
            pixmap = QPixmap("C:/Users/DELL/Desktop/college_logo.jpg")
            pixmap = pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo__label.setPixmap(pixmap)
            self.logo__label.setFixedSize(pixmap.size())
        except Exception:
            self.logo__label.setText("Logo")
        logo_row_layout.addWidget(self.logo__label, alignment=Qt.AlignLeft)

        # College Name (center)
        self.college_name_button = QPushButton("     SPHOORTHY ENGINEERING COLLEGE    ")
        self.college_name_button.setStyleSheet(
            "background-color:black;color:white;font-weight:bold;font-family:ARIAL;font-size:40px; padding: 10px; border:2px solid WHITE"
        )
        self.college_name_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        logo_row_layout.addWidget(self.college_name_button, alignment=Qt.AlignCenter)

        # NAAC Image (right)
        self.naac_image_label = QLabel(self)
        try:
            naac_pixmap = QPixmap("C:/Users/DELL/Desktop/naac_image.jpg")
            naac_pixmap = naac_pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.naac_image_label.setPixmap(naac_pixmap)
            self.naac_image_label.setFixedSize(naac_pixmap.size())
        except Exception:
            self.naac_image_label.setText("NAAC")
        logo_row_layout.addWidget(self.naac_image_label, alignment=Qt.AlignRight)

        main__layout.addLayout(logo_row_layout)

        # Academic year banner
        self.academic_year_button = QPushButton("CSE-C-2ND YEAR B.TECH 1ST SEMESTER ACADEMIC YEAR: 2024-2025")
        self.academic_year_button.setStyleSheet(
            "background-color:#FF9636;color:BLACK;font-weight:bold;font-family:ARIAL;font-size:25px;padding:10px;border:2px solid white"
        )
        main__layout.addWidget(self.academic_year_button)

        # Class Incharge, Lecture hall, Date/time
        button_layout = QHBoxLayout()
        self.class_incharge_button = QPushButton("CLASS INCHARGE : DR.KAJA MASTHAN AND D.MAMATHA REDDY")
        self.class_incharge_button.setStyleSheet(
            "background-color:#00C9A7;color:BLACK;font-weight:bold;font-family:ARIAL;font-size:25px;padding:10px;border:2px solid white;text-align: left;"
        )
        button_layout.addWidget(self.class_incharge_button)

        lecture_hall_layout = QHBoxLayout()
        lecture_hall_label = QLabel("Lecture Hall: 406")
        lecture_hall_label.setStyleSheet("background-color:#F9F871;font-size: 20px; font-weight: bold; padding: 10px; border: 1px solid black;")
        lecture_hall_layout.addWidget(lecture_hall_label)

        self.date_time_label = QLabel()
        self.date_time_label.setStyleSheet("background-color:#F9F871;font-size: 20px; font-weight: bold; padding: 10px; border: 1px solid black;")
        lecture_hall_layout.addWidget(self.date_time_label)

        button_layout.addLayout(lecture_hall_layout)
        main__layout.addLayout(button_layout)

        # Notice scroller
        self.scroll_button = QPushButton((" " + self.notice_text + " || ") * 10)
        self.scroll_button.setStyleSheet("background-color:#0D5F8A;color:white;font-weight:Bold;font-style:italic ;font-family:verdana;font-size:30px;padding:10px;border:2px solid white")
        self.scroll_button.installEventFilter(self)
        self.scroll_button.mouseDoubleClickEvent = self.on_double_click
        main__layout.addWidget(self.scroll_button)

        # Timetable area (left / main)
        timetable_widget = QWidget()
        self.grid__layout = QGridLayout()
        self.grid__layout.setContentsMargins(1, 1, 1, 1)
        self.grid__layout.setSpacing(1)

        # Timetable data
        self.timetable__data = [
            [("JAVA", "G.PRASAD"), ("COSM", "SRIHARI"), ("BREAK", ""), ("COA", "MAMATHA"), ("DE", "PRIYA"), ("LUNCH", ""), ("DE", "PRIYA"), ("DS", "KIRAN"), ("SPORTS", "")],
            [("JAVA", "G.PRASAD"), ("JAVA / DS LAB", "G.PRASAD"), ("BREAK", ""), ("JAVA / DS LAB", "G.PRASAD"), ("LIBRARY", ""), ("LUNCH", ""), ("COSM", "SRIHARI"), ("COA", "MAMATHA"), ("DS", "KIRAN")],
            [("COA", "MAMATHA"), ("JAVA", "G.PRASAD"), ("BREAK", ""), ("DS", "KIRAN"), ("LIBRARY", ""), ("LUNCH", ""), ("COA", "MAMATHA"), ("DE", "PRIYA"), ("COSM", "SRIHARI")],
            [("COSM", "SRIHARI"), ("DS", "KIRAN"), ("BREAK", ""), ("COA", "MAMATHA"), ("DE", "PRIYA"), ("LUNCH", ""), ("SDC LAB", "DIVYA"), ("SDC LAB", "DIVYA"), ("JAVA", "G.PRASAD")],
            [("DS / JAVA LAB", "KIRAN"), ("DS", "KIRAN"), ("BREAK", ""), ("COSM", "SRIHARI"), ("COA", "MAMATHA"), ("LUNCH", ""), ("GS LAB", "PRIYANKA"), ("GS LAB", "PRIYANKA"), ("DS LAB", "KIRAN")],
            [("JAVA", "G.PRASAD"), ("DS", "KIRAN"), ("BREAK", ""), ("COSM", "SRIHARI"), ("COA", "MAMATHA"), ("LUNCH", ""), ("", ""), ("", ""), ("", "")],
        ]

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        times_headers = [
            "TIME/DAY",
            "9:00am-10:00am",
            "10:00am-10:50am",
            "10:50-11:00",
            "11:00am-11:50am",
            "11:50am-12:40pm",
            "12:40-1:30",
            "1:30pm-2:20pm",
            "2:20pm-3:10pm",
            "3:10pm-4:00pm",
        ]

        # Add headers
        for col, time_h in enumerate(times_headers):
            header__button = QPushButton(time_h)
            header__button.setStyleSheet("background-color:#444444;color:WHITE;font-weight:bold;font-size:20px;padding:10px;border:2px solid white")
            header__button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.grid__layout.addWidget(header__button, 0, col)

        # Add days and subject buttons
        for row, day in enumerate(days):
            day_button = QPushButton(day)
            day_button.setStyleSheet("background-color:#444444;color:white;font-weight:bold;font-size:25px;padding:10px;border:2px solid white")
            day_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.grid__layout.addWidget(day_button, row + 1, 0)
            for col, (subject, professor) in enumerate(self.timetable__data[row]):
                self.create_subject_button(row, col, subject, professor)

        timetable_widget.setLayout(self.grid__layout)
        main__layout.addWidget(timetable_widget, 50)

        # Events and clock area (bottom/right)
        event_widget = QWidget()
        event_layout = QHBoxLayout()
        event_label = QLabel("📅 Upcoming Events")
        event_label.setAlignment(Qt.AlignCenter)
        event_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        event_layout.addWidget(event_label)

        # Events (example)
        event_buttons_layout = QHBoxLayout()
        event_buttons_container = QVBoxLayout()
        events = ["Seminar", "Workshop", "Exam", "Holiday", "tech fest", "ugadi", "annual day"]
        for event in events[:3]:
            btn = QPushButton(event)
            btn.setStyleSheet("background-color: lightblue; font-size: 20px; padding: 8px;")
            event_buttons_container.addWidget(btn)
        event_buttons_layout.addLayout(event_buttons_container)

        # Scrollable remaining events
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        for event in events[3:]:
            btn = QPushButton(event)
            btn.setStyleSheet("background-color: lightblue; font-size: 18px; padding: 5px;")
            self.scroll_layout.addWidget(btn)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setFixedWidth(300)
        self.scroll_area.setFixedHeight(120)
        event_buttons_layout.addWidget(self.scroll_area)

        event_layout.addLayout(event_buttons_layout)

        # Clock
        self.clock_widget = QLabel()
        self.clock_widget.setFixedSize(200, 110)
        self.clock_widget.setAlignment(Qt.AlignCenter)
        self.clock_widget.setStyleSheet("border: 5px solid black; border-radius: 50px; background:pink; font-size: 40px; padding: 10px;")
        self.update_time()
        clock_timer = QTimer(self)
        clock_timer.timeout.connect(self.update_time)
        clock_timer.start(1000)

        clock_container = QVBoxLayout()
        clock_container.addStretch()
        clock_container.addWidget(self.clock_widget, alignment=Qt.AlignRight)
        event_layout.addLayout(clock_container)

        event_widget.setLayout(event_layout)
        main__layout.addWidget(event_widget, 2)

        self.setLayout(main__layout)
        self.show()

    def create_subject_button(self, row, col, subject, professor):
        # Choose color based on subject type
        if "LAB" in subject:
            button_color = "#00C9A7"
        elif "BREAK" in subject or "LUNCH" in subject:
            button_color = "#1E73BE"
        elif "SPORTS" in subject or "LIBRARY" in subject:
            button_color = "#FFF600"
        else:
            button_color = "white"

        button = QPushButton(f"{subject}\n{professor}")
        original_style = f"background-color: {button_color}; font-size: 20px; padding: 10px; font-weight:bold;"
        button.setStyleSheet(original_style)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.mouseDoubleClickEvent = lambda event, r=row, c=col, b=button, s=subject, p=professor: self.edit__subject(r, c, b, s, p)
        self.grid__layout.addWidget(button, row + 1, col + 1)
        self.buttons[(row, col)] = button
        self.original_styles[(row, col)] = original_style

    def update_timetable(self):
        current_time = QTime.currentTime()
        current_day = QDate.currentDate().dayOfWeek() - 1  # 0=Monday
        current_slot = self.get_current_slot(current_time, current_day)
        self.highlight_current_subject(current_slot)

    def get_current_slot(self, current_time, current_day):
        # Define start times for slots roughly matching headers (ordered)
        times = [
            QTime(9, 0),
            QTime(10, 0),
            QTime(10, 50),
            QTime(11, 0),
            QTime(11, 50),
            QTime(12, 40),
            QTime(13, 30),
            QTime(14, 30),
            QTime(15, 30),
        ]
        durations = [
            3600,  # 9:00 - 10:00
            3000,  # 10:00 - 10:50 (50 min = 3000s)
            600,   # 10:50 - 11:00 (10 min)
            3000,  # 11:00 - 11:50
            3000,  # 11:50 - 12:40
            3000,  # 12:40 - 13:30
            3000,  # 13:30 - 14:20/30
            3600,  # 14:30 - 15:30
            1800,  # 15:30 - 16:00
        ]

        if current_day < len(self.timetable__data):
            for i, start_time in enumerate(times):
                end_time = start_time.addSecs(durations[i])
                if start_time <= current_time < end_time:
                    return current_day, i

            # If no active slot, return next upcoming slot on the same day
            for i, start_time in enumerate(times):
                if current_time < start_time:
                    return current_day, i

        return None

    def highlight_current_subject(self, current_slot):
        # Reset previous highlighted button
        if current_slot != self.current_subject_slot:
            if self.current_subject_slot:
                prev_row, prev_col = self.current_subject_slot
                prev_button = self.buttons.get((prev_row, prev_col))
                if prev_button:
                    original_style = self.original_styles.get((prev_row, prev_col), "")
                    prev_button.setStyleSheet(original_style)

            # Highlight new slot
            if current_slot is not None:
                row, col = current_slot
                button = self.buttons.get((row, col))
                if button:
                    button.setStyleSheet("background-color: white; color: black; font-weight: bold; font-size: 20px; border: 5px solid #ff5C4D;")
                    subject, professor = self.timetable__data[row][col]
                    # speak subject once when it becomes active
                    if subject and subject != self.last_subject_read:
                        self.read_subject(subject)
                        self.last_subject_read = subject

            self.current_subject_slot = current_slot

    def update_highlight(self):
        # Called by a frequent timer to keep UI responsive
        current_time = QTime.currentTime()
        current_day = QDate.currentDate().dayOfWeek() - 1
        current_slot = self.get_current_slot(current_time, current_day)
        self.highlight_current_subject(current_slot)

    def read_subject(self, subject):
        # Use Qt TTS when available, otherwise pyttsx3
        message = f"It's time for: {subject}"
        if _HAS_QT_TTS and self.speech_engine is not None:
            try:
                self.speech_engine.say(message)
            except Exception:
                pass
        else:
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 150)
                engine.setProperty("volume", 1.0)
                engine.say(message)
                engine.runAndWait()
            except Exception:
                pass

    def edit__subject(self, row, col, button, subject, professor):
        button.setVisible(False)
        edit_layout = QVBoxLayout()

        subject_edit = QLineEdit(subject)
        subject_edit.setStyleSheet("background-color:White;font-size: 16px;font-weight:bold; padding: 5px;")
        edit_layout.addWidget(subject_edit)

        professor_edit = QLineEdit(professor)
        professor_edit.setStyleSheet("background-color:white;font-size: 16px;font-weight:bold; padding: 5px;")
        edit_layout.addWidget(professor_edit)

        save_button = QPushButton("Save")
        save_button.setStyleSheet("font-size: 16px; font-weight:bold;padding: 5px; background-color: lightgreen;")
        save_button.clicked.connect(lambda: self.save__subject(row, col, subject_edit, professor_edit, button))
        edit_layout.addWidget(save_button)

        edit_widget = QWidget()
        edit_widget.setLayout(edit_layout)
        self.grid__layout.addWidget(edit_widget, row + 1, col + 1)

    def save__subject(self, row, col, subject_edit, professor_edit, button):
        new_subject = subject_edit.text()
        new_professor = professor_edit.text()
        self.timetable__data[row][col] = (new_subject, new_professor)

        button_color = self.get_subject_color(new_subject)
        button.setStyleSheet(f"background-color: {button_color}; font-size: 20px; font-weight: bold; padding: 10px;")
        button.setText(f"{new_subject}\n{new_professor}")

        parent_widget = subject_edit.parentWidget()
        if parent_widget:
            self.grid__layout.removeWidget(parent_widget)
            parent_widget.deleteLater()

        button.setVisible(True)

    def get_subject_color(self, subject):
        if "LAB" in subject:
            return "GREEN"
        elif "BREAK" in subject or "LUNCH" in subject:
            return "BLUE"
        elif "SPORTS" in subject or "LIBRARY" in subject:
            return "ORANGE"
        else:
            return "VIOLET"

    def scroll_text(self):
        current_text = self.scroll_button.text()
        if not current_text:
            return
        new_text = current_text[1:] + current_text[0]
        self.scroll_button.setText(new_text)

    def on_double_click(self, event):
        current_text = self.scroll_button.text()
        self.text_edit = QLineEdit(current_text, self)
        self.text_edit.setStyleSheet("font-size: 25px; font-weight: bold; color: white;")
        self.text_edit.setGeometry(self.scroll_button.geometry())
        self.text_edit.setAlignment(Qt.AlignLeft)
        self.scroll_button.hide()
        self.text_edit.show()
        self.text_edit.returnPressed.connect(self.save_edited_text)

    def save_edited_text(self):
        notice_text = self.text_edit.text()
        self.notice_text = notice_text
        self.scroll_button.setText((" " + (self.notice_text + " || ")) * 10)
        self.text_edit.hide()
        self.scroll_button.show()

    def start_schedule_timer(self):
        self.schedule_timer = QTimer(self)
        self.schedule_timer.timeout.connect(self.check_scheduled_time)
        self.schedule_timer.start(1000)

    def start_midnight_reset_timer(self):
        # Reset at midnight: use a 1-second timer to check if midnight passed to avoid drift issues
        self.midnight_timer = QTimer(self)
        self.midnight_timer.timeout.connect(self.reset_at_midnight_check)
        self.midnight_timer.start(60 * 1000)  # check every minute

    def reset_at_midnight_check(self):
        now = QDateTime.currentDateTime()
        if now.time().hour() == 0 and now.time().minute() == 0:
            self.notice_read = False

    def check_scheduled_time(self):
        current_time = QTime.currentTime().toString("hh:mm:ss AP")
        if current_time == self.schedule_time and not getattr(self, "notice_read", False):
            self.speak_notice()
            self.notice_read = True

    def speak_notice(self):
        # speak the notice three times
        if _HAS_QT_TTS and self.speech_engine is not None:
            try:
                for _ in range(3):
                    self.speech_engine.say(self.notice_text)
            except Exception:
                pass
        else:
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 150)
                engine.setProperty("volume", 1.0)
                for _ in range(3):
                    engine.say(self.notice_text)
                    engine.runAndWait()
            except Exception:
                pass

    def reset_notice_read_flag(self):
        self.notice_read = False

    def eventFilter(self, obj, event):
        if obj == self.scroll_button and event.type() == QEvent.MouseButtonDblClick:
            self.prompt_for_notice()
            return True
        return super().eventFilter(obj, event)

    def prompt_for_notice(self):
        text, ok = QInputDialog.getText(self, "Update Notice", "Enter new notice:")
        if ok and text:
            self.notice_text = text
            self.scroll_button.setText((" " + (self.notice_text + " || ")) * 10)

    def auto_scroll_events(self):
        # example auto scroll function for events (not used currently)
        self.scroll_position = getattr(self, "scroll_position", 0) + 10
        if self.scroll_position >= self.scroll_content.height() - self.scroll_area.height():
            self.scroll_position = 0
        self.scroll_area.verticalScrollBar().setValue(self.scroll_position)

    def update_time(self):
        current_time = QTime.currentTime().toString("hh:mm:ss")
        self.clock_widget.setText(current_time)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#ffffff"))
    app.setPalette(palette)

    window = TimetableApp()
    window.setStyleSheet("background-color: WHITE;")
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
