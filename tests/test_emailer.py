import unittest
from unittest.mock import Mock, patch

from monitor import emailer


class EmailerTests(unittest.TestCase):
    @patch("monitor.emailer.smtplib.SMTP")
    def test_send_email_supports_multiple_recipients(self, mock_smtp):
        server = Mock()
        mock_smtp.return_value.__enter__.return_value = server
        smtp = {
            "host": "smtp.example.org",
            "port": 587,
            "user": "sender@example.org",
            "password": "secret",
            "to": ["ops@example.org", "alerts@example.org"],
        }

        emailer.send_email("Alert", "Body", [], smtp)

        mock_smtp.assert_called_once_with("smtp.example.org", 587)
        server.starttls.assert_called_once_with()
        server.login.assert_called_once_with("sender@example.org", "secret")
        message = server.send_message.call_args.args[0]
        self.assertEqual(message["To"], "ops@example.org, alerts@example.org")
        self.assertEqual(message["From"], "sender@example.org")
        self.assertEqual(message["Subject"], "Alert")


if __name__ == "__main__":
    unittest.main()
