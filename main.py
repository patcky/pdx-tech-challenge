import time
import logging

import pandas

from steam_api_adapter import SteamApiAdapter
from load_env import Config
from db_connection import DBConnection
from models.package import Package
from models.app import App


def main():
    """Read the CSV file, get the package data from the Steam API
    and save it to an Sqlite3 database."""

    start_time = time.time()

    config = Config()

    df: pandas.DataFrame = pandas.read_csv(config.csv_file_path)
    db = DBConnection(config.db_path)

    if config.environment == "development":
        db.delete_db_if_exists()

    db.create_db_if_not_exists()
    db.create_tables()

    adapter = SteamApiAdapter(config.adapter_config())
    responses = adapter.thread_executor(df)
    for http_response in responses:
        response = http_response.result()
        package = Package(params=response)
        package.save(db=db)
        if package.error:
            continue

        apps = response.get(next(iter(response))).get("data").get("apps")
        for app in apps:
            app["package_id"] = package.id
            App(params=app).save(db=db)

    db.commit_changes()
    db.close_connection()

    execution_time: float = time.time() - start_time
    print(f"Finished! This took {execution_time} seconds.")

if __name__ == "__main__":
    main()
