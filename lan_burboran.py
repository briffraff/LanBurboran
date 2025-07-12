import sys
from UI.lan_burboran_UI import LanBurboran_UI

from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox)


class LanBurboran:
    def __init__(self, is_server=False):
        self.window = QMainWindow()
        self.window_ui = LanBurboran_UI()
        self.window_ui.setupUi(self.window)

        self.is_server = is_server


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
