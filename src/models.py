# Data models for validation pipeline.
from typing import Optional, List
from pydantic import BaseModel, Field

class ExtractedDeed(BaseModel):
    # Raw data from LLM extraction
    doc: str = Field(description="Document number (e.g., DEED-TRUST-0042)")
    county_raw: str = Field(description="County name as it appears in OCR (may be abbreviated)")
    state: str = Field(description="State code (e.g., CA)")
    date_signed: str = Field(description="Date the deed was signed (YYYY-MM-DD)")
    date_recorded: str = Field(description="Date the deed was recorded (YYYY-MM-DD)")
    grantor: str = Field(description="Party transferring the property")
    grantee: str = Field(description="Party receiving the property")
    amount_numeric: float = Field(description="Transaction amount as a number")
    amount_words: str = Field(description="Transaction amount written in words")
    apn: str = Field(description="Assessor's Parcel Number")
    status: str = Field(description="Document status (e.g., PRELIMINARY, FINAL)")

class EnrichedDeed(ExtractedDeed):
    # After enrichment with county resolution and tax rate
    county_canonical: str = Field(description="Standardized county name")
    tax_rate: float = Field(description="County tax rate (e.g., 0.012 for 1.2%)")
    match_confidence: float = Field(description="Confidence score for county match (0.0-1.0)")


class ValidationError(BaseModel):
    error_type: str = Field(description="Type of validation error")
    message: str = Field(description="Detailed error message")
    field: Optional[str] = Field(default=None, description="Field that failed validation")


class ValidationResult(BaseModel):
    # Final validation outcome
    passed: bool = Field(description="Whether validation passed")
    deed: Optional[EnrichedDeed] = Field(default=None, description="Enriched deed data if passed")
    errors: List[ValidationError] = Field(default_factory=list, description="List of validation errors")
    closing_cost: Optional[float] = Field(default=None, description="Calculated closing cost if passed")


class County(BaseModel):
    name: str = Field(description="Official county name")
    tax_rate: float = Field(description="County tax rate")
