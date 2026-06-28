import unittest

import pandas as pd

from src.preprocessing.text import clean_ticket_text, normalize_ticket_series


class TextPreprocessingTest(unittest.TestCase):
    def test_clean_ticket_text_removes_url_and_email(self) -> None:
        text = "Please install VPN from https://example.com. Contact admin@example.com."

        cleaned = clean_ticket_text(text)

        self.assertNotIn("https", cleaned)
        self.assertNotIn("admin@example.com", cleaned)
        self.assertEqual(cleaned, "please install vpn from contact")

    def test_clean_ticket_text_preserves_technical_tokens(self) -> None:
        text = "Windows 11 error 0x80070005 on C:\\Temp\\app.exe"

        cleaned = clean_ticket_text(text)

        self.assertIn("windows 11", cleaned)
        self.assertIn("0x80070005", cleaned)
        self.assertIn("c:\\temp\\app.exe", cleaned)

    def test_normalize_ticket_series_handles_missing_values(self) -> None:
        series = pd.Series(["Need access", None])

        cleaned = normalize_ticket_series(series)

        self.assertEqual(cleaned.tolist(), ["need access", ""])


if __name__ == "__main__":
    unittest.main()
