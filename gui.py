# gui.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont


class Fretboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(100, 400)
        self.setStyleSheet("background-color: #cccccc; border: 2px solid #333333;")
        self.current_y = self.height() // 2

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#a0c4ff"))
        painter.drawRect(20, 0, 60, self.height())
        painter.setBrush(QColor(30, 80, 200))
        painter.drawEllipse(30, self.current_y - 6, 40, 12)

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


class OtamatoneGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Otamatone GUI")
        self.setGeometry(100, 100, 300, 600)
        self.setFocusPolicy(Qt.StrongFocus)

        self.melody_on = False
        self.wow_on = False

        self.fretboard = Fretboard()

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
        layout.addSpacing(10)
        layout.addWidget(self.melody_label)
        layout.addWidget(self.wow_label)
        layout.addSpacing(20)
        layout.addWidget(self.waveform_label)
        layout.addStretch()

        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.melody_on = True
            self.update_labels()
        elif event.key() == Qt.Key_Shift and not event.isAutoRepeat():
            self.wow_on = True
            self.update_labels()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.melody_on = False
            self.update_labels()
        elif event.key() == Qt.Key_Shift and not event.isAutoRepeat():
            self.wow_on = False
            self.update_labels()

    def update_labels(self):
        self.melody_label.setText(f"🎵 멜로디: {'ON' if self.melody_on else 'OFF'}")
        self.wow_label.setText(f"🌊 와우: {'ON' if self.wow_on else 'OFF'}")
