import sqlite3
import os

def delete_db_if_exists(db_path):
    """Delete the sqlite database if it exists."""
    if os.path.exists(db_path):
        os.remove(db_path)


def create_db_if_not_exists(db_path):
    """Create the sqlite database if it doesn't exist and return a connection to it."""

    # create sqlite database and connect to it #
    conn: sqlite3.Connection = sqlite3.connect(db_path)
    return conn

def create_tables(conn):
    """Create the tables in the sqlite database."""

    # create table for storing package data
    conn.execute(
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
            release_date DATE,
            error BOOLEAN DEFAULT FALSE
        )"""
    )

    # create table for storing apps data, with a foreign key to the packages table.
    # one package can have many apps but an app can only belong to one package #
    conn.execute(
        """CREATE TABLE IF NOT EXISTS apps
        (
            id INTEGER PRIMARY KEY,
            name TEXT,
            package_id INTEGER,
            FOREIGN KEY(package_id) REFERENCES packages(id)
        )"""
    )
