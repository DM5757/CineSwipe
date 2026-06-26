"""Safe Gemini API connection test utility."""

import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from services.gemini_errors import log_gemini_error  # noqa: E402
from services.gemini_service import _is_valid_api_key  # noqa: E402

WORKING_MODEL_FILE = PROJECT_ROOT / "data" / "working_gemini_model.txt"
TEST_MODELS = (
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
)
TEST_PROMPT = (
    'Return only this JSON: [{"title":"Inception","year":"2010","match_reason":"Test"}]'
)


def _load_api_key() -> str:
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    import os

    return os.getenv("GEMINI_API_KEY", "")


def _test_model(api_key: str, model_name: str) -> tuple[bool, str]:
    client = genai.Client(api_key=api_key.strip())
    response = client.models.generate_content(
        model=model_name,
        contents=TEST_PROMPT,
    )
    response_text = (getattr(response, "text", None) or "").strip()
    return bool(response_text), response_text


def main() -> int:
    api_key = _load_api_key()
    key_loaded = _is_valid_api_key(api_key)

    print(f"Gemini key loaded: {key_loaded}")
    print(f"Gemini key length: {len(api_key.strip()) if api_key else 0}")

    if not key_loaded:
        print("Cannot test Gemini: API key is missing or invalid.")
        return 1

    for model_name in TEST_MODELS:
        print(f"Testing model: {model_name}")
        try:
            success, response_text = _test_model(api_key, model_name)
            if success:
                print(f"SUCCESS with model: {model_name}")
                print(response_text)
                WORKING_MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
                WORKING_MODEL_FILE.write_text(model_name, encoding="utf-8")
                print(f"Saved working model to: {WORKING_MODEL_FILE}")
                return 0
            print("Model returned an empty response.")
        except Exception as exc:
            log_gemini_error(exc)

    print("All Gemini model tests failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
