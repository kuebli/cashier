import unittest

from app.db.db import DB


class TestDB(unittest.TestCase):
    def setUp(self) -> None:
        self.db = DB(":memory:")

    def test_tables_exist(self):
        conn = self.db.connect()
        cur = conn.cursor()

        # check if table categories exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='categories'"
        )
        self.assertIsNotNone(cur.fetchone())

        # check if table articles exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='articles'"
        )
        self.assertIsNotNone(cur.fetchone())

        # check if table carts exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='carts'"
        )
        self.assertIsNotNone(cur.fetchone())

        conn.close()
