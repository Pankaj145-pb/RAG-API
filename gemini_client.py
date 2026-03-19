# gemini_client.py
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY environment variable")

# single shared client instance
client = genai.Client(api_key=GEMINI_API_KEY)