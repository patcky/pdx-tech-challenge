from models.package import Package
import logging

class App(object):
    def __init__(self, params: dict):
        self.table_name: str = "apps"
        self.id: int = params.get("id", None)
        self.name: str = params.get("name", None)
        self.package_id: int = params.get("package_id", None)

    def save(self, db):
        """Save app data to the database."""
        try:
            db.save_object_to_db(params=vars(self))
        except:
            logging.error("Error saving app data to db.")
            raise
