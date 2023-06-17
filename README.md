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
