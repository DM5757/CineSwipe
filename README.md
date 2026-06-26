# CineSwipe

**Swipe your mood. Find your movie.**

CineSwipe is a Streamlit MVP for mood-based movie recommendations. Swipe through mood cards, like the ones that resonate, and get curated film picks matched to your vibe.

## Features

- **Welcome screen** — Quick intro and one-tap start
- **Swipe screen** — Like or skip mood cards with live progress feedback
- **Results screen** — 3–5 movie recommendations with match explanations
- **Local data** — No API keys required for the MVP (JSON-backed mood cards and movies)
- **Clean architecture** — Logic, services, UI, and data are separated

## Project Structure

```
CineSwipe/
├── app.py                          # Streamlit entry point
├── requirements.txt
├── .env.example
├── data/
│   ├── mood_cards.json             # Swipeable mood prompts
│   └── fallback_movies.json        # Local movie catalog
├── logic/
│   ├── mood_engine.py              # Card queue, traits, scoring
│   └── recommendation_engine.py    # Trait-based movie matching
├── services/
│   ├── gemini_service.py           # Gemini movie recommendations
│   └── omdb_service.py             # OMDb metadata lookups
├── scripts/
│   └── test_gemini.py              # Safe Gemini API connection test
└── ui/
    ├── components.py               # Reusable UI blocks
    └── styles.py                   # Global styling
```

## Quick Start

1. **Create a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   # source .venv/bin/activate   # macOS/Linux
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**:

   ```bash
   streamlit run app.py
   ```

4. Open the URL shown in your terminal (usually `http://localhost:8501`).

## How It Works

1. Tap **Start Swiping** on the welcome screen.
2. Review mood cards one at a time — tap **Like** or **Skip**.
3. After liking **5 moods**, unlock **Get My Recommendations**.
4. Browse your personalized picks on the results screen.

## Environment Variables

Copy `.env.example` to `.env` when you're ready to wire up external APIs:

```
GEMINI_API_KEY=your_key_here
OMDB_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.0-flash
```

Optional: run `scripts/test_gemini.py` to verify your Gemini key and save a working model to `data/working_gemini_model.txt`.

### Test Gemini API connection

```bash
python scripts/test_gemini.py
```

Windows with the project venv:

```bash
.venv\Scripts\python.exe scripts\test_gemini.py
```

The app falls back to local recommendations if Gemini or OMDb is unavailable.

## Tech Stack

- Python 3.10+
- Streamlit
- JSON data files (no database)

## License

MIT
