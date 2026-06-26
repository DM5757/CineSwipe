"""Reusable Streamlit UI components for CineSwipe screens."""

import html
from typing import Any, Callable

import streamlit as st

from logic.custom_mood import get_display_mood_signals
from logic.mood_engine import MoodEngine

IMDB_OPTIONS = {
    "mood_first": {
        "label": "Mood first",
        "description": (
            "Recommendations mostly follow your mood, even if the movie "
            "is not extremely highly rated."
        ),
    },
    "balanced": {
        "label": "Balanced",
        "description": "Recommendations consider both mood match and IMDb rating.",
    },
    "highly_rated": {
        "label": "Highly rated",
        "description": "Recommendations prefer movies with stronger IMDb ratings.",
    },
}


def render_welcome() -> None:
    st.markdown('<p class="cine-title">CineSwipe</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="cine-subtitle">Swipe your mood. Find your movie.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <p class="cine-body">
        CineSwipe learns what you're in the mood for — one card at a time.
        Swipe through mood prompts, like the ones that resonate, and we'll
        recommend films that match your vibe. Like five moods to unlock
        your personalized picks.
        </p>
        """,
        unsafe_allow_html=True,
    )


def _render_pref_option_card(
    card_class: str,
    label: str,
    description: str,
    *,
    is_selected: bool,
) -> None:
    """Render a preference card without indented HTML (avoids markdown code-block escaping)."""
    badge = '<span class="pref-selected-badge">✓ Selected</span>' if is_selected else ""
    card_html = (
        f'<div class="{card_class}">{badge}'
        f'<p class="pref-card-title">{label}</p>'
        f'<p class="pref-card-desc">{description}</p>'
        f"</div>"
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_imdb_preference_screen() -> str:
    st.markdown('<p class="cine-title" style="font-size:2.2rem;">Rating Preference</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="cine-subtitle">How much should IMDb rating matter?</p>',
        unsafe_allow_html=True,
    )

    if "imdb_pref_draft" not in st.session_state:
        st.session_state.imdb_pref_draft = st.session_state.get("imdb_preference", "balanced")

    for key, option in IMDB_OPTIONS.items():
        is_selected = st.session_state.imdb_pref_draft == key
        card_class = "pref-option-card selected" if is_selected else "pref-option-card"
        _render_pref_option_card(
            card_class,
            option["label"],
            option["description"],
            is_selected=is_selected,
        )
        if not is_selected:
            if st.button("Choose", key=f"pref_{key}", use_container_width=True, type="secondary"):
                st.session_state.imdb_pref_draft = key
                st.rerun()

    return st.session_state.imdb_pref_draft


def render_swipe_header(engine: MoodEngine, on_undo: Callable[[], None]) -> None:
    col_title, col_undo = st.columns([3, 1])
    with col_title:
        st.markdown(
            '<p class="cine-title swipe-header-title">Swipe Your Mood</p>',
            unsafe_allow_html=True,
        )
        render_progress(engine)
    with col_undo:
        st.markdown('<div class="swipe-undo-wrap"></div>', unsafe_allow_html=True)
        if st.button(
            "Undo last action",
            use_container_width=True,
            disabled=not engine.can_undo(),
            key="btn_undo",
        ):
            on_undo()


def render_mood_card(card: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="cine-card">
            <p class="section-label">Today's mood</p>
            <p class="mood-card-title">{card['title']}</p>
            <p class="mood-card-desc">{card['description']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_profile_ready_message() -> None:
    st.markdown(
        """
        <div class="profile-ready-card">
            <p class="profile-ready-title">Your mood profile is ready.</p>
            <p class="profile-ready-body">
            You can get recommendations now, remove a mood to edit your profile,
            or undo your last action.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feedback(message: str) -> None:
    if not message:
        return
    skip_prefixes = ("Mood skipped", "Undid skip", "Nothing to undo")
    css_class = "feedback-banner skip" if message.startswith(skip_prefixes) else "feedback-banner"
    st.markdown(f'<div class="{css_class}">{message}</div>', unsafe_allow_html=True)


def render_progress(engine: MoodEngine) -> None:
    label = engine.progress_label()
    css_class = "progress-pill ready" if engine.is_profile_ready else "progress-pill"
    st.markdown(f'<div class="{css_class}">{label}</div>', unsafe_allow_html=True)


def render_selected_moods(
    engine: MoodEngine,
    on_remove: Callable[[str], None],
) -> None:
    if not engine.selected_moods:
        return

    st.markdown('<p class="section-label">Your selected moods</p>', unsafe_allow_html=True)
    st.markdown('<div class="mood-chips-row-marker"></div>', unsafe_allow_html=True)
    chip_cols = st.columns(len(engine.selected_moods))
    for col, card in zip(chip_cols, engine.selected_moods):
        custom_suffix = " custom" if card.get("is_custom") else ""
        label = f"{card['title']}{custom_suffix} ×"
        with col:
            if st.button(label, key=f"remove_{card['id']}", help=f"Remove {card['title']}"):
                on_remove(card["id"])


def render_custom_mood_input(
    engine: MoodEngine,
    on_submit: Callable[[str], None],
) -> None:
    if not engine.can_like_more():
        st.markdown('<p class="section-label">Add your own mood</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="profile-full-note">Your mood profile is full. Remove one mood to add another.</p>',
            unsafe_allow_html=True,
        )
        return

    st.markdown('<p class="section-label">Add your own mood</p>', unsafe_allow_html=True)
    custom_text = st.text_input(
        "Custom mood",
        placeholder="Example: late night nostalgic thriller with rainy atmosphere",
        label_visibility="collapsed",
    )
    if st.button(
        "Add Mood",
        use_container_width=True,
        disabled=not custom_text.strip(),
        key="btn_add_custom",
    ):
        on_submit(custom_text.strip())


def render_top_traits(
    top_traits: list[tuple[str, float]],
    selected_moods: list[dict[str, Any]] | None = None,
) -> None:
    if not top_traits and not selected_moods:
        return

    labels = get_display_mood_signals(
        top_traits,
        selected_moods or [],
    )
    if not labels:
        return

    chips = "".join(f'<span class="trait-chip">{html.escape(label)}</span>' for label in labels)
    st.markdown(
        f'<p class="section-label">Your top mood signals</p>'
        f'<div class="trait-chip-row">{chips}</div>',
        unsafe_allow_html=True,
    )


def render_movie_card(movie: dict[str, Any]) -> None:
    poster_url = movie.get("poster_url")
    title = html.escape(str(movie.get("title", "Unknown")))
    year = html.escape(str(movie.get("year", "—")))
    rating = html.escape(str(movie.get("rating", "N/A")))
    plot = html.escape(str(movie.get("plot", "")))
    match_reason = html.escape(str(movie.get("match_reason", "A great match for your mood.")))

    meta_parts = [f"{year}", f"★ {rating}"]
    if movie.get("genre"):
        meta_parts.append(html.escape(str(movie["genre"])))
    if movie.get("runtime"):
        meta_parts.append(html.escape(str(movie["runtime"])))
    meta_line = " · ".join(meta_parts)

    if poster_url:
        safe_poster = html.escape(str(poster_url), quote=True)
        poster_html = f'<img class="movie-poster" src="{safe_poster}" alt="{title} poster" />'
    else:
        poster_html = '<div class="movie-poster-placeholder"><span>🎬</span></div>'

    card_html = (
        f'<div class="movie-card-row">{poster_html}'
        f'<div class="movie-card-content">'
        f'<p class="movie-title">{title}</p>'
        f'<p class="movie-meta">{meta_line}</p>'
        f'<p class="movie-plot">{plot}</p>'
        f'<span class="movie-match">{match_reason}</span>'
        f"</div></div>"
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_recommendation_mode(source: str, notice: str | None = None) -> None:
    mode_label = "AI powered" if source == "ai" else "Local fallback"
    st.markdown(
        f'<p class="section-label" style="margin-top:0.75rem;">Recommendation mode: {mode_label}</p>',
        unsafe_allow_html=True,
    )
    if notice:
        st.markdown(f'<div class="feedback-banner skip">{html.escape(notice)}</div>', unsafe_allow_html=True)


def render_results_header() -> None:
    st.markdown('<p class="cine-title" style="font-size:2.4rem;">Your Picks</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="cine-subtitle">Curated for the mood you built.</p>',
        unsafe_allow_html=True,
    )
