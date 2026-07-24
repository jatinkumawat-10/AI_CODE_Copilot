import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "poolside/laguna-xs-2.1:free"

MAX_FILE_SIZE = 1024 * 1024
