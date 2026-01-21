# Unit tests for money amount parsing and validation.

import pytest
from src.utils.money_words import parse_money_words, format_money
from src.validate.rules import validate_amount_consistency
from src.validate.errors import AmountMismatchError

class TestMoneyWordParser:
    # Tests for parsing money words to numbers.
    def test_parse_one_million(self):
        assert parse_money_words("One Million") == 1_000_000.0

    def test_parse_one_million_two_hundred_thousand(self):
        result = parse_money_words("One Million Two Hundred Thousand")
        assert result == 1_200_000.0

    def test_parse_with_dollars_suffix(self):
        result = parse_money_words("One Million Two Hundred Thousand Dollars")
        assert result == 1_200_000.0

    def test_parse_five_hundred_thousand(self):
        assert parse_money_words("Five Hundred Thousand") == 500_000.0

    def test_parse_one_hundred(self):
        assert parse_money_words("One Hundred") == 100.0

    def test_parse_twenty_five(self):
        assert parse_money_words("Twenty Five") == 25.0

    def test_parse_empty_text(self):
        with pytest.raises(ValueError):
            parse_money_words("")

    def test_parse_invalid_word(self):
        with pytest.raises(ValueError):
            parse_money_words("foo bar baz")


class TestAmountValidation:
    # Tests for amount consistency validation.
    def test_matching_amounts_pass(self):
        validate_amount_consistency(
            1_200_000.0,
            "One Million Two Hundred Thousand"
        )

    def test_small_discrepancy_within_tolerance(self):
        validate_amount_consistency(
            1_200_500.0,
            "One Million Two Hundred Thousand",
            tolerance=1000.0
        )

    def test_large_discrepancy_fails(self):
        with pytest.raises(AmountMismatchError) as exc_info:
            validate_amount_consistency(
                1_250_000.0,  
                "One Million Two Hundred Thousand",  
                tolerance=1000.0
            )

        error_msg = str(exc_info.value)
        assert "1,250,000" in error_msg
        assert "1,200,000" in error_msg
        assert "50,000" in error_msg or "discrepancy" in error_msg.lower()

    def test_custom_tolerance(self):
        with pytest.raises(AmountMismatchError):
            validate_amount_consistency(
                1_250_000.0,
                "One Million Two Hundred Thousand",
                tolerance=10_000.0
            )

        validate_amount_consistency(
            1_250_000.0,
            "One Million Two Hundred Thousand",
            tolerance=100_000.0
        )


class TestMoneyFormatting:
    def test_format_money(self):
        assert format_money(1_250_000.0) == "$1,250,000.00"
        assert format_money(1_200_000.0) == "$1,200,000.00"
        assert format_money(50_000.0) == "$50,000.00"
