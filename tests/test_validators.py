"""Unit tests for input parsing and prompt validation functions."""

import unittest
from unittest.mock import patch
from inventory_cli.cli.validators import (
    prompt_string,
    prompt_float,
    prompt_int,
    prompt_confirm,
    prompt_choice,
)

class TestValidators(unittest.TestCase):
    """Test suite for CLI prompt validation functions."""

    @patch("builtins.input", side_effect=["  PROD-123  "])
    def test_prompt_string_normal(self, mock_input):
        val = prompt_string("Enter SKU", to_upper=True)
        self.assertEqual(val, "PROD-123")

    @patch("builtins.input", side_effect=["", "fallback"])
    def test_prompt_string_empty_retry(self, mock_input):
        val = prompt_string("Enter name", min_len=1)
        self.assertEqual(val, "fallback")

    @patch("builtins.input", side_effect=[""])
    def test_prompt_string_default(self, mock_input):
        val = prompt_string("Enter name", default="Standard")
        self.assertEqual(val, "Standard")

    @patch("builtins.input", side_effect=["not-a-number", "-5", "19.99"])
    def test_prompt_float_with_min(self, mock_input):
        val = prompt_float("Enter price", min_val=0.01)
        self.assertEqual(val, 19.99)

    @patch("builtins.input", side_effect=[""])
    def test_prompt_float_allow_blank(self, mock_input):
        val = prompt_float("Enter price", allow_blank=True)
        self.assertIsNone(val)

    @patch("builtins.input", side_effect=["3.14", "10"])
    def test_prompt_int_retry_on_float(self, mock_input):
        val = prompt_int("Enter quantity", min_val=0)
        self.assertEqual(val, 10)

    @patch("builtins.input", side_effect=["maybe", "Y"])
    def test_prompt_confirm_yes(self, mock_input):
        self.assertTrue(prompt_confirm("Confirm?"))

    @patch("builtins.input", side_effect=["no"])
    def test_prompt_confirm_no(self, mock_input):
        self.assertFalse(prompt_confirm("Confirm?"))

    @patch("builtins.input", side_effect=["", ""])
    def test_prompt_confirm_default(self, mock_input):
        self.assertFalse(prompt_confirm("Confirm?", default=False))
        self.assertTrue(prompt_confirm("Confirm?", default=True))

    @patch("builtins.input", side_effect=["99", "2"])
    def test_prompt_choice(self, mock_input):
        val = prompt_choice("Pick an option", ["Alpha", "Beta", "Gamma"])
        self.assertEqual(val, "Beta")

if __name__ == "__main__":
    unittest.main()
