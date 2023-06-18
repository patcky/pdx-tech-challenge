import sqlite3
import os
from datetime import datetime

def commit_changes_and_close_connection(conn):
    """Commit changes to the database and close connection."""
    conn.commit()
    conn.close()

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
    try:
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

    except sqlite3.Error as e:
        logging.error("Error creating tables.", e)
        raise e

def save_package_data_to_db(
    package_id: int, result: dict, conn: sqlite3.Connection
) -> None:
    """Save the result of the http request to sqlite database. If the
    package data was not found by the Steam API, save an entry to the
    database with an error."""

    # if the package id is not found, the api returns success: False
    if not result[package_id]["success"]:
        # save an entry to db as an error and skip the rest of the function
        conn.execute(
            "INSERT INTO packages (id, error) VALUES (?, ?)", (package_id, True)
        )
        return

    data = result[package_id]["data"]  # create an object to store the data

    # save apps, price, platforms, release_date in the respective tables, incrementally
    # the id of the package is the same as the package id in the csv
    conn.execute(
        "INSERT INTO packages (id, price_currency, price_initial, price_final, price_discount_percent, price_individual, platforms_windows, platforms_mac, platforms_linux, release_date_coming_soon, release_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            package_id,
            data["price"]["currency"],
            data["price"]["initial"],
            data["price"]["final"],
            data["price"]["discount_percent"],
            data["price"]["individual"],
            data["platforms"]["windows"],
            data["platforms"]["mac"],
            data["platforms"]["linux"],
            data["release_date"]["coming_soon"],
            # convert the date to the format YYYY-MM-DD to be able to sort it easily
            datetime.strptime(data["release_date"]["date"], "%d %b, %Y").strftime(
                "%Y-%m-%d"
            ),
        ),
    )

    # for each app in the package, save the app id and name in the apps table
    for app in data["apps"]:
        conn.execute(
            "INSERT INTO apps (id, name, package_id) VALUES (?, ?, ?)",
            (app["id"], app["name"], package_id),
        )
