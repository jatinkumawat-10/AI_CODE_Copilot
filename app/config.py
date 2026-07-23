from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "poolside/laguna-xs-2.1:free"

MAX_FILE_SIZE = 1024 * 1024