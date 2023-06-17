import json
import pandas
import requests
import sqlite3
import os
import concurrent.futures
import time

# time counter
start_time = time.time()

# get steam api key from .env variable
key = os.getenv("STEAM_API_KEY")

# open csv file and read the content
df: pandas.DataFrame = pandas.read_csv("packages.csv")

# delete database if it exists. doing this for debugging purposes.
if os.path.exists("steam.db"):
    os.remove("steam.db")

# create sqlite database
conn: sqlite3.Connection = sqlite3.connect("steam.db")

# create table for storing package data, with id, price (json), platforms (json) and release_date (json)
# still not sure if it's better to separate everything in different tables, since the challenge didn't say anything about it
conn.execute(
    "CREATE TABLE IF NOT EXISTS packages (id INTEGER PRIMARY KEY, price JSON, platforms JSON, release_date JSON)"
)

# create table for storing apps data, with id and name as columns and package_id as foreign key to the packages table. #
# one package can have many apps but an app can only belong to one package (I think)
conn.execute(
    "CREATE TABLE IF NOT EXISTS apps (id INTEGER PRIMARY KEY, name TEXT, package_id INTEGER, FOREIGN KEY(package_id) REFERENCES packages(id))"
)

def get_package_data(package_id: int) -> dict:
    """Get package data from steam api and return it as a dict"""
    return requests.get("http://store.steampowered.com/api/packagedetails/",
                        params={
                            "packageids": package_id,
                            "key": key
                        }).json()

with concurrent.futures.ThreadPoolExecutor() as executor:

    concurrent_http_requests = []

    # for each row of the csv, excluding the header, do a get request to "http://store.steampowered.com/api/salepage/" passing the package id as a parameter in the request.
    for index, row in df.iterrows():
        print(index)

        # impose a limit of 5 rows for the iteration, since there is a limit of requests per 5 minutes in the api
        if index > 0 and index % 5 == 0: # type: ignore
            break
        # get the response and parse it as json
        concurrent_http_requests.append(
            executor.submit(get_package_data,
                            package_id=int(row["PACKAGEID"])))

    for http_request in concurrent.futures.as_completed(concurrent_http_requests):
        result = http_request.result()
        package_id = next(iter(result))
        # if the package id is not found, the api returns success: False
        if not result[package_id]["success"]:
            # save an entry to db as an error
            conn.execute(
                "INSERT INTO packages (id, price, platforms, release_date) VALUES (?, ?, ?, ?)",
                (package_id, "", "", ""))
            continue

        data = result[package_id]["data"]

        # save apps, price, platforms, release_date in the respective tables, incrementally
        # the id of the package is the same as the package id in the csv
        conn.execute(
            "INSERT INTO packages (id, price, platforms, release_date) VALUES (?, ?, ?, ?)",
            (package_id, json.dumps(data["price"]),
             json.dumps(data["platforms"]), json.dumps(data["release_date"])))

        # for each app in the package, save the app id and name in the apps table
        for app in data["apps"]:
            app_id = app["id"]
            app_name = app["name"]
            conn.execute("INSERT INTO apps (id, name, package_id) VALUES (?, ?, ?)",
                            (app_id, app_name, package_id))

# commit changes to the database
conn.commit()

# close connection to the database
conn.close()

# print the time it took to run the script
execution_time: float = time.time() - start_time
print(f'Finished! This took {execution_time} seconds.')
