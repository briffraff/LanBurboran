import sys
from PySide6.QtWidgets import QApplication
from lan_burboran import LanBurboran

from UI.welcome_window_UI import WelcomeWindow

def main():
    app = QApplication(sys.argv)

    welcome = WelcomeWindow()
    welcome.show()

    def start_server():
        welcome.close()
        room_name = "LAN Chat Room"
        chat = LanBurboran(is_server=True, room_name=room_name)
        chat.window.show()

    def join_chat():
        welcome.close()
        chat = LanBurboran(is_server=False)
        chat.window.show()

    welcome.create_btn.clicked.connect(start_server)
    welcome.join_btn.clicked.connect(join_chat)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
