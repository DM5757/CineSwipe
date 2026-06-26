"""CineSwipe — Swipe-based movie recommendation app."""

import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from logic.custom_mood import build_custom_mood_card
from logic.mood_engine import MoodEngine
from logic.profile_cache import build_profile_signature
from logic.recommendation_engine import get_recommendations
from ui.components import (
    render_custom_mood_input,
    render_feedback,
    render_imdb_preference_screen,
    render_mood_card,
    render_movie_card,
    render_profile_ready_message,
    render_recommendation_mode,
    render_results_header,
    render_selected_moods,
    render_swipe_header,
    render_top_traits,
    render_welcome,
)
from ui.styles import inject_styles

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"


def load_json(filename: str) -> list[dict]:
    with open(DATA_DIR / filename, encoding="utf-8") as file:
        return json.load(file)


def init_session_state() -> None:
    defaults = {
        "screen": "welcome",
        "mood_engine": None,
        "recommendations": [],
        "recommendation_source": "fallback",
        "recommendation_notice": None,
        "recommendation_profile_signature": None,
        "mood_cards": [],
        "movies": [],
        "imdb_preference": "balanced",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state.mood_cards:
        st.session_state.mood_cards = load_json("mood_cards.json")
    if not st.session_state.movies:
        st.session_state.movies = load_json("fallback_movies.json")
    if st.session_state.mood_engine is None:
        st.session_state.mood_engine = MoodEngine(st.session_state.mood_cards)


def go_to(screen: str) -> None:
    st.session_state.screen = screen
    st.rerun()


def _invalidate_recommendation_cache() -> None:
    st.session_state.recommendations = []
    st.session_state.recommendation_source = "fallback"
    st.session_state.recommendation_notice = None
    st.session_state.recommendation_profile_signature = None


def reset_session() -> None:
    st.session_state.mood_engine = MoodEngine(st.session_state.mood_cards)
    _invalidate_recommendation_cache()
    st.session_state.imdb_preference = "balanced"
    if "imdb_pref_draft" in st.session_state:
        st.session_state.imdb_pref_draft = "balanced"
    st.session_state.screen = "welcome"


def _mood_profile_inputs(engine: MoodEngine) -> tuple[list[str], list[str]]:
    selected_titles = [
        mood["title"] for mood in engine.selected_moods if not mood.get("is_custom")
    ]
    custom_moods = [
        mood.get("description") or mood["title"]
        for mood in engine.selected_moods
        if mood.get("is_custom")
    ]
    return selected_titles, custom_moods


def render_welcome_screen() -> None:
    render_welcome()
    if st.button("Start", type="primary", use_container_width=True):
        st.session_state.mood_engine = MoodEngine(st.session_state.mood_cards)
        st.session_state.imdb_pref_draft = st.session_state.imdb_preference
        go_to("imdb_pref")


def render_imdb_pref_screen() -> None:
    choice = render_imdb_preference_screen()

    col_back, col_continue = st.columns(2)
    with col_back:
        if st.button("Back", use_container_width=True):
            go_to("welcome")
    with col_continue:
        if st.button("Continue to Swiping", type="primary", use_container_width=True):
            if st.session_state.imdb_preference != choice:
                _invalidate_recommendation_cache()
            st.session_state.imdb_preference = choice
            go_to("swipe")


def render_swipe_screen() -> None:
    engine: MoodEngine = st.session_state.mood_engine

    render_swipe_header(engine, on_undo=lambda: _handle_undo(engine))
    render_feedback(engine.last_feedback)
    render_selected_moods(engine, on_remove=lambda card_id: _handle_remove(engine, card_id))

    if engine.is_profile_ready:
        render_profile_ready_message()
    else:
        card = engine.get_current_card()
        if card is None:
            st.markdown(
                '<p class="cine-body" style="margin-bottom:1rem;">No more mood cards in the deck. Add a custom mood or remove one to keep editing.</p>',
                unsafe_allow_html=True,
            )
        else:
            render_mood_card(card)

            col_skip, col_like = st.columns(2)
            with col_skip:
                if st.button("Skip", use_container_width=True, key="btn_skip"):
                    engine.skip()
                    st.rerun()
            with col_like:
                if st.button("Like", type="primary", use_container_width=True, key="btn_like"):
                    engine.like()
                    st.rerun()

    render_custom_mood_input(engine, on_submit=lambda text: _handle_custom_mood(engine, text))

    st.divider()

    if engine.can_recommend():
        if st.button("Get My Recommendations", type="primary", use_container_width=True):
            _generate_recommendations(engine)
    else:
        remaining = max(0, 5 - engine.liked_count)
        st.button(
            f"Like {remaining} more mood{'s' if remaining != 1 else ''} to unlock",
            disabled=True,
            use_container_width=True,
        )

    if st.button("Back to Welcome", use_container_width=True):
        go_to("welcome")


def _generate_recommendations(engine: MoodEngine) -> None:
    selected_titles, custom_moods = _mood_profile_inputs(engine)
    top_traits = engine.get_top_traits()
    profile_signature = build_profile_signature(
        engine.selected_moods,
        top_traits,
        st.session_state.imdb_preference,
    )

    if (
        st.session_state.get("recommendation_profile_signature") == profile_signature
        and st.session_state.get("recommendations")
    ):
        go_to("results")
        return

    with st.spinner("Finding movies that match your mood..."):
        recommendations, source, notice = get_recommendations(
            trait_scores=engine.trait_scores,
            top_traits=top_traits,
            selected_mood_titles=selected_titles,
            custom_moods=custom_moods,
            fallback_movies=st.session_state.movies,
            imdb_preference=st.session_state.imdb_preference,
        )

    st.session_state.recommendations = recommendations
    st.session_state.recommendation_source = source
    st.session_state.recommendation_notice = notice
    st.session_state.recommendation_profile_signature = profile_signature
    go_to("results")


def _handle_undo(engine: MoodEngine) -> None:
    engine.undo()
    _invalidate_recommendation_cache()
    st.rerun()


def _handle_remove(engine: MoodEngine, card_id: str) -> None:
    engine.remove_selected(card_id)
    _invalidate_recommendation_cache()
    st.rerun()


def _handle_custom_mood(engine: MoodEngine, text: str) -> None:
    card = build_custom_mood_card(text)
    engine.add_custom_mood(card)
    _invalidate_recommendation_cache()
    st.rerun()


def render_results_screen() -> None:
    engine: MoodEngine = st.session_state.mood_engine
    render_results_header()
    render_top_traits(engine.get_top_traits(), engine.selected_moods)

    pref_label = {
        "mood_first": "Mood first",
        "balanced": "Balanced",
        "highly_rated": "Highly rated",
    }.get(st.session_state.imdb_preference, "Balanced")
    st.markdown(
        f'<p class="section-label" style="margin-top:1rem;">Rating preference: {pref_label}</p>',
        unsafe_allow_html=True,
    )

    render_recommendation_mode(
        st.session_state.get("recommendation_source", "fallback"),
        st.session_state.get("recommendation_notice"),
    )

    st.markdown('<p class="section-label" style="margin-top:1rem;">Recommended for you</p>', unsafe_allow_html=True)

    for movie in st.session_state.recommendations:
        render_movie_card(movie)

    with st.expander("Technical details"):
        st.caption("Errors are logged to the console. API keys are never shown in the UI.")

    col_restart, col_edit = st.columns(2)
    with col_restart:
        if st.button("Start Over", use_container_width=True):
            reset_session()
            st.rerun()
    with col_edit:
        if st.button("Edit Mood Profile", use_container_width=True):
            go_to("swipe")


def main() -> None:
    st.set_page_config(
        page_title="CineSwipe",
        page_icon="🎬",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    inject_styles()
    init_session_state()

    screen = st.session_state.screen
    if screen == "welcome":
        render_welcome_screen()
    elif screen == "imdb_pref":
        render_imdb_pref_screen()
    elif screen == "swipe":
        render_swipe_screen()
    elif screen == "results":
        render_results_screen()


if __name__ == "__main__":
    main()
