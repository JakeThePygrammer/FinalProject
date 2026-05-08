import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()


def generate_text(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "GEMINI_API_KEY is missing from .env"

    # URL FIX: We use the v1beta endpoint with the exact name from your list
    # Note: We don't include 'models/' in the URL string because the path handles it
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)

        if response.status_code == 200:
            result = response.json()
            # Extract the text from the Gemini 3 response structure
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            return f"AI Error {response.status_code}: {response.text}"

    except Exception as e:
        return f"Connection error: {e}"