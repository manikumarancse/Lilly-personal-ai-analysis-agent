from datetime import datetime
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)

class LillyAlert(QWidget):
    closed = Signal()

    def __init__(self, title: str, message: str):
        super().__init__()
        self._sound = QSoundEffect(self)
        self._build(title, message)

    def _build(self, title: str, message: str):
        # Tool window keeps Lilly out of Alt+Tab; always-on-top keeps it visible.
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setFixedWidth(390)

        self.setStyleSheet("""
            QWidget {
                background: #101828;
                color: #F9FAFB;
                font-family: "Segoe UI";
            }
            QLabel#title {
                font-size: 18px;
                font-weight: 700;
            }
            QLabel#time {
                color: #98A2B3;
                font-size: 11px;
            }
            QLabel#message {
                font-size: 14px;
            }
            QPushButton {
                background: #FFFFFF;
                color: #101828;
                border: none;
                border-radius: 7px;
                padding: 9px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #EAECF0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("title")

        time_label = QLabel(datetime.now().strftime("%d %b %Y • %I:%M:%S %p"))
        time_label.setObjectName("time")

        message_label = QLabel(message)
        message_label.setObjectName("message")
        message_label.setWordWrap(True)

        button_row = QHBoxLayout()
        button_row.addStretch()
        ack = QPushButton("Acknowledge")
        ack.clicked.connect(self.acknowledge)
        button_row.addWidget(ack)

        layout.addWidget(title_label)
        layout.addWidget(time_label)
        layout.addWidget(message_label)
        layout.addLayout(button_row)

    def showEvent(self, event):
        super().showEvent(event)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        margin = 18
        self.adjustSize()
        x = screen.right() - self.width() - margin
        y = screen.bottom() - self.height() - margin
        self.move(x, y)

        # Windows system alert sound, no bundled audio file required.
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

        self.raise_()
        self.activateWindow()

    def acknowledge(self):
        self.closed.emit()
        self.close()

    # Clicking the window's normal close path also counts as acknowledgement.
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
