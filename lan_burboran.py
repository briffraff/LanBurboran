import sys

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QTextEdit, QListWidget, QLineEdit, QPushButton,
                               QLabel, QMessageBox)


class LanBurboran(QWidget):
    def __init__(self, is_server=False):
        super().__init__()
        self.is_server = is_server
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("LAN Burboran")
        layout = QVBoxLayout()
        header = QLabel(f"Стая: Седянка • Онлайн: 1")
        self.header = header
        layout.addWidget(header)

        main_layout = QHBoxLayout()
        self.user_list = QListWidget()
        self.chat_view = QTextEdit(readOnly=True)
        main_layout.addWidget(self.user_list, 1)
        main_layout.addWidget(self.chat_view, 3)
        layout.addLayout(main_layout)

        bottom = QHBoxLayout()
        self.input = QLineEdit()
        send_btn = QPushButton("Изпрати")
        bottom.addWidget(self.input)
        bottom.addWidget(send_btn)
        layout.addLayout(bottom)

        self.setLayout(layout)
        self.show()


def main():
    app = QApplication(sys.argv)
    reply = QMessageBox.question(None, "Избор", "Създаване на стая (Server)?",
                                 QMessageBox.Yes | QMessageBox.No)
    is_server = (reply == QMessageBox.Yes)
    w = LanBurboran(is_server)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
