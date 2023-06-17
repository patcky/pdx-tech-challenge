import concurrent.futures
import json
import os
import time
import logging

from dotenv import load_dotenv
import pandas
import requests
import sqlite3


def get_package_data(package_id: int, steam_api_key: str) -> dict:
    """Get package data from Steam API and return it as a dict"""
    response = requests.get(
        "http://store.steampowered.com/api/packagedetails/",
        params={"packageids": package_id, "key": steam_api_key},
    )

    if response.status_code in [range(400, 499)]:
        # add logging here
        raise Exception("Error getting package data from Steam API - Bad request")

    elif response.status_code in [range(500, 599)]:
        # add logging here
        raise Exception("Error getting package data from Steam API - Server error")

    return response.json()


def save_package_data_to_db(package_id: int, result: dict, conn: sqlite3.Connection) -> None:
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

    data = result[package_id]["data"] # create an object to store the data


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
            data["release_date"]["date"],
        ),
    )

    # for each app in the package, save the app id and name in the apps table
    for app in data["apps"]:
        conn.execute(
            "INSERT INTO apps (id, name, package_id) VALUES (?, ?, ?)",
            (app["id"], app["name"], package_id),
        )


def main():
    """This reads the csv file, gets the package data from the Steam API
    and saves it to a sqlite database. It uses multithreading to speed up the
    process. The number of threads is defined by the \`REQUESTS_LIMIT\` variable in
    the .env file, where you can also find the \`STEAM_API_KEY\` variable.If the
    package id is present but the data is not in the Steam API, it saves an
    entry to the database with an error."""

    # time counter
    start_time = time.time()

    # load environment variables from .env file
    load_dotenv()

    # get Steam api key from .env variable
    steam_api_key = os.getenv("STEAM_API_KEY")

    # get limit of concurrent http requests from .env variable
    requests_limit = int(os.getenv("REQUESTS_LIMIT"))

    if not requests_limit or not steam_api_key:
        raise Exception("Missing one or more environment variables.")

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
