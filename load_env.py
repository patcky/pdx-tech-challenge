import os
import logging
from dotenv import load_dotenv
from http.client import HTTPConnection

class Config(object):
    def __init__(self):
        try:
            load_dotenv()
            self.steam_api_key: str = os.environ.get("STEAM_API_KEY")
            self.requests_limit: int = int(os.environ.get("REQUESTS_LIMIT"))
            self.environment: str = os.environ.get("ENVIRONMENT")
            self.input_csv_file_path: str = os.environ.get("INPUT_CSV_FILE_PATH")
            self.db_path: str = os.environ.get("DB_PATH")
            self.output_packages_csv_file_path: str = os.environ.get("OUTPUT_PACKAGES_CSV_FILE_PATH")
            self.output_apps_csv_file_path: str = os.environ.get("OUTPUT_APPS_CSV_FILE_PATH")
            if self.environment == "development":
                self.turn_on_logging_for_development_env()
        except:
            logging.error("Error loading config.")
            raise

    def turn_on_logging_for_development_env(self) -> None:
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

    def adapter_config(self) -> dict:
        """Return a dict with the config for the adapter."""
        return {
            "STEAM_API_KEY": self.steam_api_key,
            "REQUESTS_LIMIT": self.requests_limit,
            "ENVIRONMENT": self.environment,
        }
