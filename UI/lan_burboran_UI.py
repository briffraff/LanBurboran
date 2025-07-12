from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QListWidget, QLineEdit, QPushButton, QLabel


class LanBurboran_UI(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("LAN Бърборан")

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.header = QLabel("Стая: Седянка • Онлайн: 1")
        layout.addWidget(self.header)

        main_layout = QHBoxLayout()
        self.user_list = QListWidget()
        self.chat_view = QTextEdit()
        self.chat_view.setReadOnly(True)
        main_layout.addWidget(self.user_list, 1)
        main_layout.addWidget(self.chat_view, 3)
        layout.addLayout(main_layout)

        bottom = QHBoxLayout()
        self.input = QLineEdit()
        self.send_btn = QPushButton("Изпрати")
        bottom.addWidget(self.input)
        bottom.addWidget(self.send_btn)
        layout.addLayout(bottom)

        central_widget.setLayout(layout)
        MainWindow.setCentralWidget(central_widget)
