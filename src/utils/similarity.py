# String similarity utilities for fuzzy matching, Uses Python's built-in difflib for fuzzy string matching, No external dependencies needed.

from difflib import SequenceMatcher
from typing import List, Tuple



def similarity_score(str1: str, str2: str) -> float:
    # Calculate similarity score between two strings, Uses SequenceMatcher from difflib.
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def find_best_match(
    query: str,
    candidates: List[str],
    threshold: float = 0.0
) -> Tuple[str, float]:
    best_match = None
    best_score = 0.0

    for candidate in candidates:
        score = similarity_score(query, candidate)
        if score > best_score:
            best_score = score
            best_match = candidate

    if best_score < threshold:
        return None, 0.0

    return best_match, best_score
