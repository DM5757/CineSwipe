"""OMDb movie metadata lookups."""

import logging
import os
import re
from typing import Any

import requests

logger = logging.getLogger(__name__)

OMDB_BASE_URL = "http://www.omdbapi.com/"
REQUEST_TIMEOUT = 10


def _is_valid_api_key(api_key: str | None) -> bool:
    return bool(api_key and api_key.strip() and api_key.strip() != "your_key_here")


def clean_movie_title(title: str) -> str:
    """Strip noisy suffixes and embedded years from a movie title."""
    cleaned = title.strip()
    cleaned = cleaned.split("/")[0].strip()
    cleaned = re.sub(r"\s*\(\d{4}\)\s*", " ", cleaned).strip()
    if " - " in cleaned:
        left, right = cleaned.split(" - ", 1)
        if len(right) > 20:
            cleaned = left.strip()
    return cleaned


def _normalize_poster(poster: str | None) -> str | None:
    if not poster or poster.strip().upper() == "N/A":
        return None
    return poster.strip()


def _normalize_rating(rating: str | None) -> str:
    if not rating or rating.strip().upper() == "N/A":
        return "N/A"
    return rating.strip()


def _normalize_year(year: str | None) -> str:
    if not year:
        return ""
    match = re.search(r"\d{4}", str(year))
    return match.group(0) if match else str(year).strip()


def _fetch_once(
    title: str,
    year: str | None,
    api_key: str,
) -> dict[str, Any] | None:
    params: dict[str, str] = {
        "apikey": api_key,
        "t": title.strip(),
        "plot": "short",
        "r": "json",
    }
    if year and str(year).strip():
        params["y"] = str(year).strip()

    try:
        response = requests.get(OMDB_BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        logger.warning("OMDb request failed for %r: %s", title, type(exc).__name__)
        return None

    if not isinstance(data, dict) or data.get("Response") != "True":
        return None

    return {
        "title": data.get("Title", title).strip(),
        "year": _normalize_year(data.get("Year", year or "")),
        "rating": _normalize_rating(data.get("imdbRating")),
        "plot": (data.get("Plot") or "No plot available.").strip(),
        "poster_url": _normalize_poster(data.get("Poster")),
        "genre": (data.get("Genre") or "").strip() or None,
        "runtime": (data.get("Runtime") or "").strip() or None,
        "director": (data.get("Director") or "").strip() or None,
        "imdb_id": (data.get("imdbID") or "").strip() or None,
    }


def fetch_movie_metadata(
    title: str,
    year: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any] | None:
    """Fetch and normalize movie metadata from OMDb. Returns None on failure."""
    key = api_key or os.getenv("OMDB_API_KEY", "")
    if not _is_valid_api_key(key):
        logger.warning("OMDb API key is missing or invalid.")
        return None

    if not title or not title.strip():
        return None

    api_key_value = key.strip()
    original = title.strip()

    result = _fetch_once(original, year, api_key_value)
    if result:
        return result

    cleaned = clean_movie_title(original)
    if cleaned and cleaned != original:
        result = _fetch_once(cleaned, year, api_key_value)
        if result:
            return result
        result = _fetch_once(cleaned, None, api_key_value)
        if result:
            return result

    return None


class OMDbService:
    """Wrapper around OMDb metadata fetching."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("OMDB_API_KEY", "")

    @property
    def is_configured(self) -> bool:
        return _is_valid_api_key(self.api_key)

    def fetch_movie_metadata(self, title: str, year: str | None = None) -> dict[str, Any] | None:
        return fetch_movie_metadata(title=title, year=year, api_key=self.api_key)
