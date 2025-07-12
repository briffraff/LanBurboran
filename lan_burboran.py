import sys
import socket

from UI.lan_burboran_UI import LanBurboran_UI
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox)
from PySide6.QtCore import Qt, Signal, QObject

USERNAME = f'User-{socket.gethostname()}'


class SignalHandler(QObject):
    new_message = Signal(str)
    update_users = Signal(set)


class LanBurboran:
    def __init__(self, is_server=False):
        self.window = QMainWindow()
        self.window_ui = LanBurboran_UI()
        self.window_ui.setupUi(self.window)

        self.is_server = is_server

        self.users = set()
        self.signals = SignalHandler()
        self.signals.new_message.connect(self.display_message)
        self.signals.update_users.connect(self.refresh_user_list)

        self.window_ui.send_btn.clicked.connect(self.send_message)

    def display_message(self, msg):
        self.window_ui.chat_view.append(msg)

    def refresh_user_list(self, users_set):
        self.users = users_set
        self.window_ui.user_list.clear()
        for u in users_set:
            self.window_ui.user_list.addItem(u)
        self.window_ui.header.setText(
            f"Стая: LAN Chat Room • Онлайн: {len(users_set)}"
        )

    def send_message(self):
        text = self.window_ui.input.text().strip()
        if not text:
            return
        full = f"{USERNAME}: {text}"
        self.display_message(full)
        # TODO: send to server
        self.window_ui.input.clear()


def main():
    app = QApplication(sys.argv)
    reply = QMessageBox.question(None, "Избор", "Създаване на стая (Server)?",
                                 QMessageBox.Yes | QMessageBox.No)

    is_server = (reply == QMessageBox.Yes)

    lanburboran = LanBurboran(is_server)
    lanburboran_window = lanburboran.window
    lanburboran_window.show()

    app.exec()


if __name__ == "__main__":
    main()
