"""Local and AI-powered movie recommendation orchestration."""

import logging
from typing import Any

from services.gemini_service import generate_movie_recommendations, is_valid_gemini_movie_item
from services.omdb_service import fetch_movie_metadata

logger = logging.getLogger(__name__)

IMDbPreference = str  # "mood_first" | "balanced" | "highly_rated"
FALLBACK_NOTICE = (
    "AI recommendations are temporarily unavailable, "
    "so CineSwipe used local fallback picks."
)
TARGET_RECOMMENDATIONS = 5

RATING_WEIGHTS: dict[str, float] = {
    "mood_first": 0.5,
    "balanced": 2.0,
    "highly_rated": 4.0,
}


def _mood_score(movie: dict[str, Any], trait_scores: dict[str, float]) -> float:
    movie_traits = set(movie.get("traits", []))
    return sum(trait_scores.get(trait, 0) for trait in movie_traits)


def _parse_rating_value(rating: Any) -> float:
    try:
        return float(rating)
    except (TypeError, ValueError):
        return 0.0


def _combined_score(
    movie: dict[str, Any],
    trait_scores: dict[str, float],
    imdb_preference: IMDbPreference,
) -> float:
    mood_part = _mood_score(movie, trait_scores)
    rating_part = _parse_rating_value(movie.get("rating", 0)) / 10.0
    rating_weight = RATING_WEIGHTS.get(imdb_preference, RATING_WEIGHTS["balanced"])
    return mood_part * 10.0 + rating_part * rating_weight


def _build_match_reason(
    movie: dict[str, Any],
    top_traits: list[tuple[str, float]],
    imdb_preference: IMDbPreference,
) -> str:
    top_trait_names = {trait for trait, _ in top_traits}
    matched = [trait for trait in movie.get("traits", []) if trait in top_trait_names]
    if not matched:
        matched = movie.get("traits", [])[:3]

    readable = ", ".join(t.replace("-", " ") for t in matched[:3])
    preference_note = {
        "mood_first": "prioritizing your mood match",
        "balanced": "balancing mood and critic ratings",
        "highly_rated": "favoring highly rated picks that fit your mood",
    }.get(imdb_preference, "matching your mood")

    return f"Matches your mood for {readable} storytelling, {preference_note}."


def recommend_movies(
    trait_scores: dict[str, float],
    movies: list[dict[str, Any]],
    top_traits: list[tuple[str, float]] | None = None,
    imdb_preference: IMDbPreference = "balanced",
    min_results: int = 3,
    max_results: int = 5,
    exclude_titles: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Return ranked movie recommendations from local fallback data."""
    if not trait_scores:
        return []

    if top_traits is None:
        top_traits = sorted(trait_scores.items(), key=lambda item: item[1], reverse=True)[:5]

    excluded = {title.lower() for title in (exclude_titles or set())}
    scored: list[tuple[float, dict[str, Any]]] = []
    for movie in movies:
        if movie.get("title", "").lower() in excluded:
            continue
        score = _combined_score(movie, trait_scores, imdb_preference)
        if score > 0:
            scored.append((score, movie))

    scored.sort(key=lambda item: item[0], reverse=True)

    if len(scored) < min_results:
        for movie in movies:
            if movie.get("title", "").lower() in excluded:
                continue
            if movie not in [m for _, m in scored]:
                scored.append((0.1, movie))
            if len(scored) >= min_results:
                break

    results: list[dict[str, Any]] = []
    for score, movie in scored[:max_results]:
        results.append(
            {
                **movie,
                "match_score": score,
                "match_reason": _build_match_reason(movie, top_traits, imdb_preference),
            }
        )

    return results


def _merge_gemini_with_omdb(
    gemini_rec: dict[str, Any],
    omdb_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Combine Gemini match reason with OMDb metadata when available."""
    title = gemini_rec.get("title", "").strip()
    year = gemini_rec.get("year", "").strip()
    match_reason = gemini_rec.get("match_reason", "").strip()

    if omdb_data:
        return {
            "title": omdb_data.get("title") or title,
            "year": omdb_data.get("year") or year,
            "rating": omdb_data.get("rating", "N/A"),
            "plot": omdb_data.get("plot") or "Plot unavailable.",
            "poster_url": omdb_data.get("poster_url"),
            "genre": omdb_data.get("genre"),
            "runtime": omdb_data.get("runtime"),
            "director": omdb_data.get("director"),
            "imdb_id": omdb_data.get("imdb_id"),
            "match_reason": match_reason,
        }

    return {
        "title": title,
        "year": year or "—",
        "rating": "N/A",
        "plot": "Details unavailable from OMDb.",
        "poster_url": None,
        "genre": None,
        "runtime": None,
        "director": None,
        "imdb_id": None,
        "match_reason": match_reason,
    }


def _fill_with_fallback(
    current: list[dict[str, Any]],
    trait_scores: dict[str, float],
    top_traits: list[tuple[str, float]],
    fallback_movies: list[dict[str, Any]],
    imdb_preference: IMDbPreference,
) -> list[dict[str, Any]]:
    """Top up recommendations with local fallback picks."""
    if len(current) >= TARGET_RECOMMENDATIONS:
        return current[:TARGET_RECOMMENDATIONS]

    existing_titles = {movie.get("title", "").lower() for movie in current}
    fillers = recommend_movies(
        trait_scores,
        fallback_movies,
        top_traits=top_traits,
        imdb_preference=imdb_preference,
        max_results=TARGET_RECOMMENDATIONS,
        exclude_titles=existing_titles,
    )

    combined = list(current)
    for movie in fillers:
        if len(combined) >= TARGET_RECOMMENDATIONS:
            break
        title_key = movie.get("title", "").lower()
        if title_key and title_key not in existing_titles:
            existing_titles.add(title_key)
            combined.append(movie)

    return combined[:TARGET_RECOMMENDATIONS]


def get_recommendations(
    trait_scores: dict[str, float],
    top_traits: list[tuple[str, float]],
    selected_mood_titles: list[str],
    custom_moods: list[str],
    fallback_movies: list[dict[str, Any]],
    imdb_preference: IMDbPreference = "balanced",
) -> tuple[list[dict[str, Any]], str, str | None]:
    """
    Try Gemini + OMDb first, then fall back to local recommendations.

    Returns:
        recommendations, source ("ai" | "fallback"), optional user notice
    """
    trait_names = [trait for trait, _ in top_traits]

    gemini_recs = generate_movie_recommendations(
        top_traits=trait_names,
        selected_mood_titles=selected_mood_titles,
        rating_preference=imdb_preference,
        custom_moods=custom_moods or None,
    )

    if gemini_recs:
        enriched: list[dict[str, Any]] = []
        for gemini_rec in gemini_recs:
            omdb_data = fetch_movie_metadata(
                title=gemini_rec["title"],
                year=gemini_rec.get("year") or None,
            )
            if omdb_data:
                enriched.append(_merge_gemini_with_omdb(gemini_rec, omdb_data))
            elif is_valid_gemini_movie_item(gemini_rec):
                enriched.append(_merge_gemini_with_omdb(gemini_rec, None))
            else:
                logger.info("Skipped Gemini title without OMDb match: %s", gemini_rec.get("title"))

        if enriched:
            final = _fill_with_fallback(
                enriched,
                trait_scores,
                top_traits,
                fallback_movies,
                imdb_preference,
            )
            return final, "ai", None

    logger.info("Using local fallback recommendations.")
    fallback = recommend_movies(
        trait_scores,
        fallback_movies,
        top_traits=top_traits,
        imdb_preference=imdb_preference,
    )
    return fallback, "fallback", FALLBACK_NOTICE
