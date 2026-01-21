# Configuration settings
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"


MONEY_TOLERANCE = 1.0
COUNTY_MATCH_THRESHOLD = 0.8  

COUNTIES_FILE = "counties.json"
