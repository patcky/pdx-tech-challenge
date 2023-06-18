import os
import logging
from dotenv import load_dotenv
from http.client import HTTPConnection

def turn_on_logging_for_development_env() -> None:
    """Turn on logging for development environment"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler(),
        ],
    )
    HTTPConnection.debuglevel = 1

def load_config() -> dict:
    """Load the config from .env file"""
    load_dotenv()
    try:
        config = {
            "STEAM_API_KEY": os.environ.get("STEAM_API_KEY"),
            "REQUESTS_LIMIT": int(os.environ.get("REQUESTS_LIMIT")),
            "ENVIRONMENT": os.environ.get("ENVIRONMENT"),
            "CSV_FILE_PATH": os.environ.get("CSV_FILE_PATH"),
            "DB_PATH": os.environ.get("DB_PATH"),
        }
        if config["ENVIRONMENT"] == "development":
            turn_on_logging_for_development_env()
    except KeyError as e:
        logging.info(e)
        raise

    return config
