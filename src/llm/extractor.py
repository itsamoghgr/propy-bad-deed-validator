# LLM-based deed field extraction
from src.models import ExtractedDeed
from src.llm.client import get_llm_client
from src.llm.prompts import create_extraction_prompt
from src.validate.errors import ExtractionError, MissingFieldError

def extract_deed_fields(raw_text: str) -> ExtractedDeed:
    prompt = create_extraction_prompt(raw_text)
    try:
        client = get_llm_client()
        data = client.extract_json(prompt)
    except Exception as e:
        raise ExtractionError(f"Failed to extract deed fields: {e}")

    required_fields = [
        "doc", "county_raw", "state", "date_signed", "date_recorded",
        "grantor", "grantee", "amount_numeric", "amount_words", "apn", "status"
    ]

    missing = [field for field in required_fields if field not in data]
    if missing:
        raise MissingFieldError(f"Missing required fields: {missing}")
        
    try:
        deed = ExtractedDeed(**data)
        return deed
    except Exception as e:
        raise ExtractionError(f"Failed to parse extracted data: {e}")
