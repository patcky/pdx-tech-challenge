import json
import pandas
import requests
import sqlite3
import os
import concurrent.futures
import time
from dotenv import load_dotenv


def main():
    """This reads the csv file, gets the package data from the steam api
    and saves it to a sqlite database. It uses multithreading to speed up the
    process. The number of threads is defined by the REQUESTS_LIMIT variable in
    the .env file, where you can also find the STEAM_API_KEY variable.If the
    package id is present but the data is not in the steam API, it saves an
    entry to the database with an error."""

    def get_package_data(package_id: int) -> dict:
        """Get package data from steam api and return it as a dict"""
        response = requests.get(
            "http://store.steampowered.com/api/packagedetails/",
            params={"packageids": package_id, "key": key},
        )

        if response.status_code in [range(400, 499)]:
            raise Exception("Error getting package data from steam api - Bad request")

        elif response.status_code in [range(500, 599)]:
            raise Exception("Error getting package data from steam api - Server error")

        return response.json()

    def save_package_data_to_db(package_id: int, result) -> None:
        """Save the result of the http request to sqlite database. If the
        package data was not found by the steam api, save an entry to the
        database with an error."""

        # if the package id is not found, the api returns success: False
        if not result[package_id]["success"]:
            # save an entry to db as an error and skip the rest of the function
            conn.execute(
                "INSERT INTO packages (id, error) VALUES (?, ?)", (package_id, True)
            )
            return

        data = result[package_id]["data"]

        # save apps, price, platforms, release_date in the respective tables, incrementally
        # the id of the package is the same as the package id in the csv
        conn.execute(
            "INSERT INTO packages (id, price, platforms, release_date) VALUES (?, ?, ?, ?)",
            (
                package_id,
                json.dumps(data["price"]),
                json.dumps(data["platforms"]),
                json.dumps(data["release_date"]),
            ),
        )

        # for each app in the package, save the app id and name in the apps table
        for app in data["apps"]:
            conn.execute(
                "INSERT INTO apps (id, name, package_id) VALUES (?, ?, ?)",
                (app["id"], app["name"], package_id),
            )

    # time counter
    start_time = time.time()

    # load environment variables from .env file
    load_dotenv()

    # get steam api key from .env variable
    key = os.getenv("STEAM_API_KEY")

    # get limit of concurrent http requests from .env variable
    requests_limit = int(os.getenv("REQUESTS_LIMIT"))

    # open csv file and read the content
    df: pandas.DataFrame = pandas.read_csv("packages.csv")

    # delete database if it exists. doing this for debugging purposes.
    if os.path.exists("steam.db"):
        os.remove("steam.db")

    # create sqlite database and connect to it #
    conn: sqlite3.Connection = sqlite3.connect("steam.db")

    # create table for storing package data, with id as primary key and price,
    # platforms and release_date as json columns. #
    # still not sure if it's better to separate everything in different tables,
    # since the challenge didn't say anything about it
    conn.execute(
        """CREATE TABLE IF NOT EXISTS packages
        (
            id INTEGER PRIMARY KEY,
            price JSON,
            platforms JSON,
            release_date JSON,
            error BOOLEAN DEFAULT FALSE
        )"""
    )

    # create table for storing apps data, with id and name as columns and
    # package_id as foreign key to the packages table. #
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

    with concurrent.futures.ThreadPoolExecutor() as executor:
        concurrent_http_requests = []
        concurrent_db_inserts = []

        # iterate over the df rows and get the package data from the steam api #
        for index, row in df.iterrows():
            print(index)
            # limit to 5 requests per 5 minutes according to the api #
            if index > 0 and index % requests_limit == 0:
                break  # remove this line when in production mode
                time.sleep(300)

            # create a concurrent task to get the package data from the steam api #
            concurrent_http_requests.append(
                executor.submit(get_package_data, package_id=int(row["PACKAGEID"]))
            )

        # wait for all concurrent tasks to finish  and save the results to the database #
        for http_response in concurrent.futures.as_completed(concurrent_http_requests):
            package_id = next(iter(http_response.result()))
            save_package_data_to_db(
                package_id=package_id, result=http_response.result()
            )

    # commit changes to the database and close connection #
    conn.commit()
    conn.close()

    # print the time it took to run the script
    execution_time: float = time.time() - start_time
    print(f"Finished! This took {execution_time} seconds.")


# using if __name__ == "__main__" is a way of storing code that should only run
# when this file is executed as a script, and not when it is imported as a module
if __name__ == "__main__":
    main()
