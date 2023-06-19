import sqlite3
import os
import logging

class DBConnection(object):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def create_db_if_not_exists(self):
        """Create the sqlite database if it doesn't exist and return a connection to it."""
        try:
            conn: sqlite3.Connection = sqlite3.connect(self.db_path)
            self.conn = conn
        except:
            logging.error("Error creating db.")
            raise

    def save_object_to_db(self, params: dict):
        """Save an object to the database."""
        try:
            table_name = params.get("table_name")
            del params["table_name"]

            for key, value in params.items():
                if value is None:
                    setattr(self, key, "NULL")

            query = (
                f"INSERT INTO {table_name} ("
                + ", ".join(params.keys())
                + ") VALUES ("
                + ", ".join(["?"] * len(params.keys()))
                + ")"
            )
            self.conn.execute(query, tuple(params.values()))
        except:
            logging.error("Error saving object to db.")
            raise

    def commit_changes(self):
        """Commit changes to the database."""
        try:
            self.conn.commit()
        except:
            logging.error("Error committing changes to db.")
            raise

    def delete_db_if_exists(self):
        """Delete the sqlite database if it exists."""
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except:
            logging.error("Error deleting db.")
            raise

    def close_connection(self):
        """Close the connection to the database."""
        try:
            self.conn.close()
        except:
            logging.error("Error closing db connection.")
            raise

    def create_tables(self):
        """Create the tables in the sqlite database."""
        try:
            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS packages
                (
                    id INTEGER PRIMARY KEY,
                    price_currency TEXT,
                    price_initial INTEGER,
                    price_final INTEGER,
                    price_discount_percent INTEGER,
                    price_individual INTEGER,
                    platforms_windows BOOLEAN,
                    platforms_mac BOOLEAN,
                    platforms_linux BOOLEAN,
                    release_date_coming_soon BOOLEAN,
                    release_date_date DATE,
                    error BOOLEAN DEFAULT FALSE
                )"""
            )

            self.conn.execute(
                """CREATE TABLE IF NOT EXISTS apps
                (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    package_id INTEGER,
                    FOREIGN KEY(package_id) REFERENCES packages(id)
                )"""
            )

        except:
            logging.error("Error creating tables.")
            raise
