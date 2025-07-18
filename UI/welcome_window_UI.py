from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LAN Бърборан – Начало")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.logo_label = QLabel()
        pixmap = QPixmap(r"Resources\icon.png")
        pixmap = pixmap.scaled(
            150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Въведи потребителско име")
        layout.addWidget(self.username_input)

        self.create_btn = QPushButton("Създаване на стая")
        layout.addWidget(self.create_btn)

        self.join_btn = QPushButton("Влизане в чата")
        layout.addWidget(self.join_btn)

        self.setLayout(layout)
