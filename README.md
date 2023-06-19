# Steam storefront API ETL

## Overview

This app is written in Python 3.11.4. It's function is to access the Steam storefront API, given a list of package IDs in a CSV file and, for each package, retrieve information about apps, price, platform and release dates.

Unofficial documentation for the Steam storefront API can be found [here](https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI#salepage).

All dependencies can be found with a version in the \`requirements.txt\` file.

The app works with multithreading in order to be more efficient in execution time. he number of threads is defined by the \`REQUESTS_LIMIT\` variable in the .env file, where you can also find the \`STEAM_API_KEY\` variable. By the API rules, there is a limit of 200 requests every 5 minutes, but for testing pruposes it is recommended to make fewer (5 should be enough to see results).

For some packages, the id is present but the data is not in the Steam API, so the API returns \`"success"\`: False in the response payload. For these cases, the app saves an entry to the database with an error and all fields as \`NULL`\.

## Schema

The app saves all the data retrieved from the API in an Sqlite3 database, and also outputs a CSV file with the same content. The schema was built taking in consideration the most effective way to store the data from the API in a way that would also facilitate reading this data in the future.
It is faster and more efficient to query for individual fields than it would be to query for a JSON.

This is how the tables should look like:




## Running the app

To run it, make sure that all dependencies are installed and then run the \`main.py\` file. Using if \`__name__ == "__main__"\` in the main file is a way of storing code that should only run when the file is executed as a script, and not when it is imported as a module.

## Technical debt

Some features that I considered implementing but didn't due to lack of time:

- Writing a docker-compose file with instructions on how to build the image and run it, in order to facilitate setup and running. Note that using Docker doesn't guarantee that it will work on other OS platforms, because unlike virtual machines, Docker still depends on the underlying OS for some resources.

- Abstracting more methods from inside some of the classes - when I started working on this, I first did a few tests on Postman. Then, I wrote a one-page script that did everything and made sure it worked. Only after that, I started refactoring, making tests, separating all the modules and creating classes. I am aware that there is still a lot of space for improvement, specially in terms of organisation of files, separation of concerns and responsibilitiees.

As an example, I'd like to change the method \`create_tables\` in \`db_connection.py\`. It should be more abstracted and not just a big hard-coded SQL query.

- Comments - I started this project commenting on almost every line. Then, I had a discussion about code comments with a friend and he mentioned that he thinks that if you need comments in the code, it means you could probably replace them with more express function and variable names and a clean code. I agreed with him and I believe it is a matter of preference. In this project, I've decided to keep the comments in the documentation. If this was a real application, I would talk to my team and decide together how to implement the comments.

- Using multiple SQL inserts in one command instead of individually inserting each row - I am aware that there is a way of inserting multiple rows in a table with only one command. I did not have enough time to implement this, as it would involve refactoring other parts of my code again.

- Writing more tests - and automating them.
