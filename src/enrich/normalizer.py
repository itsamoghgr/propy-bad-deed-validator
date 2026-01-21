# Text normalization utilities for county name matching, this module handles abbreviation expansion and text cleaning.
import re
from typing import Dict

# Common abbreviations in county names
ABBREVIATIONS: Dict[str, str] = {
    "s.": "santa", 
    "st.": "saint",
    "mt.": "mount",
    "n.": "north",
    "e.": "east",
    "w.": "west",
    "ft.": "fort",
}

def normalize_county_name(name: str) -> str:
    # Normalize county name for matching.
    name = name.lower()
    name = re.sub(r'\s+', ' ', name).strip()
    name = name.replace('|', '').strip()

    return name

def expand_abbreviations(name: str) -> str:
    # Expand common abbreviations in county names.
    name = normalize_county_name(name)
    words = name.split()
    expanded_words = []

    for word in words:
        if word in ABBREVIATIONS:
            expanded_words.append(ABBREVIATIONS[word])
        else:
            word_clean = word.replace('.', '')
            if word.endswith('.') and word in ABBREVIATIONS:
                expanded_words.append(ABBREVIATIONS[word])
            else:
                expanded_words.append(word_clean)

    return ' '.join(expanded_words)
