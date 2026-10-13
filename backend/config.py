import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.openai import OpenAIProvider


ROOT = Path(__file__).resolve().parents[1]
for env_file in (ROOT / ".env", ROOT.parent / ".env"):
    load_dotenv(env_file)

MODEL_NAME = "gpt-6-luna"


@lru_cache(maxsize=1)
def model() -> OpenAIResponsesModel:
    key = os.environ.get("PORTKEY_API_KEY", "").strip()
    if not key:
        raise RuntimeError("PORTKEY_API_KEY is missing from .env")
    client = AsyncOpenAI(
        api_key=key,
        base_url=os.environ.get("PORTKEY_BASE_URL", "https://api.portkey.ai/v1"),
        default_headers={"x-portkey-provider": "openai"},
    )
    return OpenAIResponsesModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))
