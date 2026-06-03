import unittest
from unittest.mock import Mock, patch

from monitor import checks


class CheckTests(unittest.TestCase):
    @patch("monitor.checks.requests.get")
    def test_check_url_marks_http_200_success(self, mock_get):
        mock_get.return_value = Mock(status_code=200)

        result = checks.check_url("https://example.org")

        self.assertEqual(result["status"], "Success")
        self.assertEqual(result["status_code"], 200)

    @patch("monitor.checks.ALLOW_403_FOR", {"example.org"})
    @patch("monitor.checks.requests.get")
    def test_check_url_allows_configured_403_domain(self, mock_get):
        mock_get.return_value = Mock(status_code=403)

        result = checks.check_url("https://docs.example.org/private")

        self.assertEqual(result["status"], "Success (403 allowed)")
        self.assertEqual(result["status_code"], 403)

    @patch("monitor.checks.logging.error")
    @patch("monitor.checks.requests.get")
    def test_check_url_returns_failed_on_exception(self, mock_get, mock_logging_error):
        mock_get.side_effect = TimeoutError("slow")

        result = checks.check_url("https://example.org")

        self.assertEqual(result["status"], "Failed")
        self.assertIn("slow", result["error"])
        mock_logging_error.assert_called_once()

    @patch("monitor.checks.check_url")
    def test_check_named_urls_preserves_input_order(self, mock_check_url):
        mock_check_url.side_effect = lambda url: {
            "url": url,
            "status": "Success",
            "status_code": 200,
            "error": None,
        }

        results = checks.check_named_urls(
            {
                "FIRST": "https://first.example.org",
                "SECOND": "https://second.example.org",
            },
            max_workers=2,
        )

        self.assertEqual([result["name"] for result in results], ["FIRST", "SECOND"])


if __name__ == "__main__":
    unittest.main()
