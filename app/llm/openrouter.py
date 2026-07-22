from openai import OpenAI
from app.config import OPENAI_API_KEY, BASE_URL

client= OpenAI(api_key=OPENAI_API_KEY, base_url=BASE_URL)