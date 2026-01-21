# OpenAI integration for LLM interactions

from typing import Optional
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from src.config import OPENAI_API_KEY, OPENAI_MODEL
from src.validate.errors import ExtractionError


class LLMClient:
    def __init__(self, api_key: Optional[str] = None, model: str = OPENAI_MODEL):
        # Initialize LLM client.
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai package not installed. "
                "Install with: pip install openai"
            )

        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def extract_json(self, prompt: str, temperature: float = 0.0) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise data extraction system. "
                                   "Extract structured data exactly as it appears. "
                                   "Do not validate, correct, or interpret values. "
                                   "Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response.choices[0].message.content
            data = json.loads(content)

            return data

        except json.JSONDecodeError as e:
            raise ExtractionError(f"LLM returned invalid JSON: {e}")
        except Exception as e:
            raise ExtractionError(f"LLM extraction failed: {e}")


# Singleton instance
_client_instance: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    global _client_instance

    if _client_instance is None:
        _client_instance = LLMClient()

    return _client_instance
