import unittest
from .steam_api_adapter import SteamApiAdapter

class TestSteamApiAdapter(unittest.TestCase):
    def setUp(self):
        self.config = {
            "STEAM_API_KEY": "FAKE_API_KEY",
            "REQUESTS_LIMIT": 5,
            "ENVIRONMENT": "development",
        }
        self.adapter = SteamApiAdapter(self.config)

    def test_get_package_data(self):
        package_id = 1
        response = self.adapter.get_package_data(package_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("success"), True)

    def test_thread_executor(self):
        df = self.adapter.read_csv_file("data/steam.csv")
        responses = self.adapter.thread_executor(df)
        self.assertEqual(len(responses), 5)
        for response in responses:
            self.assertEqual(response.result().status_code, 200)
            self.assertEqual(response.result().json().get("success"), True)

if __name__ == '__main__':
    unittest.main()
