import unittest
from anges.utils.parse_response import parse_response_text

class TestParseResponseText(unittest.TestCase):
    def test_single_tag(self):
        response_text = """
KEY_WORD_TAG::TAG1::START
This is some content.
KEY_WORD_TAG::TAG1::END
"""
        expected = {"TAG1": "This is some content."}
        self.assertEqual(parse_response_text(response_text), expected)

    def test_multiple_tags(self):
        response_text = """
KEY_WORD_TAG::TAG1::START
Content for tag 1.KEY_WORD_TAG::TAG1::END
KEY_WORD_TAG::TAG2::START
Content for tag 2.
KEY_WORD_TAG::TAG2::END
"""
        expected = {"TAG1": "Content for tag 1.", "TAG2": "Content for tag 2."}
        self.assertEqual(parse_response_text(response_text), expected)

    def test_nested_tags(self):
        response_text = """
KEY_WORD_TAG::OUTER::START
Outer content
KEY_WORD_TAG::INNER::START
Nested content.
KEY_WORD_TAG::INNER::END
KEY_WORD_TAG::OUTER::END
"""
        expected = {"OUTER": "Outer content\nKEY_WORD_TAG::INNER::START\nNested content.\nKEY_WORD_TAG::INNER::END"}
        self.assertEqual(parse_response_text(response_text), expected)

    def test_unmatched_end_tag(self):
        response_text = """
KEY_WORD_TAG::TAG1::START
Some content.
KEY_WORD_TAG::TAG1::END
KEY_WORD_TAG::TAG2::END
"""
        with self.assertRaises(ValueError) as context:
            parse_response_text(response_text)
        self.assertEqual(str(context.exception), "Unmatched tags found")

    def test_unmatched_start_tag(self):
        response_text = """
KEY_WORD_TAG::TAG1::START
Some content.
"""
        with self.assertRaises(ValueError) as context:
            parse_response_text(response_text)
        self.assertEqual(str(context.exception), "Unmatched tags found")

    def test_content_outside_tags(self):
        response_text = """
Content outside of tags.
KEY_WORD_TAG::TAG1::START
Valid content.
KEY_WORD_TAG::TAG1::END
"""
        expected = {"TAG1": "Valid content."}
        self.assertEqual(parse_response_text(response_text), expected)

    def test_empty_content_between_tags(self):
        response_text = """
KEY_WORD_TAG::TAG1::START

KEY_WORD_TAG::TAG1::END
"""
        expected = {"TAG1": ""}
        self.assertEqual(parse_response_text(response_text), expected)

    def test_multiple_lines_with_whitespace(self):
        response_text = """
KEY_WORD_TAG::TAG1::START
    line1
  line2  
    line3
KEY_WORD_TAG::TAG1::END
"""
        expected = {"TAG1": "    line1\n  line2  \n    line3"}
        self.assertEqual(parse_response_text(response_text), expected)

    def test_special_characters(self):
        response_text = """
KEY_WORD_TAG::TAG1::START
Special chars: !@#$%^&*()_+
Multiple lines with \n
Tab\t and spaces
KEY_WORD_TAG::TAG1::END
"""
        expected = {"TAG1": "Special chars: !@#$%^&*()_+\nMultiple lines with \n\nTab\t and spaces"}
        self.assertEqual(parse_response_text(response_text), expected)

if __name__ == "__main__":
    unittest.main()
