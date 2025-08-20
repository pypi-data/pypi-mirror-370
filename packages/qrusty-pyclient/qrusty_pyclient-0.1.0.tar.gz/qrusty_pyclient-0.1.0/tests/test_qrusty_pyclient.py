import unittest
from unittest.mock import patch
from qrusty_pyclient import QrustyClient


class TestQrustyClient(unittest.TestCase):
    def setUp(self):
        self.client = QrustyClient(base_url="http://localhost:3000")

    @patch("qrusty_pyclient.requests.post")
    def test_publish(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"id": "msg-1"}
        resp = self.client.publish(
            queue="orders", priority=100, payload={"order_id": 123}
        )
        self.assertEqual(resp["id"], "msg-1")

    @patch("qrusty_pyclient.requests.get")
    def test_stats(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"queues": [], "summary": {}}
        resp = self.client.stats()
        self.assertIn("queues", resp)
        self.assertIn("summary", resp)


if __name__ == "__main__":
    unittest.main()
