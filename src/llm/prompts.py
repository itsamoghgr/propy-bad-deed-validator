# LLM prompts for deed extraction.
def create_extraction_prompt(raw_text: str) -> str:
    return f"""Extract structured data from this deed OCR text.

IMPORTANT INSTRUCTIONS:
- Extract values EXACTLY as they appear in the text
- Do NOT validate dates, amounts, or any other fields
- Do NOT correct, interpret, or fix values
- If a value looks wrong, extract it anyway
- Return ONLY valid JSON matching the schema below

SCHEMA:
{{
  "doc": "document number (string)",
  "county_raw": "county name exactly as shown (string)",
  "state": "state code (string)",
  "date_signed": "signing date in YYYY-MM-DD format (string)",
  "date_recorded": "recording date in YYYY-MM-DD format (string)",
  "grantor": "grantor name (string)",
  "grantee": "grantee name (string)",
  "amount_numeric": "transaction amount as number (float)",
  "amount_words": "transaction amount in words exactly as written (string)",
  "apn": "assessor parcel number (string)",
  "status": "document status (string)"
}}

OCR TEXT:
{raw_text}

Return ONLY the JSON object with extracted data. No other text.
"""
