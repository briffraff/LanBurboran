import unittest
from unittest.mock import patch, MagicMock
import welcome


class TestWelcome(unittest.TestCase):
    def test_generate_random_username_when_empty(self):
        """Ако не е въведено име ще генерира случайно"""
        mock_window = MagicMock()
        mock_window.username_input.text.return_value = ""

        username = welcome.choose_username(mock_window)

        self.assertTrue(username.startswith("User-"))
        self.assertEqual(len(username), 9)  # User-1234

    def test_choose_username_with_input(self):
        """Ако е въведено име го връща"""
        mock_window = MagicMock()
        mock_window.username_input.text.return_value = "Гошо"

        username = welcome.choose_username(mock_window)
        self.assertEqual(username, "Гошо")

    @patch('welcome.QInputDialog.getText', return_value=("TestRoom", True))
    def test_set_room_name_with_input(self, mock_getText):
        """Връща въведено име на стая"""
        room_name = welcome.set_room_name()
        self.assertEqual(room_name, "TestRoom")

    @patch('welcome.QInputDialog.getText', return_value=("", False))
    def test_set_room_name_default_if_cancelled(self, mock_getText):
        """Ако е натиснат cancel връща DEFAULT_ROOM_NAME"""
        room_name = welcome.set_room_name()
        self.assertEqual(room_name, welcome.DEFAULT_ROOM_NAME)

    @patch('welcome.discover_servers', return_value=[
        ("TestRoom", "127.0.0.1", 50001)
    ])
    def test_searching_for_rooms_returns_list(self, mock_discover):
        """Връща списък със стаи, ако са намерени"""
        rooms = welcome.searching_for_rooms()
        self.assertEqual(len(rooms), 1)
        self.assertEqual(rooms[0][0], "TestRoom")

    @patch('welcome.discover_servers', return_value=[])
    @patch('welcome.QMessageBox.warning')
    @patch('sys.exit')
    def test_searching_for_rooms_exits_if_none(self, mock_exit, mock_warning, mock_discover):
        """Ако няма намерени стаи ще покаже предупреждение и излиза"""
        welcome.searching_for_rooms()
        mock_warning.assert_called_once_with(
            None, "Няма стаи", "Не са намерени стаи в мрежата."
        )
        mock_exit.assert_called_once()

    @patch('welcome.QInputDialog.getItem', return_value=("1. TestRoom (127.0.0.1:50001)", True))
    def test_choose_room_selects_correct_room(self, mock_getItem):
        """Връща избраната стая"""
        rooms = [("TestRoom", "127.0.0.1", 50001)]
        room_name, server_ip, server_port = welcome.choose_room(rooms)
        self.assertEqual(room_name, "TestRoom")
        self.assertEqual(server_ip, "127.0.0.1")
        self.assertEqual(server_port, 50001)

    @patch('welcome.QInputDialog.getItem', return_value=("1. TestRoom (127.0.0.1:50001)", False))
    @patch('sys.exit')
    def test_choose_room_exits_on_cancel(self, mock_exit, mock_getItem):
        """Ако потребителят отказва избор на стая ще излезе"""
        rooms = [("TestRoom", "127.0.0.1", 50001)]
        welcome.choose_room(rooms)
        mock_exit.assert_called_once()

    @patch('welcome.LanBurboran')
    def test_start_chat_calls_LanBurboran(self, mock_LanBurboran):
        """Вика стартиране на чат ,като клиент"""
        welcome.start_chat("Room1", "127.0.0.1", 50001, "Гошо")
        mock_LanBurboran.assert_called_once_with(
            is_server=False,
            room_name="Room1",
            server_ip="127.0.0.1",
            server_port=50001,
            username="Гошо"
        )

    @patch('welcome.LanBurboran')
    def test_start_room_calls_LanBurboran(self, mock_LanBurboran):
        """Вика стартиране на чат, като сървър"""
        welcome.start_room("Room1")
        mock_LanBurboran.assert_called_once_with(
            is_server=True,
            room_name="Room1"
        )


if __name__ == "__main__":
    unittest.main()
