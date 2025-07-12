import unittest
from PySide6.QtWidgets import QApplication
from lan_burboran import LanBurboran

app = QApplication([])


class TestLanBurboran(unittest.TestCase):
    def setUp(self):
        self.lanburboran = LanBurboran()

    def test_refresh_user_list(self):
        test_users = {"user1", "user2"}
        self.lanburboran.refresh_user_list(test_users)
        self.assertEqual(self.lanburboran.window_ui.user_list.count(), 2)
        self.assertEqual(self.lanburboran.window_ui.header.text(),
                         "Стая: LAN Chat Room • Онлайн: 2")

    def tearDown(self):
        self.lanburboran.window.close()


if __name__ == "__main__":
    unittest.main()
