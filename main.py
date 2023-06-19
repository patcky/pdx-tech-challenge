import time
import logging

import pandas

from steam_api_adapter import SteamApiAdapter
from load_env import Config
from db_connection import DBConnection
from models.package import Package
from models.app import App
from helpers import save_to_csv


def main():
    """Read the CSV file, get the package data from the Steam API
    and save it to an Sqlite3 database."""

    start_time = time.time()

    config = Config()

    df: pandas.DataFrame = pandas.read_csv(config.input_csv_file_path)
    db = DBConnection(config.db_path)

    if config.environment == "development":
        db.delete_db_if_exists()

    db.create_db_if_not_exists()
    db.create_tables()

    adapter = SteamApiAdapter(config.adapter_config())
    responses = adapter.thread_executor(df)

    packages = []
    apps = []

    for http_response in responses:
        response = http_response.result()
        package = Package(params=response)
        package.save(db=db)
        packages.append(vars(package))

        if package.error:
            continue

        package_apps = response.get(next(iter(response))).get("data").get("apps")
        for package_app in package_apps:
            package_app["package_id"] = package.id
            app = App(params=package_app)
            app.save(db=db)
            apps.append(vars(app))

    # import pdb; pdb.set_trace()
    save_to_csv(data=packages, file_path=config.output_packages_csv_file_path)
    save_to_csv(data=apps, file_path=config.output_apps_csv_file_path)

    db.commit_changes()
    db.close_connection()

    execution_time: float = time.time() - start_time
    print(f"Finished! This took {execution_time} seconds.")


if __name__ == "__main__":
    main()
