import sys
import random
from PySide6.QtWidgets import QApplication, QInputDialog, QMessageBox
from lan_burboran import LanBurboran, discover_servers
from UI.welcome_window_UI import WelcomeWindow

DEFAULT_ROOM_NAME = "LAN Chat Room"


def close(welcome):
    welcome.close()


def start_room(room_name):
    chat = LanBurboran(
        is_server=True,
        room_name=room_name
    )
    chat.window.show()


def set_room_name():
    room_name, ok = QInputDialog.getText(
        None, "Име на стая", "Въведете име на стаята:", text=DEFAULT_ROOM_NAME)
    if not ok or not room_name.strip():
        room_name = DEFAULT_ROOM_NAME

    return room_name


def start_chat(room_name, server_ip, server_port, username):
    chat = LanBurboran(
        is_server=False,
        room_name=room_name,
        server_ip=server_ip,
        server_port=server_port,
        username=username
    )
    chat.window.show()


def choose_username(window):
    def generate_random_username():
        return f"User-{random.randint(1000, 9999)}"

    username = window.username_input.text().strip()
    if not username:
        username = generate_random_username()

    return username


def choose_room(rooms):
    items = [f"{i+1}. {s[0]} ({s[1]}:{s[2]})" for i,
             s in enumerate(rooms)]
    selected, ok = QInputDialog.getItem(
        None, "Избор на стая", "Изберете стая:", items, 0, False)
    if not ok:
        sys.exit(0)
    index = int(selected.split(".")[0]) - 1
    room_name, server_ip, server_port = rooms[index]

    return room_name, server_ip, server_port


def searching_for_rooms():
    rooms = discover_servers()
    if not rooms:
        QMessageBox.warning(None, "Няма стаи",
                            "Не са намерени стаи в мрежата.")
        sys.exit(0)

    return rooms


def main():
    app = QApplication(sys.argv)

    welcome = WelcomeWindow()
    welcome.show()

    def create_room():
        # close welcome window
        close(welcome)

        # set room name
        room_name = set_room_name()

        # start room
        start_room(room_name)

    def join_chat():
        # close welcome window
        close(welcome)

        # Searching for rooms
        rooms = searching_for_rooms()

        # Choose a room
        room_name, server_ip, server_port = choose_room(rooms)

        # Choose a name
        username = choose_username(welcome)

        # Start chat
        start_chat(room_name, server_ip, server_port, username)

    welcome.create_btn.clicked.connect(create_room)
    welcome.join_btn.clicked.connect(join_chat)

    app.exec()


if __name__ == "__main__":
    main()
