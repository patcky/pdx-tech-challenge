import sqlite3
import logging
from datetime import datetime, date


class Package(object):
    def __init__(self, params: dict):
        self.table_name: str = "packages"

        self.id: int = next(iter(params))
        params: dict = params.get(str(self.id))

        self.error: bool = not params.get("success") | False
        data: dict = params.get("data", {})

        price: dict = data.get("price", {})
        self.price_currency: str = price.get("currency", None)
        self.price_initial: float = price.get("initial", None)
        self.price_final: float = price.get("final", None)
        self.price_discount_percent: int = price.get("discount_percent", None)
        self.price_individual: float = price.get("individual", None)

        platforms: dict = data.get("platforms", {})
        self.platforms_windows: bool = platforms.get("platforms_windows", None)
        self.platforms_mac: bool = platforms.get("platforms_mac", None)
        self.platforms_linux: bool = platforms.get("platforms_linux", None)

        release_date: dict = data.get("release_date", {})
        self.release_date_coming_soon: bool = release_date.get("coming_soon", None)
        self.release_date_date: date = release_date.get("date", None)
        if self.release_date_date:
            self.release_date_date = datetime.strptime(
                self.release_date_date, "%d %b, %Y"
            ).strftime("%Y-%m-%d")

    def save(self, db):
        """Save package data to the database."""
        try:
            db.save_object_to_db(params=vars(self))
        except:
            logging.error("Error saving package data to db.")
            raise
