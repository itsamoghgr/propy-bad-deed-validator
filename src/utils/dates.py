# Date utilities and validation logic, This module provides deterministic date validation.

from datetime import datetime, date
from typing import Tuple



def parse_date(date_str: str) -> date:
    # Parse date string to date object, supports ISO format (YYYY-MM-DD) and common variations.
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        formats = ["%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        raise ValueError(f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD or similar.")

def validate_date_sequence(date_signed: str, date_recorded: str) -> None:
    from src.validate.errors import InvalidDateSequenceError

    try:
        signed = parse_date(date_signed)
        recorded = parse_date(date_recorded)
    except ValueError as e:
        raise InvalidDateSequenceError(f"Date parsing error: {e}")

    if recorded < signed:
        raise InvalidDateSequenceError(
            f"Document cannot be recorded ({date_recorded}) before it was signed ({date_signed}). "
            f"This is logically impossible."
        )


def get_date_difference_days(date1_str: str, date2_str: str) -> int:
    date1 = parse_date(date1_str)
    date2 = parse_date(date2_str)

    return (date2 - date1).days
