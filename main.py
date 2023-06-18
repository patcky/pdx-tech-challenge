# Standard library imports
import concurrent.futures
import json
import os
import time
import logging

# Third party imports
import pandas
import requests
import sqlite3

# Local application imports
from get_package_data import get_package_data
from load_env import load_config
from db_connection import delete_db_if_exists, create_db_if_not_exists, create_tables, save_package_data_to_db


def main():
    """This reads the csv file, gets the package data from the Steam API
    and saves it to a sqlite database. It uses multithreading to speed up the
    process. The number of threads is defined by the \`REQUESTS_LIMIT\` variable in
    the .env file, where you can also find the \`STEAM_API_KEY\` variable.If the
    package id is present but the data is not in the Steam API, it saves an
    entry to the database with an error."""

    config = load_config()

    steam_api_key = config["STEAM_API_KEY"]
    requests_limit = config["REQUESTS_LIMIT"]
    environment = config["ENVIRONMENT"]
    csv_file_path = config["CSV_FILE_PATH"]
    db_path = config["DB_PATH"]

    # time counter
    start_time = time.time()

    # open csv file and read the content
    df: pandas.DataFrame = pandas.read_csv(csv_file_path)

    # delete the database if it exists
    delete_db_if_exists(db_path)
    conn = create_db_if_not_exists(db_path)
    create_tables(conn)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        concurrent_http_requests = []
        concurrent_db_inserts = []

        # iterate over the df rows and get the package data from the Steam api #
        for index, row in df.iterrows():
            print(index)
            # limit to 5 requests per 5 minutes according to the api #
            if index > 0 and index % requests_limit == 0:
                break  # remove this line when in production mode
                time.sleep(300)

            # create a concurrent task to get the package data from the Steam api #
            concurrent_http_requests.append(
                executor.submit(
                    get_package_data,
                    package_id=int(row["PACKAGEID"]),
                    steam_api_key=steam_api_key,
                )
            )

        # wait for all concurrent tasks to finish  and save the results to the database #
        for http_response in concurrent.futures.as_completed(concurrent_http_requests):
            package_id = next(iter(http_response.result()))
            save_package_data_to_db(
                package_id=package_id, result=http_response.result(), conn=conn
            )

    # commit changes to the database and close connection #
    conn.commit()
    conn.close()

    # print the time it took to run the script
    execution_time: float = time.time() - start_time
    print(f"Finished! This took {execution_time} seconds.")


# using if \`__name__ == "__main__"\` is a way of storing code that should only run
# when this file is executed as a script, and not when it is imported as a module
if __name__ == "__main__":
    main()
