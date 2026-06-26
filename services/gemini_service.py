"""Gemini-powered movie recommendations from mood profiles."""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from google import genai

from services.gemini_errors import log_gemini_error

logger = logging.getLogger(__name__)

DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
WORKING_MODEL_FILE = Path(__file__).resolve().parent.parent / "data" / "working_gemini_model.txt"
MAX_TITLE_LENGTH = 80

INVALID_TITLE_KEYWORDS = (
    "episode",
    "podcast",
    "trailer",
    "review",
    "specialists",
    "interview",
    "youtube",
)

RATING_PREFERENCE_LABELS = {
    "mood_first": "Mood first",
    "balanced": "Balanced",
    "highly_rated": "Highly rated",
}

RATING_PREFERENCE_GUIDANCE = {
    "mood_first": "Prioritize mood fit over IMDb rating.",
    "balanced": "Balance mood fit and IMDb rating.",
    "highly_rated": "Prefer stronger IMDb ratings while still matching the mood.",
}


def resolve_gemini_model() -> str:
    """
    Resolve Gemini model with priority:
    1. GEMINI_MODEL from environment
    2. data/working_gemini_model.txt
    3. gemini-2.0-flash default
    """
    env_model = os.getenv("GEMINI_MODEL", "").strip()
    if env_model:
        return env_model

    if WORKING_MODEL_FILE.exists():
        saved_model = WORKING_MODEL_FILE.read_text(encoding="utf-8").strip()
        if saved_model:
            return saved_model

    return DEFAULT_GEMINI_MODEL


def _is_valid_api_key(api_key: str | None) -> bool:
    return bool(api_key and api_key.strip() and api_key.strip() != "your_key_here")


def _is_valid_year(year: str) -> bool:
    return bool(re.fullmatch(r"\d{4}", str(year).strip()))


def is_valid_gemini_movie_item(item: dict[str, Any]) -> bool:
    """Return True if a parsed Gemini movie item looks acceptable."""
    title = str(item.get("title", "")).strip()
    year = str(item.get("year", "")).strip()
    match_reason = str(item.get("match_reason", "")).strip()

    if not title or title.upper() == "N/A":
        return False
    if not _is_valid_year(year):
        return False
    if len(title) > MAX_TITLE_LENGTH:
        return False
    if "/" in title:
        return False
    if not match_reason or match_reason.upper() == "N/A":
        return False

    lower_title = title.lower()
    if any(keyword in lower_title for keyword in INVALID_TITLE_KEYWORDS):
        return False

    return True


def validate_gemini_recommendations(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter Gemini items to clean, unique, valid movie recommendations."""
    validated: list[dict[str, Any]] = []
    seen_titles: set[str] = set()

    for item in items:
        if not isinstance(item, dict) or not is_valid_gemini_movie_item(item):
            continue

        title = str(item["title"]).strip()
        title_key = title.lower()
        if title_key in seen_titles:
            continue

        seen_titles.add(title_key)
        validated.append(
            {
                "title": title,
                "year": str(item["year"]).strip(),
                "match_reason": str(item["match_reason"]).strip(),
            }
        )

    return validated


def _extract_json_array(text: str) -> list[dict[str, Any]] | None:
    """Parse Gemini output into a list of recommendation dicts."""
    if not text or not text.strip():
        return None

    cleaned = text.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        array_match = re.search(r"\[[\s\S]*\]", cleaned)
        if not array_match:
            return None
        try:
            data = json.loads(array_match.group(0))
        except json.JSONDecodeError:
            return None

    if not isinstance(data, list):
        return None

    raw_items: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict):
            raw_items.append(item)

    validated = validate_gemini_recommendations(raw_items)
    return validated or None


def _build_prompt(
    top_traits: list[str],
    selected_mood_titles: list[str],
    rating_preference: str,
    custom_moods: list[str] | None = None,
) -> str:
    pref_label = RATING_PREFERENCE_LABELS.get(rating_preference, "Balanced")
    pref_guidance = RATING_PREFERENCE_GUIDANCE.get(
        rating_preference,
        RATING_PREFERENCE_GUIDANCE["balanced"],
    )
    traits_text = ", ".join(top_traits) if top_traits else "general cinematic mood"
    moods_text = ", ".join(selected_mood_titles) if selected_mood_titles else "none"
    custom_text = ", ".join(custom_moods) if custom_moods else "none"

    return f"""You are a movie recommendation assistant for CineSwipe.

Recommend exactly 5 real, existing movies based on this user mood profile.

Selected mood titles: {moods_text}
Top mood traits: {traits_text}
Custom mood descriptions: {custom_text}
Rating preference: {pref_label}
Rating guidance: {pref_guidance}

Strict rules:
- Recommend real existing movies only.
- Movies only. No TV shows.
- No podcasts.
- No YouTube videos.
- No episodes.
- No combined titles.
- No slash-separated recommendations.
- No long article or video titles.
- No N/A fields.
- Each item must contain exactly one movie.
- Title must be the clean official movie title only.
- Year must be the release year only, as a 4-digit year.
- Do not recommend duplicates.
- Return only valid JSON.
- No markdown fences.
- No explanation outside JSON.

Return this JSON format exactly:
[
  {{
    "title": "Se7en",
    "year": "1995",
    "match_reason": "Short reason."
  }}
]
"""


def generate_movie_recommendations(
    top_traits: list[str],
    selected_mood_titles: list[str],
    rating_preference: str,
    custom_moods: list[str] | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> list[dict[str, Any]] | None:
    """Ask Gemini for movie recommendations. Returns None on failure."""
    key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not _is_valid_api_key(key):
        logger.warning("Gemini API key is missing or invalid.")
        return None

    model_name = model or resolve_gemini_model()
    prompt = _build_prompt(top_traits, selected_mood_titles, rating_preference, custom_moods)

    try:
        client = genai.Client(api_key=key.strip())
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        raw_text = getattr(response, "text", None) or ""
        recommendations = _extract_json_array(raw_text)
        if not recommendations:
            logger.warning("Gemini response did not contain valid recommendation JSON.")
            return None
        return recommendations
    except Exception as exc:
        log_gemini_error(exc)
        return None


class GeminiService:
    """Wrapper around Gemini recommendation generation."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")

    @property
    def is_configured(self) -> bool:
        return _is_valid_api_key(self.api_key)

    def generate_movie_recommendations(
        self,
        top_traits: list[str],
        selected_mood_titles: list[str],
        rating_preference: str,
        custom_moods: list[str] | None = None,
    ) -> list[dict[str, Any]] | None:
        return generate_movie_recommendations(
            top_traits=top_traits,
            selected_mood_titles=selected_mood_titles,
            rating_preference=rating_preference,
            custom_moods=custom_moods,
            api_key=self.api_key,
        )
