import time
import logging

import pandas

from steam_API_adapter import SteamApiAdapter
from load_env import load_config
from db_connection import (
    delete_db_if_exists,
    create_db_if_not_exists,
    create_tables,
    save_package_data_to_db,
    commit_changes_and_close_connection,
)


def main():
    """Read the CSV file, get the package data from the Steam API
    and save it to an Sqlite3 database."""

    config = load_config()

    steam_api_key = config["STEAM_API_KEY"]
    requests_limit = config["REQUESTS_LIMIT"]
    environment = config["ENVIRONMENT"]
    csv_file_path = config["CSV_FILE_PATH"]
    db_path = config["DB_PATH"]

    start_time = time.time()

    df: pandas.DataFrame = pandas.read_csv(csv_file_path)

    delete_db_if_exists(db_path)
    conn = create_db_if_not_exists(db_path)
    create_tables(conn)

    adapter_params = {
        "steam_api_key": steam_api_key,
        "requests_limit": requests_limit,
        "environment": environment,
    }
    adapter = SteamApiAdapter(adapter_params)
    responses = adapter.thread_executor(df)
    for http_response in responses:
        package_id = next(iter(http_response.result()))
        save_package_data_to_db(
            package_id=package_id, result=http_response.result(), conn=conn
        )

    commit_changes_and_close_connection(conn)

    execution_time: float = time.time() - start_time
    print(f"Finished! This took {execution_time} seconds.")

if __name__ == "__main__":
    main()
