import json
import pandas
import requests
import sqlite3
import os
import asyncio
import time

# get steam api key from .env variable
key = os.getenv("STEAM_API_KEY")

# time counter
start_time = time.time()

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

# implement async requests to the code
# https://stackoverflow.com/zquestions/45216663/how-to-make-multiple-requests-using-asyncio-in-python-3-6

# for each row of the csv, excluding the header, do a get request to "http://store.steampowered.com/api/salepage/" passing the package id as a parameter in the request.
for index, row in df.iterrows():
    print(index)
    package_id = int(row["PACKAGEID"])
    # impose a limit of 5 rows for the iteration, since there is a limit of requests per 5 minutes in the api
    if index > 0 and index % 5 == 0: # type: ignore
        break
    # get the response and parse it as json
    response = requests.get("http://store.steampowered.com/api/packagedetails/",
                     params={
                         "packageids": package_id,
                         "key": key
                     }).json()[str(package_id)]
    print(response)
    # if the package id is not found, the api returns success: False
    if not response["success"]:
        # save an entry to db as an error
        continue
    data = response["data"]

    #print(data)
    apps = data["apps"]
    price = data["price"]
    platforms = data["platforms"]
    release_date = data["release_date"]

    # save apps, price, platforms, release_date in the respective tables, incrementally
    # the id of the package is the same as the package id in the csv
    conn.execute(
        "INSERT INTO packages (id, price, platforms, release_date) VALUES (?, ?, ?, ?)",
        (package_id, json.dumps(price), json.dumps(platforms),
         json.dumps(release_date)))
    # for each app in the package, save the app id and name in the apps table
    for app in apps:
        app_id = app["id"]
        app_name = app["name"]
        conn.execute("INSERT INTO apps (id, name, package_id) VALUES (?, ?, ?)",
                        (app_id, app_name, package_id))

conn.commit()

execution_time = round(time.time() - start_time, 2)

print(f'Finished! This took {execution_time} seconds.')
