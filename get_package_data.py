import requests
import json
import logging


def get_package_data(package_id: int, steam_api_key: str) -> dict:
    """Get package data from Steam API and return it as a dict"""
    generic_error_message = "Error getting package data from Steam API."
    try:
        response = requests.get(
            "http://store.steampowered.com/api/packagedetails/",
            params={"packageids": package_id, "key": steam_api_key},
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
