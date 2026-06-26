# CineSwipe

**Swipe your mood. Find your movie.**

CineSwipe is a Streamlit app for mood-based movie recommendations. Swipe through mood cards, like the ones that resonate, and get curated film picks matched to your vibe — powered by Gemini and OMDb, with a local fallback when APIs are unavailable.

## Features

- **Welcome screen** — Quick intro and one-tap start
- **Rating preference** — Choose how much IMDb rating should matter
- **Swipe screen** — Like or skip mood cards with live progress feedback
- **Custom moods** — Add your own mood text
- **Results screen** — AI-powered movie picks with OMDb metadata and posters
- **Local fallback** — Works offline with JSON-backed mood cards and movies
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
│   ├── recommendation_engine.py  # AI + fallback recommendation flow
│   └── profile_cache.py            # Recommendation session caching
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

3. **Set up environment variables**:

   Copy `.env.example` to `.env`, then add your API keys:

   ```
   GEMINI_API_KEY=your_key_here
   OMDB_API_KEY=your_key_here
   GEMINI_MODEL=gemini-2.5-flash-lite
   ```

   **Recommended Gemini model:** `gemini-2.5-flash-lite`

4. **Run the app**:

   ```bash
   streamlit run app.py
   ```

   Windows with the project venv:

   ```bash
   .venv\Scripts\python.exe -m streamlit run app.py
   ```

5. Open the URL shown in your terminal (usually `http://localhost:8501`).

## How It Works

1. Tap **Start** on the welcome screen.
2. Choose your IMDb rating preference.
3. Review mood cards one at a time — tap **Like** or **Skip**.
4. After liking **5 moods**, unlock **Get My Recommendations**.
5. Browse your personalized picks on the results screen.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Gemini API key |
| `OMDB_API_KEY` | OMDb API key |
| `GEMINI_MODEL` | Optional. Defaults to `gemini-2.5-flash-lite`, or uses `data/working_gemini_model.txt` if present |

The app falls back to local recommendations if Gemini or OMDb is unavailable.

### Test Gemini API connection

```bash
python scripts/test_gemini.py
```

Windows with the project venv:

```bash
.venv\Scripts\python.exe scripts\test_gemini.py
```

On success, the working model is saved to `data/working_gemini_model.txt` (local machine state, not committed).

## Tech Stack

- Python 3.10+
- Streamlit
- Google Gemini (`google-genai`)
- OMDb API
- JSON data files (no database)

## License

MIT
