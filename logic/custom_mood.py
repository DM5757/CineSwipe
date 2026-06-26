"""Build custom mood cards from free-text input using keyword matching."""

import re
import uuid
from typing import Any

KEYWORD_TRAITS: dict[str, str] = {
    "dark": "dark",
    "thriller": "thriller",
    "scary": "horror",
    "horror": "horror",
    "psychological": "psychological",
    "mystery": "mystery",
    "romantic": "romance",
    "romance": "romance",
    "funny": "comedy",
    "comedy": "comedy",
    "nostalgic": "nostalgic",
    "nostalgia": "nostalgic",
    "classic": "classic",
    "slow": "drama",
    "emotional": "emotional",
    "action": "action",
    "sci fi": "sci-fi",
    "sci-fi": "sci-fi",
    "scifi": "sci-fi",
    "crime": "crime",
    "fantasy": "fantasy",
    "drama": "drama",
    "adventure": "adventure",
    "mind bending": "mind-bending",
    "mind-bending": "mind-bending",
    "cozy": "cozy",
    "rainy": "cozy",
    "late night": "mystery",
    "unhinged": "intense",
    "chaotic": "intense",
    "devastating": "emotional",
    "uplifting": "uplifting",
    "inspiring": "inspirational",
    "witty": "witty",
    "suspense": "suspense",
    "epic": "epic",
    "indie": "indie",
    "animated": "animation",
    "family": "family",
    "musical": "musical",
    "documentary": "documentary",
}

KNOWN_PEOPLE: dict[str, str] = {
    "daniel day-lewis": "daniel day lewis",
    "daniel day lewis": "daniel day lewis",
    "leonardo dicaprio": "leonardo dicaprio",
    "jake gyllenhaal": "jake gyllenhaal",
    "ryan gosling": "ryan gosling",
    "brad pitt": "brad pitt",
    "christian bale": "christian bale",
    "robert de niro": "robert de niro",
    "al pacino": "al pacino",
    "tom hardy": "tom hardy",
    "cillian murphy": "cillian murphy",
    "christopher nolan": "christopher nolan",
    "quentin tarantino": "quentin tarantino",
    "martin scorsese": "martin scorsese",
    "denis villeneuve": "denis villeneuve",
}

ACTOR_DIRECTOR_TRAITS = [
    "actor driven",
    "strong performance",
    "prestige drama",
    "character study",
]

WEAK_DISPLAY_TRAITS = {"custom", "mood-based"}


def extract_traits_from_text(text: str) -> list[str]:
    """Match mood keywords and actor/director names in user text."""
    normalized = text.lower().replace("_", " ")
    found: list[str] = []
    person_detected = False

    for keyword, trait in KEYWORD_TRAITS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", normalized) and trait not in found:
            found.append(trait)

    for person_key, person_trait in KNOWN_PEOPLE.items():
        if person_key in normalized:
            person_detected = True
            if person_trait not in found:
                found.append(person_trait)

    if person_detected:
        for trait in ACTOR_DIRECTOR_TRAITS:
            if trait not in found:
                found.append(trait)

    if not found:
        return ["custom", "mood-based"]
    return found


def build_custom_mood_card(text: str) -> dict[str, Any]:
    """Create a mood card dict from user-submitted text."""
    traits = extract_traits_from_text(text)
    weights = {trait: 3 if trait in KNOWN_PEOPLE.values() else 2 for trait in traits}
    display = text.strip()
    title = display if len(display) <= 48 else f"{display[:45]}..."

    return {
        "id": f"custom_{uuid.uuid4().hex[:8]}",
        "title": title,
        "description": display,
        "traits": traits,
        "weights": weights,
        "is_custom": True,
    }


def get_display_mood_signals(
    top_traits: list[tuple[str, float]],
    selected_moods: list[dict[str, Any]],
    limit: int = 5,
) -> list[str]:
    """Return user-facing mood signals, hiding weak technical traits when possible."""
    meaningful = [
        trait.replace("-", " ")
        for trait, _ in top_traits
        if trait not in WEAK_DISPLAY_TRAITS
    ]
    if meaningful:
        return meaningful[:limit]

    custom_labels = []
    for mood in selected_moods:
        if mood.get("is_custom"):
            raw = (mood.get("description") or mood["title"]).strip()
            label = raw if len(raw) <= 42 else f"{raw[:39]}..."
            custom_labels.append(label)

    if custom_labels:
        return custom_labels[:limit]

    return [trait.replace("-", " ") for trait, _ in top_traits[:limit]]
