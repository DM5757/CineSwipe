"""Global CSS and theme tokens for CineSwipe."""

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background: linear-gradient(160deg, #0a0a12 0%, #12121f 45%, #1a1028 100%);
            color: #f4f4f8;
        }

        #MainMenu, footer, header { visibility: hidden; }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 720px;
        }

        .cine-title {
            font-size: 3.2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            background: linear-gradient(135deg, #ffffff 0%, #c4b5fd 50%, #f472b6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.25rem;
            line-height: 1.1;
        }

        .cine-subtitle {
            font-size: 1.25rem;
            color: #a8a8b8;
            margin-bottom: 1.5rem;
            font-weight: 500;
        }

        .cine-body {
            color: #c8c8d4;
            font-size: 1.05rem;
            line-height: 1.7;
            margin-bottom: 2rem;
        }

        .cine-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 2rem 2rem 1.75rem;
            margin: 1rem 0 1.5rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(12px);
        }

        .mood-card-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.75rem;
        }

        .mood-card-desc {
            font-size: 1.1rem;
            color: #b8b8c8;
            line-height: 1.65;
        }

        .movie-card-row {
            display: flex;
            gap: 1.25rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 16px;
            padding: 1.25rem;
            margin-bottom: 1rem;
        }

        .movie-poster {
            width: 100px;
            min-width: 100px;
            height: 150px;
            object-fit: cover;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .movie-poster-placeholder {
            width: 100px;
            min-width: 100px;
            height: 150px;
            border-radius: 10px;
            background: linear-gradient(145deg, rgba(139, 92, 246, 0.15), rgba(30, 30, 50, 0.8));
            border: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
        }

        .movie-card-content {
            flex: 1;
            min-width: 0;
        }

        .movie-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.35rem;
        }

        .movie-meta {
            color: #9b9bb0;
            font-size: 0.95rem;
            margin-bottom: 0.75rem;
        }

        .movie-plot {
            color: #c4c4d4;
            font-size: 1rem;
            line-height: 1.6;
            margin-bottom: 0.85rem;
        }

        .movie-match {
            display: inline-block;
            background: rgba(167, 139, 250, 0.15);
            border: 1px solid rgba(167, 139, 250, 0.35);
            color: #ddd6fe;
            font-size: 0.9rem;
            padding: 0.45rem 0.85rem;
            border-radius: 999px;
        }

        .feedback-banner {
            background: rgba(52, 211, 153, 0.12);
            border: 1px solid rgba(52, 211, 153, 0.35);
            color: #6ee7b7;
            padding: 0.75rem 1.1rem;
            border-radius: 12px;
            font-size: 0.95rem;
            margin: 0.75rem 0 1.25rem;
            text-align: center;
        }

        .feedback-banner.skip {
            background: rgba(148, 163, 184, 0.12);
            border-color: rgba(148, 163, 184, 0.3);
            color: #cbd5e1;
        }

        .progress-pill {
            display: inline-block;
            background: rgba(244, 114, 182, 0.12);
            border: 1px solid rgba(244, 114, 182, 0.35);
            color: #f9a8d4;
            font-size: 0.95rem;
            font-weight: 600;
            padding: 0.5rem 1.1rem;
            border-radius: 999px;
            margin-bottom: 1rem;
        }

        .progress-pill.ready {
            background: rgba(52, 211, 153, 0.12);
            border-color: rgba(52, 211, 153, 0.35);
            color: #6ee7b7;
        }

        .profile-ready-card {
            background: rgba(52, 211, 153, 0.08);
            border: 1px solid rgba(52, 211, 153, 0.25);
            border-radius: 16px;
            padding: 1.5rem 1.75rem;
            margin: 1rem 0 1.5rem;
        }

        .profile-ready-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #6ee7b7;
            margin-bottom: 0.5rem;
        }

        .profile-ready-body {
            color: #b8c8c0;
            font-size: 1rem;
            line-height: 1.6;
            margin: 0;
        }

        .selected-mood-chip {
            background: rgba(139, 92, 246, 0.12);
            border: 1px solid rgba(139, 92, 246, 0.3);
            color: #e9d5ff;
            font-size: 0.9rem;
            font-weight: 500;
            padding: 0.55rem 0.9rem;
            border-radius: 10px;
            margin-bottom: 0.35rem;
        }

        .mood-chips-row-marker + div div[data-testid="stHorizontalBlock"] {
            gap: 0.35rem;
            flex-wrap: wrap;
            margin-bottom: 0.5rem;
        }

        .mood-chips-row-marker + div div[data-testid="stHorizontalBlock"] button {
            min-height: 2rem !important;
            padding: 0.3rem 0.65rem !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            border-radius: 999px !important;
            background: rgba(139, 92, 246, 0.12) !important;
            border: 1px solid rgba(139, 92, 246, 0.3) !important;
            color: #e9d5ff !important;
            white-space: nowrap;
            width: 100%;
            box-shadow: none !important;
        }

        .mood-chips-row-marker + div div[data-testid="stHorizontalBlock"] button:hover {
            background: rgba(236, 72, 153, 0.18) !important;
            border-color: rgba(236, 72, 153, 0.45) !important;
            color: #fce7f3 !important;
        }

        .chip-custom {
            display: inline-block;
            background: rgba(244, 114, 182, 0.2);
            color: #f9a8d4;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding: 0.15rem 0.45rem;
            border-radius: 6px;
            margin-left: 0.5rem;
            vertical-align: middle;
        }

        .swipe-header-title {
            font-size: 2.2rem !important;
            margin-bottom: 0.5rem !important;
        }

        .undo-spacer {
            height: 0.35rem;
        }

        .swipe-undo-wrap + div .stButton > button {
            min-height: 2.25rem !important;
            font-size: 0.82rem !important;
            padding: 0.4rem 0.65rem !important;
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            color: #a8a8b8 !important;
            box-shadow: none !important;
        }

        .swipe-undo-wrap + div .stButton > button:hover:not(:disabled) {
            border-color: rgba(167, 139, 250, 0.35) !important;
            color: #c4b5fd !important;
        }

        .profile-full-note {
            color: #a8a8b8;
            font-size: 0.95rem;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin: 0 0 0.5rem;
        }

        /* Rating preference option cards */
        .pref-option-card {
            position: relative;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 1.15rem 1.35rem 0.85rem;
            margin-bottom: 0.35rem;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .pref-option-card.selected {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.18), rgba(236, 72, 153, 0.12));
            border: 2px solid rgba(236, 72, 153, 0.55);
            box-shadow: 0 0 24px rgba(139, 92, 246, 0.3);
            margin-bottom: 0.85rem;
        }

        .pref-selected-badge {
            position: absolute;
            top: 0.8rem;
            right: 0.85rem;
            background: rgba(76, 29, 149, 0.45);
            border: 1px solid rgba(192, 132, 252, 0.45);
            box-shadow: 0 0 12px rgba(139, 92, 246, 0.28);
            color: #e9d5ff;
            font-size: 0.72rem;
            font-weight: 600;
            padding: 0.28rem 0.6rem;
            border-radius: 999px;
            letter-spacing: 0.02em;
            line-height: 1.2;
        }

        .pref-card-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #ffffff;
            margin: 0 0 0.4rem;
        }

        .pref-option-card.selected .pref-card-title {
            background: linear-gradient(135deg, #ffffff, #f9a8d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .pref-card-desc {
            font-size: 0.95rem;
            color: #b8b8c8;
            line-height: 1.55;
            margin: 0;
        }

        .pref-option-card + div .stButton > button {
            min-height: 2.25rem !important;
            margin-bottom: 0.85rem !important;
            font-size: 0.88rem !important;
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #c8c8d4 !important;
            box-shadow: none !important;
        }

        .pref-option-card + div .stButton > button:hover {
            border-color: rgba(167, 139, 250, 0.35) !important;
            background: rgba(139, 92, 246, 0.08) !important;
        }

        button[data-testid="stBaseButton-secondary"] {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: #c8c8d4 !important;
        }

        button[data-testid="stBaseButton-secondary"]:hover {
            border-color: rgba(167, 139, 250, 0.35) !important;
            background: rgba(139, 92, 246, 0.08) !important;
        }

        button[data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, #8b5cf6, #ec4899) !important;
            border: none !important;
            box-shadow: 0 8px 30px rgba(139, 92, 246, 0.35) !important;
            color: #ffffff !important;
        }

        /* Tighter swipe layout */
        .feedback-banner {
            margin: 0.35rem 0 0.75rem;
            padding: 0.55rem 0.9rem;
            font-size: 0.88rem;
        }

        .progress-pill {
            margin-bottom: 0.35rem;
        }

        .cine-card {
            margin: 0.5rem 0 1rem;
            padding: 1.5rem 1.65rem 1.35rem;
        }

        .profile-ready-card {
            margin: 0.5rem 0 1rem;
            padding: 1.15rem 1.35rem;
        }

        .section-label {
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: #7c7c90;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        div[data-testid="stHorizontalBlock"] button {
            min-height: 3.25rem;
            font-size: 1.05rem;
            font-weight: 600;
            border-radius: 14px !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #8b5cf6, #ec4899) !important;
            border: none !important;
            color: white !important;
            font-weight: 700 !important;
            padding: 0.75rem 2rem !important;
            border-radius: 14px !important;
            box-shadow: 0 8px 30px rgba(139, 92, 246, 0.35);
        }

        .stButton > button[kind="primary"]:hover {
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.5);
        }

        .stButton > button:disabled {
            opacity: 0.45 !important;
        }

        .trait-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1.25rem;
        }

        .trait-chip {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #a8a8b8;
            font-size: 0.8rem;
            padding: 0.3rem 0.7rem;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
