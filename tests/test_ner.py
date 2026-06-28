import unittest

from src.ner import EntityExtractor


class EntityExtractorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = EntityExtractor()

    def test_extracts_software_device_system_location_and_error_code(self) -> None:
        text = "Outlook on Windows failed with HTTP 500 on laptop in meeting room."

        entities = self.extractor.extract(text)
        pairs = {(entity.text.lower(), entity.label) for entity in entities}

        self.assertIn(("outlook", "SOFTWARE"), pairs)
        self.assertIn(("windows", "SOFTWARE"), pairs)
        self.assertIn(("http 500", "ERROR_CODE"), pairs)
        self.assertIn(("laptop", "DEVICE"), pairs)
        self.assertIn(("meeting room", "LOCATION"), pairs)

    def test_prefers_longer_phrases(self) -> None:
        entities = self.extractor.extract("Please enable access card for the conference room.")
        pairs = [(entity.text.lower(), entity.label) for entity in entities]

        self.assertIn(("access card", "DEVICE"), pairs)
        self.assertIn(("conference room", "LOCATION"), pairs)
        self.assertNotIn(("card", "DEVICE"), pairs)
        self.assertNotIn(("room", "LOCATION"), pairs)

    def test_empty_text_returns_no_entities(self) -> None:
        self.assertEqual(self.extractor.extract("   "), [])

    def test_generic_error_text_is_not_error_code(self) -> None:
        entities = self.extractor.extract("The application failed and an error occurred.")

        self.assertNotIn("ERROR_CODE", {entity.label for entity in entities})


if __name__ == "__main__":
    unittest.main()
