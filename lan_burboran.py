import socket
import threading
from datetime import datetime

import constants
from UI.lan_burboran_UI import LanBurboran_UI

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog
from PySide6.QtCore import Qt, Signal, QObject

# Config
UDP_PORT = 50000
BUFFER_SIZE = 1024
BROADCAST_ADDR = '255.255.255.255'
DISCOVERY_TIMEOUT = 2
START_TCP_PORT = 50001
DEFAULT_ROOM_NAME = "LAN Chat Room"


class SignalHandler(QObject):
    new_message = Signal(str)
    update_users = Signal(set)
    update_room_name = Signal(str)


class LanBurboran:
    def __init__(self, is_server=False, room_name=DEFAULT_ROOM_NAME, server_ip=None, server_port=None, username=None):
        self.window = QMainWindow()
        self.window_ui = LanBurboran_UI()
        self.window_ui.setupUi(self.window)

        self.is_server = is_server
        self.room_name = room_name
        self.users = set()
        self.tcp_clients = {}
        self.server_ip = server_ip
        self.server_port = server_port
        self.username = username
        self.tcp_sock = None
        self.system_name = f"User-{socket.gethostname()}"

        self.signals = SignalHandler()
        self.signals.new_message.connect(self.display_message)
        self.signals.update_users.connect(self.refresh_user_list)
        self.signals.update_room_name.connect(self.update_room_name)

        self.window_ui.send_btn.clicked.connect(self.send_message)
        self.window_ui.input.returnPressed.connect(self.handle_return_pressed)

        self.window_ui.switch_btn.clicked.connect(self.switch_room)

        if is_server:
            self.server_port = self.find_free_port()
            threading.Thread(target=self.run_udp_server, daemon=True).start()
            threading.Thread(target=self.run_tcp_server, daemon=True).start()
            self.window_ui.current_user_label.setText(
                f"Вие сте: {self.system_name} (СЪРВЪР)")
            self.window_ui.header.setStyleSheet(
                "background-color: lightgreen; font-weight: bold;")
        else:
            threading.Thread(target=self.run_tcp_client, daemon=True).start()

        self.stop_client = threading.Event()

    def handle_return_pressed(self):
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            # Shift + Enter
            self.window_ui.input.insert("\n")
        else:
            # Enter
            self.send_message()

    def find_free_port(self):
        port = START_TCP_PORT
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(("", port))
                s.close()
                return port
            except OSError:
                port += 1

    def ask_for_username(self):
        name, ok = QInputDialog.getText(
            self.window, "Избор на име", "Въведете потребителско име:",
            text=f"User-{socket.gethostname()}"
        )
        if ok and name.strip():
            return name.strip()
        return f"User-{socket.gethostname()}"

    def display_message(self, msg):
        self.window_ui.chat_view.append(msg)

    def refresh_user_list(self, users_set):
        self.users = users_set
        self.window_ui.user_list.clear()
        for u in sorted(users_set):
            self.window_ui.user_list.addItem(u)
        self.window_ui.header.setText(
            f"Стая: {self.room_name} • Онлайн: {len(self.users)}"
        )

    def update_room_name(self, new_name):
        self.room_name = new_name
        self.window_ui.header.setText(
            f"Стая: {self.room_name} • Онлайн: {len(self.users)}"
        )
        self.window.setWindowTitle(
            f"Стая: {self.room_name} • Онлайн: {len(self.users)}"
        )

    def send_message(self):
        text = self.window_ui.input.text().strip()
        if not text:
            return
        full = f"{self.username}: {text}"
        timestamped = f"{self.format_time()} {full}"
        self.display_message(timestamped)
        if self.is_server:
            self.broadcast_message(timestamped)
        else:
            if hasattr(self, 'tcp_sock'):
                try:
                    self.tcp_sock.sendall(full.encode())
                except:
                    self.signals.new_message.emit(
                        f"{constants.icons[1]} Сървърът не отговаря.")
        self.window_ui.input.clear()

    def switch_room(self):
        if self.is_server:
            QMessageBox.information(
                self.window, "Смяна на стая", "Сървърът не може да напусне своята стая.")
            return
        if hasattr(self, 'tcp_sock'):
            self.tcp_sock.close()
        servers = discover_servers()
        if not servers:
            QMessageBox.warning(self.window, "Няма стаи",
                                "Не са намерени стаи в мрежата.")
            return
        items = [f"{i+1}. {s[0]} ({s[1]}:{s[2]})" for i,
                 s in enumerate(servers)]
        selected, ok = QInputDialog.getItem(
            self.window, "Смени стая", "Изберете нова стая:", items, 0, False
        )
        if ok:
            index = int(selected.split(".")[0]) - 1
            room_name, server_ip, server_port = servers[index]
            self.room_name = room_name
            self.server_ip = server_ip
            self.server_port = server_port
            self.window_ui.chat_view.clear()
            self.users.clear()
            self.refresh_user_list(set())
            self.update_room_name(room_name)
            threading.Thread(target=self.run_tcp_client, daemon=True).start()

    def format_time(self):
        return datetime.now().strftime("[%H:%M]")

    def run_udp_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_sock.bind(("", UDP_PORT))
            while True:
                msg, addr = udp_sock.recvfrom(BUFFER_SIZE)
                if msg.decode() == "DISCOVER_SERVER":
                    response = f"SERVER_HERE:{self.room_name}:{self.server_port}"
                    udp_sock.sendto(response.encode(), addr)

    def run_tcp_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_sock.bind(("", self.server_port))
            tcp_sock.listen()
            print(f"TCP сървър стартиран на порт {self.server_port}...")
            while True:
                client_sock, addr = tcp_sock.accept()
                print(f"Нов клиент: {addr}")
                threading.Thread(target=self.handle_client, args=(
                    client_sock, addr), daemon=True).start()

    def handle_client(self, client_sock, addr):
        with client_sock:
            try:
                proposed_name = client_sock.recv(BUFFER_SIZE).decode()
                full_username = f"{proposed_name} ({addr[0]})"
                counter = 1
                unique_username = full_username
                while unique_username in self.users:
                    unique_username = f"{full_username}#{counter}"
                    counter += 1
                self.users.add(unique_username)
                self.tcp_clients[client_sock] = unique_username
                self.signals.update_users.emit(self.users.copy())
                self.broadcast_user_list()
                join_msg = f"{self.format_time()} {constants.icons[0]} {unique_username} влезе в стаята."
                self.broadcast_message(join_msg)
                self.display_message(join_msg)
            except:
                return

            while True:
                try:
                    msg = client_sock.recv(BUFFER_SIZE)
                    if not msg:
                        break
                    decoded = f"{self.format_time()} {msg.decode()}"
                    self.signals.new_message.emit(decoded)
                    self.broadcast_message(decoded, exclude=client_sock)
                except ConnectionResetError:
                    break

            leave_msg = f"{self.format_time()} {constants.icons[4]} {unique_username} напусна стаята."
            self.broadcast_message(leave_msg)
            self.display_message(leave_msg)
            self.users.remove(unique_username)
            del self.tcp_clients[client_sock]
            self.signals.update_users.emit(self.users.copy())
            self.broadcast_user_list()

    def broadcast_message(self, message, exclude=None):
        for client in list(self.tcp_clients.keys()):
            if client != exclude:
                try:
                    client.sendall(message.encode())
                except:
                    pass

    def broadcast_user_list(self):
        user_list_str = "|".join(sorted(self.users))
        for client in self.tcp_clients.keys():
            try:
                client.sendall(f"UPDATE_USER_LIST:{user_list_str}".encode())
            except:
                pass

    def run_tcp_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            try:
                tcp_sock.connect((self.server_ip, self.server_port))
                tcp_sock.sendall(self.username.encode())
                self.tcp_sock = tcp_sock
                self.window_ui.current_user_label.setText(
                    f"Вие сте: {self.username}")
                while not self.stop_client.is_set():
                    msg = tcp_sock.recv(BUFFER_SIZE)
                    if not msg:
                        break
                    decoded = msg.decode()
                    if decoded.startswith("UPDATE_USER_LIST:"):
                        user_str = decoded.split(":", 1)[1]
                        self.signals.update_users.emit(
                            set(user_str.split("|")))
                    else:
                        self.signals.new_message.emit(decoded)
            except ConnectionRefusedError:
                self.signals.new_message.emit(
                    f"{constants.icons[4]} Сървърът не отговаря.")


def discover_servers():
    found_servers = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_sock.settimeout(DISCOVERY_TIMEOUT)
        udp_sock.sendto("DISCOVER_SERVER".encode(), (BROADCAST_ADDR, UDP_PORT))
        while True:
            try:
                msg, server_addr = udp_sock.recvfrom(BUFFER_SIZE)
                response = msg.decode()
                if response.startswith("SERVER_HERE:"):
                    parts = response.split(":")
                    room_name, tcp_port = parts[1], int(parts[2])
                    found_servers.append((room_name, server_addr[0], tcp_port))
            except socket.timeout:
                break
    return found_servers
