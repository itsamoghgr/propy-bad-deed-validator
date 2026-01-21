# Unit tests for county name resolution.

import pytest
from src.models import County
from src.enrich.county_resolver import resolve_county
from src.enrich.normalizer import normalize_county_name, expand_abbreviations
from src.validate.errors import CountyMatchError

SAMPLE_COUNTIES = [
    County(name="Santa Clara", tax_rate=0.012),
    County(name="San Mateo", tax_rate=0.011),
    County(name="Santa Cruz", tax_rate=0.010)
]


class TestCountyNormalization:
    # Tests for county name normalization.
    def test_normalize_lowercase(self):
        assert normalize_county_name("Santa Clara") == "santa clara"

    def test_normalize_removes_pipes(self):
        assert normalize_county_name("S. Clara  |") == "s. clara"

    def test_normalize_extra_whitespace(self):
        assert normalize_county_name("S.  Clara  ") == "s. clara"


class TestAbbreviationExpansion:
    # Tests for abbreviation expansion.
    def test_expand_s_to_santa(self):
        result = expand_abbreviations("S. Clara")
        assert result == "santa clara"

    def test_expand_st_to_saint(self):
        result = expand_abbreviations("St. Louis")
        assert result == "saint louis"

    def test_no_expansion_needed(self):
        result = expand_abbreviations("Santa Clara")
        assert result == "santa clara"


class TestCountyResolution:
    # Tests for county resolution with fuzzy matching.
    def test_resolve_exact_match(self):
        name, tax_rate, confidence = resolve_county(
            "Santa Clara",
            SAMPLE_COUNTIES
        )
        assert name == "Santa Clara"
        assert tax_rate == 0.012
        assert confidence == 1.0

    def test_resolve_abbreviated_name(self):
        name, tax_rate, confidence = resolve_county(
            "S. Clara",
            SAMPLE_COUNTIES,
            threshold=0.7 
        )
        assert name == "Santa Clara"
        assert tax_rate == 0.012
        assert confidence > 0.7

    def test_resolve_with_extra_whitespace(self):
        name, tax_rate, confidence = resolve_county(
            "S. Clara  |  ",
            SAMPLE_COUNTIES,
            threshold=0.7
        )
        assert name == "Santa Clara"
        assert tax_rate == 0.012

    def test_resolve_no_match_fails(self):
        with pytest.raises(CountyMatchError):
            resolve_county(
                "Unknown County",
                SAMPLE_COUNTIES,
                threshold=0.8
            )

    def test_resolve_low_confidence_fails(self):
        with pytest.raises(CountyMatchError):
            resolve_county(
                "xyz",
                SAMPLE_COUNTIES,
                threshold=0.9 
            )

    def test_all_sample_counties(self):
        for county in SAMPLE_COUNTIES:
            name, tax_rate, confidence = resolve_county(
                county.name,
                SAMPLE_COUNTIES
            )
            assert name == county.name
            assert tax_rate == county.tax_rate
            assert confidence == 1.0
