import unittest

from tiny_r_fc_2047_word import decode, decode_header_value, decode_word


class DecodeWordTests(unittest.TestCase):
    def test_q_encoding_underscore_is_space(self):
        self.assertEqual(decode_word("utf-8", "Q", "Hello_World"), "Hello World")

    def test_q_encoding_hex_escapes(self):
        self.assertEqual(decode_word("utf-8", "Q", "caf=C3=A9"), "café")

    def test_b_encoding(self):
        self.assertEqual(decode_word("utf-8", "B", "Y2Fmw6k="), "café")

    def test_lowercase_encoding_letter(self):
        self.assertEqual(decode_word("utf-8", "b", "Y2Fmw6k="), "café")

    def test_unknown_charset_falls_back_to_latin1(self):
        # 0xE9 is not valid UTF-8 but is 'é' in latin-1.
        self.assertEqual(decode_word("x-unknown", "Q", "caf=E9"), "café")

    def test_invalid_encoding_letter_raises(self):
        with self.assertRaises(ValueError):
            decode_word("utf-8", "X", "abc")


class DecodeHeaderValueTests(unittest.TestCase):
    def test_plain_text_unchanged(self):
        self.assertEqual(decode_header_value("just a subject"), "just a subject")

    def test_single_encoded_word(self):
        self.assertEqual(
            decode_header_value("=?utf-8?Q?caf=C3=A9?="),
            "café",
        )

    def test_adjacent_encoded_words_join_without_space(self):
        self.assertEqual(
            decode_header_value("=?utf-8?Q?Hello?= =?utf-8?Q?World?="),
            "HelloWorld",
        )

    def test_whitespace_between_encoded_word_and_text_preserved(self):
        self.assertEqual(
            decode_header_value("=?utf-8?Q?Hello?= World"),
            "Hello World",
        )

    def test_undecodable_word_left_alone(self):
        # '=' is not valid base64 and '?' cannot appear in the body, so this
        # is not a well-formed encoded-word and must survive verbatim.
        original = "=?utf-8?B?not base64?="
        self.assertEqual(decode_header_value(original), original)

    def test_non_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            decode_header_value(None)

    def test_decode_alias(self):
        self.assertEqual(decode("=?utf-8?Q?ok?="), "ok")


if __name__ == "__main__":
    unittest.main()
