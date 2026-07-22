from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing. Check your .env file.")

BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "poolside/laguna-xs-2.1:free"