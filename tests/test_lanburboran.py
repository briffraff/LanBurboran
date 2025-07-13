import unittest
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication
from lan_burboran import LanBurboran
import constants

app = QApplication([])


class TestLanBurboran(unittest.TestCase):
    def setUp(self):
        patcher_getText = patch(
            'lan_burboran.QInputDialog.getText', return_value=("Гошо", True)
        )
        patcher_getText.start()
        self.addCleanup(patcher_getText.stop)

        patcher_thread = patch('lan_burboran.threading.Thread', MagicMock())
        patcher_thread.start()
        self.addCleanup(patcher_thread.stop)

        patcher_discover = patch('lan_burboran.discover_servers', return_value=[
            ("TestRoom", "127.0.0.1", 50001)
        ])
        patcher_discover.start()
        self.addCleanup(patcher_discover.stop)

        self.lanburboran = LanBurboran(is_server=False)

    def tearDown(self):
        self.lanburboran.window.close()

    def test_refresh_user_list(self):
        test_users = {"user1", "user2"}
        self.lanburboran.refresh_user_list(test_users)
        self.assertEqual(self.lanburboran.window_ui.user_list.count(), 2)
        self.assertIn("Онлайн: 2", self.lanburboran.window_ui.header.text())

    @patch('lan_burboran.QMessageBox.information')
    def test_switch_room_as_server_shows_popup(self, mock_info):
        with patch('lan_burboran.threading.Thread', MagicMock()):
            server = LanBurboran(is_server=True)
            server.switch_room()
            mock_info.assert_called_once_with(
                server.window,
                "Смяна на стая",
                "Сървърът не може да напусне своята стая."
            )

    def test_send_message_no_server(self):
        self.lanburboran.username = "Гошо"
        self.lanburboran.window_ui.input.setText("Тест!")

        self.lanburboran.tcp_sock = None
        self.lanburboran.send_message()

        last_message = self.lanburboran.window_ui.chat_view.toPlainText(
        ).strip().split("\n")[-1]

        self.assertEqual(
            last_message, f"{constants.icons[1]} Сървърът не отговаря.")

    @patch('lan_burboran.QMessageBox.warning')
    def test_switch_room_no_servers_shows_warning(self, mock_warning):
        self.lanburboran.tcp_sock = MagicMock()
        with patch('lan_burboran.discover_servers', return_value=[]):
            self.lanburboran.switch_room()
        mock_warning.assert_called_once_with(
            self.lanburboran.window,
            "Няма стаи",
            "Не са намерени стаи в мрежата."
        )

    @patch('lan_burboran.QInputDialog.getItem', return_value=("1. TestRoom (127.0.0.1:50001)", True))
    def test_switch_room_as_client_changes_room(self, mock_getItem):
        self.lanburboran.tcp_sock = MagicMock()
        self.lanburboran.switch_room()
        self.assertEqual(self.lanburboran.room_name, "TestRoom")
        self.assertIn("TestRoom", self.lanburboran.window_ui.header.text())

    def test_send_message(self):
        self.lanburboran.username = "Гошо"
        self.lanburboran.window_ui.input.setText("Тест!")

        self.lanburboran.tcp_sock = MagicMock()
        self.lanburboran.send_message()

        last_message = self.lanburboran.window_ui.chat_view.toPlainText(
        ).strip().split("\n")[-1].split(" ", 1)[1]

        self.assertEqual(last_message, "Гошо: Тест!")


if __name__ == "__main__":
    unittest.main()
