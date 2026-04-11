# City Bite Finder (Flask + SQLite + Gemini + OpenStreetMap)

## Setup
1. `python -m venv .venv`
2. Activate venv
3. `pip install -r requirements.txt`
4. Copy `.env.example` -> `.env` and set `GEMINI_API_KEY`
5. `python app.py`

## Features
- CRUD for food spots
- External API (no key): OpenStreetMap Nominatim to get full city name
- Gemini AI:
  - Rewrite description (Macedonian, short)
  - Suggest tags (comma-separated)
