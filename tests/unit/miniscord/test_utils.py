from unittest import TestCase

from miniscord._utils import sanitize_input, parse_arguments


class TestSanitizeInput(TestCase):
    def test_no_change(self):
        self.assertEqual("abc 0_9", sanitize_input("abc 0_9"))

    def test_lower_trim(self):
        self.assertEqual("abc", sanitize_input("  ABC  "))

    def test_remove_special_chars(self):
        self.assertEqual("hello id  some command", sanitize_input("Hello <@id> ! `some command`"))


class TestParseArguments(TestCase):
    def test_empty(self):
        self.assertEqual([], parse_arguments(""))

    def test_single_arg(self):
        self.assertEqual(["abc"], parse_arguments("abc"))

    def test_multi_args(self):
        self.assertEqual(["abc", "def", "ghi"], parse_arguments("abc def ghi"))

    def test_quotes(self):
        self.assertEqual(["abc def"], parse_arguments("'abc def'"))

    def test_quotes_squotes(self):
        self.assertEqual(["abc 'def'"], parse_arguments("\"abc 'def'\""))

    def test_squotes(self):
        self.assertEqual(["abc def"], parse_arguments("\"abc def\""))

    def test_squotes_quotes(self):
        self.assertEqual(["\"abc\" def"], parse_arguments("'\"abc\" def'"))

    def test_complex(self):
        self.assertEqual(["abc 'def'", "ghi", "jkl mno"], parse_arguments("\"abc 'def'\" ghi 'jkl mno'"))
