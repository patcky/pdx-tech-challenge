import unittest
from .db_connection import DBConnection

class TestDBConnection(unittest.TestCase):
    def setUp(self):
        self.db = DBConnection(":memory:")
        self.db.create_db_if_not_exists()
        self.db.create_tables()

    def test_create_db_if_not_exists(self):
        self.assertIsNotNone(self.db.conn)

    def test_create_tables(self):
        self.db.create_tables()
        self.assertIsNotNone(self.db.conn.execute("SELECT * FROM packages"))
        self.assertIsNotNone(self.db.conn.execute("SELECT * FROM apps"))

    def test_save_object_to_db(self):
        self.db.save_object_to_db({
            "table_name": "packages",
            "id": 1,
            "name": "test",
            "error": None,
        })
        self.db.commit_changes()
        self.assertIsNotNone(self.db.conn.execute("SELECT * FROM packages WHERE id=1"))

    def test_commit_changes(self):
        self.db.save_object_to_db({
            "table_name": "packages",
            "id": 1,
            "name": "test",
            "error": None,
        })
        self.db.commit_changes()
        self.assertIsNotNone(self.db.conn.execute("SELECT * FROM packages WHERE id=1"))

    def test_delete_db_if_exists(self):
        self.db.delete_db_if_exists()
        self.assertIsNone(self.db.conn)

    def test_close_connection(self):
        self.db.close_connection()
        self.assertIsNone(self.db.conn)

if __name__ == '__main__':
    unittest.main()
