"""
This is the complete validation pipeline:

    1. Extract structured data from OCR using LLM
    2. Enrich with county resolution and tax rate
    3. Validate with deterministic business rules
    4. Return pass/fail result

"""

import json
import sys

from src.models import ValidationResult, ValidationError as ValidationErrorModel
from src.llm.extractor import extract_deed_fields
from src.enrich.county_resolver import load_counties, enrich_with_county
from src.validate.rules import validate_deed
from src.validate.errors import ValidationError


RAW_OCR_TEXT = """*** RECORDING REQ ***
Doc: DEED-TRUST-0042
County: S. Clara  |  State: CA
Date Signed: 2024-01-15
Date Recorded: 2024-01-10
Grantor:  T.E.S.L.A. Holdings LLC
Grantee:  John  &  Sarah  Connor
Amount: $1,250,000.00 (One Million Two Hundred Thousand Dollars)
APN: 992-001-XA
Status: PRELIMINARY
*** END ***"""

def validate_deed_document(raw_text: str) -> ValidationResult:
    errors = []
    try:
        print("Step 1: Extracting fields with LLM...")
        extracted = extract_deed_fields(raw_text)
        print(f"  > Extracted: {extracted.doc}")
        print(f"    County (raw): {extracted.county_raw}")
        print(f"    Date Signed: {extracted.date_signed}")
        print(f"    Date Recorded: {extracted.date_recorded}")
        print(f"    Amount (numeric): ${extracted.amount_numeric:,.2f}")
        print(f"    Amount (words): {extracted.amount_words}")
        print()

        print("Step 2: Enriching with county data...")
        counties = load_counties()
        enriched = enrich_with_county(extracted, counties)
        print(f"  > County Resolved: '{extracted.county_raw}' -> '{enriched.county_canonical}'")
        print(f"    Tax Rate: {enriched.tax_rate * 100:.1f}%")
        print(f"    Match Confidence: {enriched.match_confidence * 100:.1f}%")
        print()

        print("Step 3: Validating business rules...")
        validate_deed(
            date_signed=enriched.date_signed,
            date_recorded=enriched.date_recorded,
            amount_numeric=enriched.amount_numeric,
            amount_words=enriched.amount_words
        )
        print("  > All validations passed!")
        print()
        closing_cost = enriched.amount_numeric * enriched.tax_rate

        return ValidationResult(
            passed=True,
            deed=enriched,
            closing_cost=closing_cost,
            errors=[]
        )

    except ValidationError as e:
        # multiple validation errors
        if hasattr(e, 'validation_errors'):
            print(f"  X Validation Failed: Multiple errors detected")
            print()

            for idx, err in enumerate(e.validation_errors, 1):
                print(f"  Error {idx}: {err.__class__.__name__}")
                print(f"    {str(err)}")
                print()

                errors.append(ValidationErrorModel(
                    error_type=err.__class__.__name__,
                    message=str(err)
                ))
        else:
            # Single error
            error_type = e.__class__.__name__
            print(f"  X Validation Failed: {error_type}")
            print(f"    {str(e)}")
            print()

            errors.append(ValidationErrorModel(
                error_type=error_type,
                message=str(e)
            ))

        return ValidationResult(
            passed=False,
            deed=None,
            closing_cost=None,
            errors=errors
        )

    except Exception as e:
        print(f"  X Unexpected Error: {e}")
        print()

        errors.append(ValidationErrorModel(
            error_type=e.__class__.__name__,
            message=str(e)
        ))

        return ValidationResult(
            passed=False,
            deed=None,
            closing_cost=None,
            errors=errors
        )


def main():
    # Main entry point.
    print("\nPropy - Bad Deed Validation")
    print("-" * 60)
    print()
    result = validate_deed_document(RAW_OCR_TEXT)

    print("\nValidation Result")
    print("-" * 60)
    print()
    if result.passed:
        print("STATUS: PASS")
        print()
        print(f"Document: {result.deed.doc}")
        print(f"County: {result.deed.county_canonical}")
        print(f"Transaction Amount: ${result.deed.amount_numeric:,.2f}")
        print(f"Tax Rate: {result.deed.tax_rate * 100:.1f}%")
        print(f"Closing Cost: ${result.closing_cost:,.2f}")
    else:
        print("STATUS: FAIL")
        print()
        print("Errors:")
        for error in result.errors:
            print(f"  - {error.error_type}: {error.message}")

    print()

    print("\nJSON Output")
    print("-" * 60)
    print(json.dumps(result.model_dump(), indent=2, default=str))

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
