import os
import unittest
from unittest.mock import patch

from monitor import config


class ConfigTests(unittest.TestCase):
    def test_parse_email_recipients_accepts_commas_and_semicolons(self):
        recipients = config.parse_email_recipients(
            "ops@example.org, alerts@example.org; admin@example.org "
        )

        self.assertEqual(
            recipients,
            ["ops@example.org", "alerts@example.org", "admin@example.org"],
        )

    @patch.dict(
        os.environ,
        {
            "EMAIL_HOST": "smtp.example.org",
            "EMAIL_PORT": "2525",
            "EMAIL_USER": "sender@example.org",
            "EMAIL_PASS": "secret",
            "EMAIL_TO": "ops@example.org,alerts@example.org",
        },
        clear=True,
    )
    def test_get_smtp_config_returns_normalized_values(self):
        smtp = config.get_smtp_config()

        self.assertEqual(smtp["host"], "smtp.example.org")
        self.assertEqual(smtp["port"], 2525)
        self.assertEqual(smtp["to"], ["ops@example.org", "alerts@example.org"])

    @patch.dict(
        os.environ,
        {
            "EMAIL_HOST": "smtp.example.org",
            "EMAIL_USER": "sender@example.org",
            "EMAIL_PASS": "secret",
            "EMAIL_TO": "",
        },
        clear=True,
    )
    def test_get_smtp_config_requires_at_least_one_recipient(self):
        with self.assertRaisesRegex(config.ConfigError, "EMAIL_TO"):
            config.get_smtp_config()

    @patch.dict(
        os.environ,
        {
            "URL_OBI_HOME": "https://obi.example.org",
            "URL_OBI_DEV": "https://dev.obi.example.org",
            "URL_CDL_HOME": "https://cdl.example.org",
            "DISABLED_GROUPS": "obi",
        },
        clear=True,
    )
    def test_get_named_urls_excludes_disabled_groups(self):
        self.assertEqual(
            config.get_named_urls(),
            {"CDL_HOME": "https://cdl.example.org"},
        )


if __name__ == "__main__":
    unittest.main()
