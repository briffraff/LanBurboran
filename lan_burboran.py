import sys
import socket
import threading

import constants
from UI.lan_burboran_UI import LanBurboran_UI
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QInputDialog)
from PySide6.QtCore import Qt, Signal, QObject

UDP_PORT = 50000
TCP_PORT = 50001
BUFFER_SIZE = 1024
BROADCAST_ADDR = '255.255.255.255'
# USERNAME = f'User-{socket.gethostname()}'


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
        self.tcp_clients = {}
        self.server_ip = None
        self.username = None
        self.signals = SignalHandler()
        self.signals.new_message.connect(self.display_message)
        self.signals.update_users.connect(self.refresh_user_list)

        self.window_ui.send_btn.clicked.connect(self.send_message)

        if is_server:
            threading.Thread(target=self.run_udp_server, daemon=True).start()
            threading.Thread(target=self.run_tcp_server, daemon=True).start()
        else:
            self.username = self.ask_for_username()
            threading.Thread(target=self.run_udp_client, daemon=True).start()

    def ask_for_username(self):
        name, ok = QInputDialog.getText(
            self.window,
            "Избор на име",
            "Въведете потребителско име:",
            text=f'User-{socket.gethostname()}'
        )
        if ok and name.strip():
            return name.strip()
        return f'User-{socket.gethostname()}'

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
        full = f"{self.username}: {text}"
        self.display_message(full)
        if self.is_server:
            self.broadcast_message(full)
        else:
            if hasattr(self, 'tcp_sock'):
                try:
                    self.tcp_sock.sendall(full.encode())
                except:
                    self.signals.new_message.emit(
                        f"{constants.icons[1]} Сървърът не отговаря.")
        self.window_ui.input.clear()

    def run_udp_server(self):
        # receive requests and send responses
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_sock.bind(("", UDP_PORT))
            while True:
                msg, addr = udp_sock.recvfrom(BUFFER_SIZE)
                if msg.decode() == "DISCOVER_SERVER":
                    udp_sock.sendto("SERVER_HERE".encode(), addr)

    def run_tcp_server(self):
        # start TCP server and handle client connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_sock.bind(("", TCP_PORT))
            tcp_sock.listen()
            print("TCP сървър стартиран...")
            while True:
                client_sock, addr = tcp_sock.accept()
                client_sock.setsockopt(
                    socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                print(f"Нов клиент: {addr}")
                threading.Thread(target=self.handle_client, args=(
                    client_sock, addr), daemon=True).start()

    def broadcast_message(self, message, exclude=None):
        for client in self.tcp_clients:
            if client != exclude:
                try:
                    client.sendall(message.encode())
                except:
                    pass

    def run_udp_client(self):
        # send UDP broadcast and listen for server response
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_sock.settimeout(3)
            udp_sock.sendto("DISCOVER_SERVER".encode(),
                            (BROADCAST_ADDR, UDP_PORT))
            try:
                msg, server_addr = udp_sock.recvfrom(BUFFER_SIZE)
                if msg.decode() == "SERVER_HERE":
                    self.server_ip = server_addr[0]
                    threading.Thread(
                        target=self.run_tcp_client, daemon=True).start()
            except socket.timeout:
                self.signals.new_message.emit(
                    f"{constants.icons[2]} Не е открит сървър в мрежата.")

    def run_tcp_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
            try:
                tcp_sock.connect((self.server_ip, TCP_PORT))
                tcp_sock.sendall(self.username.encode())

                try:
                    confirmed = tcp_sock.recv(BUFFER_SIZE).decode()
                    if confirmed.startswith("USERNAME_CONFIRMED:"):
                        self.username = confirmed.split(":", 1)[1]
                        self.signals.new_message.emit(
                            f"{constants.icons[3]} Вашето име е '{self.username}'"
                        )
                except ConnectionResetError:
                    self.signals.new_message.emit(
                        f"{constants.icons[4]} Връзката със сървъра бе прекъсната.")
                    return

                self.tcp_sock = tcp_sock
                while True:
                    msg = tcp_sock.recv(BUFFER_SIZE)
                    if not msg:
                        break
                    self.signals.new_message.emit(msg.decode())
            except ConnectionRefusedError:
                self.signals.new_message.emit(
                    f"{constants.icons[4]} Сървърът не отговаря.")


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
