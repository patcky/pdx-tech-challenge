import concurrent.futures
import json
import logging
import requests

import pandas

class SteamApiAdapter():
    def __init__(self, params: dict):
        self.steam_api_key: str = params["steam_api_key"]
        self.requests_limit: int = params["requests_limit"]
        self.environment: int = params["environment"]

    def get_package_data(self, package_id: int) -> dict:
        """Get package data from Steam API and return it as a dict"""
        generic_error_message = "Error getting package data from Steam API."
        try:
            response = requests.get(
                "http://store.steampowered.com/api/packagedetails/",
                params={"packageids": package_id, "key": self.steam_api_key},
            )
        except requests.exceptions.RequestException as e:
            logging.error(generic_error_message, "Connection error", e)
            raise e

        if response.status_code in [range(400, 499)]:
            logging.error(
                "Bad request", response
            )
            raise Exception(generic_error_message, "Bad request")

        elif response.status_code in [range(500, 599)]:
            logging.error(
                generic_error_message, "Server error", response
            )
            raise Exception("Server error")

        if not response.json():
            logging.error(
                generic_error_message, "Empty response from Steam API",
                response,
            )
            raise Exception("Empty response from Steam API")

        return response.json()

    def thread_executor(self, df: pandas.DataFrame):
        """Execute the HTTP requests concurrently using threads."""

        with concurrent.futures.ThreadPoolExecutor() as executor:
            concurrent_http_requests = []
            concurrent_db_inserts = []

            for index, row in df.iterrows():
                logging.info(f">{index}")
                if index > 0 and index % self.requests_limit == 0:
                    if self.environment == "development":
                        break
                    time.sleep(300)

                concurrent_http_requests.append(
                    executor.submit(
                        self.get_package_data,
                        package_id=int(row["PACKAGEID"]),
                    )
                )

            return concurrent.futures.as_completed(concurrent_http_requests)
