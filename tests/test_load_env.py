import unittest
from . import Config


class TestLoadEnv(unittest.TestCase):
    def setUp(self):
        self.config = Config()

    def test_config(self):
        if not self.config.steam_api_key:
            raise AssertionError("Missing STEAM_API_KEY")
        self.assertEqual(self.config.requests_limit, 5)
        self.assertEqual(self.config.environment, "development")
        self.assertEqual(self.config.csv_file_path, "data/steam.csv")
        self.assertEqual(self.config.db_path, "data/steam.db")

    def test_adapter_config(self):
        self.assertEqual(
            self.config.adapter_config(),
            {
                "STEAM_API_KEY": self.config.steam_api_key,
                "REQUESTS_LIMIT": self.config.requests_limit,
                "ENVIRONMENT": self.config.environment,
            },
        )


if __name__ == "__main__":
    unittest.main()
