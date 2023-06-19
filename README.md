# pdx-tech-challenge

Please email a well documented code script with supporting comments in the code, 7 days after receiving this case.

Problem statement

You have been tasked with developing a new ETL to collect information about our products on the Steam Store. This can be done by using the Steam storefront API.

This is a public unsupported API and has no official documentation. Unofficial documentation can be found at the link below. Be aware that this documentation might not be 100% accurate.
https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI#salepage

In the zip file you will find a list of package IDs. For each one we want to retrieve the following details:

Apps
Price information
Platform
Release dates

- The script should be written in Python 3 (recommended packages Pandas and Requests).
- In order to replicate the load part of the script please use the sqlite3 python package to create a SQLite virtual database.
- The result should be loaded into SQlite tables, assuming that the data should be loaded incrementally.
- The final tables should be provided both as SQLite tables in the script but also CSV files.
- Part of the solution should be to think about how the data should be stored in a good way.


# Package information retrieval - TODOs:

Docs:
- mention multithreading in documentation
- explain that this was done on a mac so it might not work on other OS platforms
because unlike VMs, Docker still depends on the underlying OS for some resources
- compare to venv, which you can also use, but also doesn't guarantee successfull
replication on other OS
- mention thoughts about the schema in the documentation
- version the libs and explain why in the docs
- change the json fields to individual fields and comment why
- It uses multithreading to speed up the
    process. The number of threads is defined by the \`REQUESTS_LIMIT\` variable in
    the .env file, where you can also find the \`STEAM_API_KEY\` variable.If the
    package id is present but the data is not in the Steam API, it saves an
    entry to the database with an error.
- using if \`__name__ == "__main__"\` is a way of storing code that should only run when the file is executed as a script, and not when it is imported as a module
- limit to 5 requests per 5 minutes according to the api

Logging and exception treatment:
- add tests
- add more typing support

Facilitate setup and running:
- write a docker-compose file with instructions on how to build the image and run it

Refactor:
- separate one file for API calls
- use models for validation of data
