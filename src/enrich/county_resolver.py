# County name resolution with fuzzy matching, This module handles the challenge of mapping messy OCR county names

import json
from typing import List, Tuple
from pathlib import Path

from src.models import County
from src.enrich.normalizer import normalize_county_name, expand_abbreviations
from src.utils.similarity import find_best_match
from src.validate.errors import CountyMatchError


# Confidence threshold for fuzzy matching
MATCH_CONFIDENCE_THRESHOLD = 0.8


def load_counties(counties_file: str = "counties.json") -> List[County]:
    # Load county reference data from JSON file.
    file_path = Path(counties_file)
    if not file_path.exists():
        file_path = Path(__file__).parent.parent.parent / counties_file

    if not file_path.exists():
        raise FileNotFoundError(f"Could not find {counties_file}")

    with open(file_path, 'r') as f:
        data = json.load(f)

    return [County(**item) for item in data]


def resolve_county(county_raw: str, counties: List[County], threshold: float = MATCH_CONFIDENCE_THRESHOLD) -> Tuple[str, float, float]:
    # Resolve raw county name to canonical name with tax rate.
    normalized = normalize_county_name(county_raw)
    expanded = expand_abbreviations(county_raw)

    for county in counties:
        county_normalized = normalize_county_name(county.name)
        if expanded == county_normalized:
            return county.name, county.tax_rate, 1.0

    county_names = [c.name for c in counties]
    best_match, confidence = find_best_match(
        expanded,
        county_names,
        threshold=threshold
    )

    if best_match is None:
        raise CountyMatchError(
            f"Could not match county '{county_raw}' to any known county.\n"
            f"  Normalized: '{normalized}'\n"
            f"  Expanded: '{expanded}'\n"
            f"  Available: {county_names}\n"
            f"  Confidence threshold: {threshold}"
        )
        
    tax_rate = next(c.tax_rate for c in counties if c.name == best_match)
    return best_match, tax_rate, confidence


def enrich_with_county(extracted_deed, counties: List[County]):
    # Enrich extracted deed with county information.
    from src.models import EnrichedDeed

    canonical_name, tax_rate, confidence = resolve_county(
        extracted_deed.county_raw,
        counties
    )

    enriched = EnrichedDeed(
        **extracted_deed.model_dump(),
        county_canonical=canonical_name,
        tax_rate=tax_rate,
        match_confidence=confidence
    )

    return enriched
