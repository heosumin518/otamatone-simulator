# gui.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont

from sound import SoundPlayer


class Fretboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(120, 600)
        self.setStyleSheet("background-color: #cccccc; border: 2px solid #333333;")
        self.current_y = self.height() // 2

        self.wow_on = False

        self.note_labels = [
            ("A3", 220.00),
            ("A#3", 233.08),
            ("B3", 246.94),
            ("C4", 261.63),
            ("C#4", 277.18),
            ("D4", 293.66),
            ("D#4", 311.13),
            ("E4", 329.63),
            ("F4", 349.23),
            ("F#4", 369.99),
            ("G4", 392.00),
            ("G#4", 415.30),
            ("A4", 440.00),
            ("A#4", 466.16),
            ("B4", 493.88),
            ("C5", 523.25),
            ("C#5", 554.37),
            ("D5", 587.33),
            ("D#5", 622.25),
            ("E5", 659.25),
            ("A5", 880.00),
        ]


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 클릭 영역
        painter.setBrush(QColor("#a0c4ff"))
        painter.drawRect(30, 0, 60, self.height())  # ← x=30으로 변경

        # 현재 마커
        painter.setBrush(QColor(30, 80, 200))
        painter.drawEllipse(40, int(self.current_y) - 6, 40, 12)

        # 계이름
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 10))

        for name, freq in self.note_labels:
            y = self.frequency_to_y(freq)
            y = max(10, min(self.height() - 10, y))  # 위아래 margin
            painter.drawText(5, int(y + 4), name)  # ← x=5, y 보정 +4

    def frequency_to_y(self, freq):
        min_freq = 220
        max_freq = 880
        ratio = (freq - min_freq) / (max_freq - min_freq)
        return self.height() * (1.0 - ratio)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.set_position(event.pos().y())

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.set_position(event.pos().y())

    def set_position(self, y):
        y = max(0, min(self.height(), y))
        self.current_y = y
        freq = self.map_y_to_frequency(y)
        print(f"[지판] Y: {y}, 주파수: {freq:.2f} Hz")
        self.update()

    def map_y_to_frequency(self, y):
        min_freq = 220
        max_freq = 880
        ratio = 1.0 - (y / self.height())
        return min_freq + (max_freq - min_freq) * ratio
    
    def set_frequency(self, target_freq):
        min_freq = 220
        max_freq = 880
        ratio = (target_freq - min_freq) / (max_freq - min_freq)
        y = self.height() * (1.0 - ratio)
        self.set_position(y)



class OtamatoneGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Otamatone GUI")
        self.setGeometry(100, 100, 300, 700)
        self.setFocusPolicy(Qt.StrongFocus)

        self.melody_on = False
        self.wow_on = False

        self.fretboard = Fretboard()

        self.current_note_label = QLabel("현재 음: 없음")
        self.current_note_label.setAlignment(Qt.AlignCenter)
        self.current_note_label.setFont(QFont("Arial", 14))
        self.current_note_label.setStyleSheet("color: #222222;")

        self.melody_label = QLabel("🎵 멜로디: OFF")
        self.wow_label = QLabel("🌊 와우: OFF")
        for label in (self.melody_label, self.wow_label):
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont("Arial", 12))
            label.setStyleSheet("color: #333;")

        self.waveform_label = QLabel("📈 파형 시각화 영역")
        self.waveform_label.setFixedHeight(80)
        self.waveform_label.setAlignment(Qt.AlignCenter)
        self.waveform_label.setStyleSheet("background-color: #eeeeee; border: 1px solid #999999;")

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.fretboard, alignment=Qt.AlignCenter)
        layout.addSpacing(5)
        layout.addWidget(self.current_note_label)
        layout.addSpacing(10)
        layout.addWidget(self.melody_label)
        layout.addWidget(self.wow_label)
        layout.addSpacing(20)
        layout.addWidget(self.waveform_label)
        layout.addStretch()

        self.setLayout(layout)

        self.sound_player = SoundPlayer(
            get_frequency_callback=self.get_frequency,
            get_melody_state_callback=self.is_melody_on,
            get_wow_state_callback=self.is_wow_on
        )

        self.key_note_map = {
            # 기본음 (흰건반 위치: ASDFGHJKL;)
            Qt.Key_A: "B3",       # 시3
            Qt.Key_S: "C4",       # 도4
            Qt.Key_D: "D4",       # 레4
            Qt.Key_F: "E4",       # 미4
            Qt.Key_G: "F4",       # 파4
            Qt.Key_H: "G4",       # 솔4
            Qt.Key_J: "A4",       # 라4
            Qt.Key_K: "B4",       # 시4
            Qt.Key_L: "C5",       # 도5
            Qt.Key_Semicolon: "D5",  # 레5

            # 샵 음 (검은건반 위치: QWERTYUI)
            Qt.Key_Q: "C#4",
            Qt.Key_W: "D#4",
            # E4에는 샵 없음
            Qt.Key_E: "F#4",
            Qt.Key_R: "G#4",
            Qt.Key_T: "A#4",
            Qt.Key_Y: "C#5",
            Qt.Key_U: "D#5",
        }

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            key = event.key()

            if key == Qt.Key_Shift:
                self.wow_on = not self.wow_on
                self.update_labels()

            elif key == Qt.Key_Space:
                self.melody_on = True
                self.update_labels()

            # 키보드 음 입력
            elif key in self.key_note_map:
                note_name = self.key_note_map[key]
                for name, freq in self.fretboard.note_labels:
                    if name == note_name:
                        y = self.fretboard.frequency_to_y(freq)
                        self.fretboard.set_position(y)
                        self.melody_on = True
                        self.update_labels()
                        self.update_current_note_label(note_name)
                        break

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            key = event.key()

            if key == Qt.Key_Space or key in self.key_note_map:
                self.melody_on = False
                self.update_labels()
                self.update_current_note_label("없음")

    def update_labels(self):
        self.melody_label.setText(f"🎵 멜로디: {'ON' if self.melody_on else 'OFF'}")
        self.wow_label.setText(f"🌊 와우: {'ON' if self.wow_on else 'OFF'}")

    def get_frequency(self):
        return self.fretboard.map_y_to_frequency(self.fretboard.current_y)

    def is_melody_on(self):
        return self.melody_on

    def is_wow_on(self):
        return self.wow_on
    
    def closeEvent(self, event):
        self.sound_player.stop()
        event.accept()

    def update_current_note_label(self, note_name):
        self.current_note_label.setText(f"현재 음: {note_name}")
