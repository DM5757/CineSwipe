"""Profile signature helpers for recommendation caching."""

import hashlib
import json
from typing import Any


def build_profile_signature(
    selected_moods: list[dict[str, Any]],
    top_traits: list[tuple[str, float]],
    imdb_preference: str,
) -> str:
    """Create a stable signature for the current mood profile."""
    custom_moods = sorted(
        (mood.get("description") or mood["title"]).strip()
        for mood in selected_moods
        if mood.get("is_custom")
    )
    payload = {
        "mood_ids": sorted(mood["id"] for mood in selected_moods),
        "custom_moods": custom_moods,
        "top_traits": top_traits,
        "imdb_preference": imdb_preference,
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
