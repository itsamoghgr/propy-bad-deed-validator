# Validation rules for deed documents.
from src.utils.money_words import parse_money_words, format_money
from src.utils.dates import validate_date_sequence as validate_dates_util
from src.validate.errors import AmountMismatchError, ValidationError
from src.config import MONEY_TOLERANCE


def validate_date_sequence(date_signed: str, date_recorded: str) -> None:
    validate_dates_util(date_signed, date_recorded)

def validate_amount_consistency(amount_numeric: float,amount_words: str,tolerance: float = MONEY_TOLERANCE) -> None:
    try:
        parsed_words = parse_money_words(amount_words)
    except ValueError as e:
        raise AmountMismatchError(f"Could not parse amount in words: {e}")

    discrepancy = abs(amount_numeric - parsed_words)
    if discrepancy > tolerance:
        raise AmountMismatchError(
            f"Amount discrepancy detected:\n"
            f"  Numeric: {format_money(amount_numeric)}\n"
            f"  Words: {format_money(parsed_words)}\n"
            f"  Discrepancy: {format_money(discrepancy)}\n"
            f"  Tolerance: {format_money(tolerance)}\n"
            f"This exceeds acceptable tolerance and indicates a potential error or fraud."
        )

def validate_deed(date_signed: str, date_recorded: str, amount_numeric: float, amount_words: str) -> None:
    """
    Validate all business rules and collect all errors.
    If multiple errors found, raises a ValidationError with all of them attached.
    """
    errors = []
    try:
        validate_date_sequence(date_signed, date_recorded)
    except ValidationError as e:
        errors.append(e)

    try:
        validate_amount_consistency(amount_numeric, amount_words)
    except ValidationError as e:
        errors.append(e)


    if errors:
        if len(errors) == 1:
            raise errors[0]
        else:
            multi_error = ValidationError(f"Found {len(errors)} validation errors")
            multi_error.validation_errors = errors 
            raise multi_error
