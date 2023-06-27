# Steam storefront API ETL

## Overview

This app is written in Python 3.11.4. It's function is to access the Steam storefront API, given a list of package IDs in a CSV file and, for each package, retrieve information about apps, price, platform and release dates.

Unofficial documentation for the Steam storefront API can be found [here](https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI#salepage).

All dependencies can be found with a version in the `requirements.txt` file.

The app works with multithreading in order to be more efficient in execution time. he number of threads is defined by the `REQUESTS_LIMIT` variable in the .env file, where you can also find the `STEAM_API_KEY` variable. By the API rules, there is a limit of 200 requests every 5 minutes, but for testing pruposes it is recommended to make fewer (5 should be enough to see results).

For some packages, the id is present but the data is not in the Steam API, so the API returns `"success": False` in the response payload. For these cases, the app saves an entry to the database with an error and all fields as `NULL`.

## Schema

The app saves all the data retrieved from the API in an Sqlite3 database, and also outputs a CSV file with the same content. The schema was built taking in consideration the most effective way to store the data from the API in a way that would also facilitate reading this data in the future.
It is faster and more efficient to query for individual fields than it would be to query for a JSON.

This is how the tables should look like:



Table: packages

| Column                  | Type     |
| ----------------------- | -------- |
| id                      | int      |
| error                   | bool     |
| price_currency          | text     |
| price_initial           | float    |
| price_final             | float    |
| price_discount_percent  | int      |
| price_individual        | float    |
| platforms_windows       | bool     |
| platforms_mac           | bool     |
| platforms_linux         | bool     |
| release_date_coming_soon| bool     |
| release_date_date       | date     |

Table: apps

| Column      | Type |
| ----------- | ---- |
| id          | int  |
| name        | text |
| package_id*  | int  |
| *(foreign key, references packages) |  |

## Running the app

To run it, make sure that all dependencies are installed and then run the `main.py` file. Using if `__name__ == "__main__"` in the main file is a way of storing code that should only run when the file is executed as a script, and not when it is imported as a module.

You also to add these items on your `.env` file:

```
STEAM_API_KEY=1CAFBF04B006D16AE985E3D02CCE1334
REQUESTS_LIMIT=5
ENVIRONMENT=development
INPUT_CSV_FILE_PATH=packages.csv
DB_PATH=steam.db
OUTPUT_PACKAGES_CSV_FILE_PATH=output/packages.csv
OUTPUT_APPS_CSV_FILE_PATH=output/apps.csv
```

## Technical debt

Some features that I considered implementing but didn't due to lack of time:

- Writing a docker-compose file with instructions on how to build the image and run it, in order to facilitate setup and running. Note that using Docker doesn't guarantee that it will work on other OS platforms, because unlike virtual machines, Docker still depends on the underlying OS for some resources.

- Abstracting more methods from inside some of the classes - when I started working on this, I first did a few tests on Postman. Then, I wrote a one-page script that did everything and made sure it worked. Only after that, I started refactoring, making tests, separating all the modules and creating classes. I am aware that there is still a lot of space for improvement, specially in terms of organisation of files, separation of concerns and responsibilitiees. As an example, I'd like to change the method `create_tables` in `db_connection.py`. It should be more abstracted and not just a big hard-coded SQL query. Another example is the function `thread_executor`, inside the `SteamApiAdapter()`. It would be better if this function was somewhere else, possibly in the `helpers.py`.

- Comments - I started this project commenting on almost every line. Then, I had a discussion about code comments with a friend and he mentioned that he thinks that if you need comments in the code, it means you could probably replace them with more express function and variable names and a clean code. I agreed with him and I believe it is a matter of preference. In this project, I've decided to keep the comments in the documentation. If this was a real application, I would talk to my team and decide together how to implement the comments.

- Using multiple SQL inserts in one command instead of individually inserting each row - I am aware that there is a way of inserting multiple rows in a table with only one command. I did not have enough time to implement this, as it would involve refactoring other parts of my code again.

- Writing more tests - and automating them. The more tests, the better.

- Using a clear pattern for structuring the code - When I started refactoring this app, I tried to go for something "Active Record-ish". Clearly, it takes a while to build it, if you have not already started building your code using it.
"Why didn't you use it from the beginning, then?"
I didn't want to have many external dependencies in my code and I also wanted to show that I had understanding about how this pattern works and that I can also do SQL queries "by hand" if needed.

- Git history - The commits are an absolute mess. I was planning on squashing them and cherry picking, writing more descriptive messages for the commits, such as `feature: implement multi threading for the http requests`. It would also have been nice to work with branches, instead of doing all the commits on main. The reason why I didn't do this is because it felt like I didn't have enough time to spend on these smaller things since I was focusing on making the application work and refactoring it, but looking back now, it would have spared me work in the end.

- Sharing API keys in a team setup - A common method for sharing secrets is to use environment variables in a .env file, as I did. In a team setup, each member would set up the same environment variable on their system. For sharing these keys, you can use a service like Vault by HashiCorp or AWS Secrets Manager, which are designed for securely storing and accessing secrets.

- Making the classes more unit testable - To make the classes more testable, I would use dependency injection. This involves passing dependencies (in this case, API key and any other required configuration) to the class when it's instantiated rather than the class getting them itself. This approach would allow me to provide mock dependencies when testing. For example, I could pass a mock API key and check how the class behaves without making actual API calls.

- DB schema evolution - For managing and evolving the database schema, it's best to use a database migration tool. These tools help to apply version control to your database schema, allowing to track changes, roll back if necessary, and ensure all team members are working with the same schema. Examples of db migration tools include Sqitch, Flyway, and Liquibase. [This](https://towardsdatascience.com/which-tool-should-you-use-for-database-migrations-4e0b9c44b790) is a good resource on the topic.

- Modeling the CSV saving functionality in OOP, so that it's not a helper - Would be very good to have a class called CsvWritter that implements a method save. Another option that’s more extensible is having interfaces like AppRepository and PackageRepository and have implementations for them: AppDbRepository, PackageDbRepository, AppCsvRepository and PackageCsvRepository each implementing the interface. Each saves the same data on a Database and a Csv but you have a single interface or contract definition for doing the same thing, so you can leverage polymorphism. This option also inverts the responsibility for saving moving it out of the models and into the Repository. This would promote code reusability and separation of concerns, where models are solely data holders and repositories handle data persistence.

- Improve isolation and make the tests more like "pure" unit tests - Mock the database connection using a library like unittest.mock. This way, instead of interacting with a real SQLite database, I would just simulate the behavior of the database and verify that the methods call the correct SQLite functions with the correct arguments. It's also important to make sure tests do not depend on each other. You should be able to run the tests in any order and they should all pass. Each test should set up its own state and clean up after itself, so it doesn't affect other tests.

- A note on the testing logic - the tests are validating if certain actions have an effect on the database (e.g., a record is created). This could lead to false positives if the logic inside the functions is not correct, but the database state is as expected due to some other reasons.

- Running the tests - instead of using `__name__ == '__main__': unittest.main()`, it would be better to run the tests using a test runner like pytest or the unittest test discovery, which allows you to just run python -m unittest or pytest in your terminal from the root directory of your project. This way, all files following the test file naming convention will be run, and you don't need a main block in each test file.
