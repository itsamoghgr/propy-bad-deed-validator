# Propy Deed Validator

My solution to Propy's "Bad Deed" validation challenge. The task: handle messy OCR text from real estate deeds while being paranoid enough not to trust AI for anything critical.

## The Problem

If an LLM hallucinates a number on a deed, Propy could record a fraudulent transaction on the blockchain. 
The challenge: use AI for parsing, validate everything with deterministic code.

The test data has two bugs:
1. Deed "recorded" before it was signed
2. $50,000 discrepancy between numeric amount and written words

Catch both with code, not prompts.

## My Approach

Three layers:

1. **LLM for parsing** - GPT-4o-mini turns messy OCR into structured JSON
2. **Deterministic enrichment** - Fuzzy match "S. Clara" → "Santa Clara"
3. **Deterministic validation** - Date and amount checks in Python

Key insight: AI parses unstructured text, then code validates financial logic and then Keeps them separated.

## Pipeline

```
Raw OCR Text → [LLM Parse] → [Enrich] → [Validate] → Pass/Fail
```

1. **Extract**: GPT parses messy text into JSON (prompt explicitly says NOT to validate)
2. **Enrich**: Resolve "S. Clara" → "Santa Clara" + tax rate lookup
3. **Validate**: Date and amount checks in Python

## Implementation Details

### 1. LLM Extraction

Used GPT-4o-mini with JSON mode (guarantees valid JSON). The prompt explicitly instructs:
- Extract values "EXACTLY as they appear"
- "Do NOT validate, correct, or fix values"
- If dates look wrong, extract them anyway

### 2. Date Sequence Validator

```python
if date_recorded < date_signed:
    raise InvalidDateSequenceError()
```

Catches the wrong date sequence: recorded Jan 10, signed Jan 15. Pure date comparison, no LLM.

### 3. Amount Consistency Validator

```python
parsed_words = parse_money_words(amount_words)
if abs(amount_numeric - parsed_words) > tolerance:
    raise AmountMismatchError()
```

Catches the $50k discrepancy:
- Numeric: $1,250,000
- Words: "One Million Two Hundred Thousand" = $1,200,000
- Tolerance: $0.00

Why $1 tolerance? Because the numeric and written amounts come from the same legal document, any difference, even $1 indicates an integrity or fraud risk and must be rejected.

**Important:** The validator runs ALL checks and shows ALL errors at once.

### 4. Money Parser (Custom Implementation)

Built my own parser instead of using a library to maintain control over edge cases, we can also use money-parser library (works just fine)

Logic:
- "One" = 1, "Million" × 1,000,000 = 1,000,000
- "Two Hundred" = 200, "Thousand" × 1,000 = 200,000
- Total: 1,000,000 + 200,000 = 1,200,000

### 5. County Resolution (Fuzzy Matching)

Maps "S. Clara" → "Santa Clara" for tax rate lookup.

Algorithm:
1. Normalize text (lowercase, remove spaces/pipes)
2. Expand abbreviations ("S." → "santa")
3. Fuzzy match using Python's difflib (SequenceMatcher)
4. Require 80% confidence threshold

No LLM guessing. Explicit matching logic with confidence scores.

## Code Structure

```
src/
├── main.py              # Pipeline orchestration
├── models.py            # Data models
├── config.py            # Settings
├── llm/                 # Extraction layer
├── enrich/              # Enrichment layer
├── validate/            # Validation layer
├── utils/               # Utilities (money parser, dates, fuzzy matching)
└── tests/               # Unit tests
```

Clean separation: LLM doesn't touch validation. Validation doesn't touch LLM.

## Quick Start

```bash
pip install -r requirements.txt
echo "OPENAI_API_KEY=your-key-here" > .env
python -m src.main
```

You'll see the validator catch BOTH bugs in the test data: date sequence and $50k amount discrepancy.

Run tests (31 tests, all passing):
```bash
pytest src/tests/ -v
```

## Output

**Test data shows BOTH errors:**
```
X Validation Failed: Multiple errors detected

Error 1: InvalidDateSequenceError
  Document cannot be recorded (2024-01-10) before it was signed (2024-01-15).

Error 2: AmountMismatchError
  Amount discrepancy detected:
    Numeric: $1,250,000.00
    Words: $1,200,000.00
    Discrepancy: $50,000.00
    Tolerance: $1.00
```

**JSON output (clean, separate error objects):**
```json
{
  "passed": false,
  "errors": [
    {
      "error_type": "InvalidDateSequenceError",
      "message": "Document cannot be recorded..."
    },
    {
      "error_type": "AmountMismatchError",
      "message": "Amount discrepancy detected..."
    }
  ]
}
```

**With valid data:**
```json
{
  "passed": true,
  "deed": { "doc": "DEED-TRUST-0042", "county_canonical": "Santa Clara" },
  "closing_cost": 15000.0
}
```

## Why This Approach Works

**Clear boundaries** - LLM parses. Code validates. No mixing.

**Explicit logic** - County matching is readable code, not prompt magic.

**Testable** - Deterministic logic means proper unit tests.

**Comprehensive errors** - Shows all problems at once instead of fail-fast.

## Tech Stack

I kept dependencies minimal:
- **openai** - For GPT-4o-mini API calls
- **pydantic** - Type-safe data models
- **python-dotenv** - Environment variable loading
- **pytest** - Testing

For fuzzy matching and date logic, I just used Python's built-in `difflib` and `datetime`.

## Task Requirements

Built for Propy's technical assessment:

1. Parse messy OCR text using LLM
2. Resolve "S. Clara" → "Santa Clara" + tax rate
3. Catch impossible date sequence (recorded before signed)
4. Catch $50k amount discrepancy (numeric vs. words)

The key was knowing when to use AI (parsing messy text) vs. deterministic code (financial validation). AI is a tool, not a replacement for good engineering.

---

That's it! Fun challenge. Learned a lot about building paranoid systems.
