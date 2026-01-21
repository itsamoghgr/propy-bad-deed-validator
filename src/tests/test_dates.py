# Unit tests for date validation logic.
import pytest
from src.utils.dates import validate_date_sequence, parse_date
from src.validate.errors import InvalidDateSequenceError


def test_valid_date_sequence_same_day():
    validate_date_sequence("2024-01-15", "2024-01-15")

def test_valid_date_sequence_recorded_after():
    validate_date_sequence("2024-01-10", "2024-01-15")

def test_invalid_date_sequence_recorded_before_signed():
    with pytest.raises(InvalidDateSequenceError) as exc_info:
        validate_date_sequence("2024-01-15", "2024-01-10")
    assert "recorded" in str(exc_info.value).lower()
    assert "signed" in str(exc_info.value).lower()

def test_invalid_date_format():
    with pytest.raises(InvalidDateSequenceError):
        validate_date_sequence("invalid-date", "2024-01-10")


def test_parse_date_iso_format():
    date = parse_date("2024-01-15")
    assert date.year == 2024
    assert date.month == 1
    assert date.day == 15

def test_parse_date_slash_format():
    date = parse_date("01/15/2024")
    assert date.year == 2024
    assert date.month == 1
    assert date.day == 15
