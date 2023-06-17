import requests
import json

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

    if not response.json():
        # add logging here
        raise Exception("Error getting package data from Steam API - No data")

    return response.json()
