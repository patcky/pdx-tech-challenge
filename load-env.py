def load_config() -> dict:
    """Load the config from .env file"""
    load_dotenv()

    STEAM_API_KEY = os.environ.get("STEAM_API_KEY"),
    REQUESTS_LIMIT = int(os.environ.get("REQUESTS_LIMIT")),
    # "DB_PATH": os.environ.get("DB_PATH"),
    # "CSV_PATH": os.environ.get("CSV_PATH"),

    if not REQUESTS_LIMIT or not STEAM_API_KEY:
        raise Exception("Missing one or more environment variables.")
