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
        self.assertEqual(result["attempts"], 1)
        self.assertIsInstance(result["response_time_ms"], int)

    @patch("monitor.checks.ALLOW_403_FOR", {"example.org"})
    @patch("monitor.checks.requests.get")
    def test_check_url_allows_configured_403_domain(self, mock_get):
        mock_get.return_value = Mock(status_code=403)

        result = checks.check_url("https://docs.example.org/private")

        self.assertEqual(result["status"], "Success (403 allowed)")
        self.assertEqual(result["status_code"], 403)
        self.assertEqual(result["attempts"], 1)

    @patch("monitor.checks.logging.error")
    @patch("monitor.checks.requests.get")
    def test_check_url_returns_failed_on_exception(self, mock_get, mock_logging_error):
        mock_get.side_effect = TimeoutError("slow")

        result = checks.check_url("https://example.org", retries=0)

        self.assertEqual(result["status"], "Failed")
        self.assertIn("slow", result["error"])
        self.assertEqual(result["attempts"], 1)
        mock_logging_error.assert_called_once()

    @patch("monitor.checks.time.sleep")
    @patch("monitor.checks.requests.get")
    def test_check_url_retries_before_returning_http_failure(self, mock_get, mock_sleep):
        mock_get.side_effect = [Mock(status_code=500), Mock(status_code=500), Mock(status_code=500)]

        result = checks.check_url("https://example.org", retries=2, retry_delay=0.1)

        self.assertEqual(result["status"], "HTTP 500")
        self.assertEqual(result["attempts"], 3)
        self.assertEqual(mock_get.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("monitor.checks.check_url")
    def test_check_named_urls_preserves_input_order(self, mock_check_url):
        mock_check_url.side_effect = lambda url, **kwargs: {
            "url": url,
            "status": "Success",
            "status_code": 200,
            "error": None,
            "response_time_ms": 12,
            "attempts": 1,
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
