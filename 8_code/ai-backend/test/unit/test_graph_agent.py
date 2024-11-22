import unittest

from core.agent.graph_agent import extract_text


class TestGraphAgent(unittest.TestCase):

    def test_extract_text_with_string(self):
        response = "This is a string"
        result = extract_text(response)
        self.assertEqual(result, "This is a string")

    def test_extract_text_with_empty_list(self):
        response = []
        result = extract_text(response)
        self.assertEqual(result, "")

    def test_extract_text_with_list_of_dicts(self):
        response = [{"text": "Let", "type": "text", "index": 0}]
        result = extract_text(response)
        self.assertEqual(result, "Let")

    def test_extract_text_with_invalid_list(self):
        response = [{"type": "text", "index": 0}]
        result = extract_text(response)
        self.assertEqual(result, "")

    def test_extract_text_with_other_type(self):
        response = 12345
        result = extract_text(response)
        self.assertEqual(result, "")

if __name__ == '__main__':
    unittest.main()