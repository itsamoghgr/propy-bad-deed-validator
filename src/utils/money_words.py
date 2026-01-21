# Money word parser - converts written amounts to numeric values
import re
from typing import Dict

# Word to number mappings
ONES: Dict[str, int] = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19
}

TENS: Dict[str, int] = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90
}

MULTIPLIERS: Dict[str, int] = {
    "hundred": 100,
    "thousand": 1_000,
    "million": 1_000_000,
    "billion": 1_000_000_000,
    "trillion": 1_000_000_000_000
}


def normalize_text(text: str) -> str:
    text = text.lower()

    text = text.replace("dollars", "")
    text = text.replace("dollar", "")

    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def parse_money_words(text: str) -> float:
    text = normalize_text(text)

    if not text:
        raise ValueError("Empty money text")

    words = text.split()

    current = 0  
    total = 0    

    for word in words:
        if word in ONES:
            current += ONES[word]
        elif word in TENS:
            current += TENS[word]
        elif word in MULTIPLIERS:
            multiplier = MULTIPLIERS[word]

            if current == 0:
                current = 1 

            if multiplier >= 1000:
                total += current * multiplier
                current = 0
            else:
                current *= multiplier
        elif word == "and":
            continue
        else:
            # Unknown word - might be "a" as in "a million"
            if word == "a":
                current = 1
            else:
                raise ValueError(f"Unknown word in money text: '{word}'")

    total += current

    return float(total)

def format_money(amount: float) -> str:
    return f"${amount:,.2f}"
