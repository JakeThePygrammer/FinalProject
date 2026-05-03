import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gemini-3-flash-preview"

def generate_text(prompt: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        return "GEMINI_API_KEY is missing from the .env file"

    client = genai.Client(api_key=api_key) 

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        return (response.text or "").strip() or "No ai result."
    except Exception as e:
        return f"AI error: {e}"