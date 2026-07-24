import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Placeholder default is intentional here, unlike OPENAI_API_KEY above.
# create_engine() parses this string at *import time* (app/db.py), before
# any actual connection is attempted -- so if DATABASE_URL is unset (e.g.
# GitHub Actions CI, which has no .env and no real database), importing
# app.db would crash immediately just from constructing the Engine object,
# even though tests never actually connect (conftest.py overrides get_db
# with a mock for every test). This placeholder is deliberately fake and
# would fail loudly if anything actually tried to connect with it -- real
# local/production runs always set a real DATABASE_URL via .env or Render's
# environment variables, which takes priority over this fallback.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/placeholder")

BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "poolside/laguna-xs-2.1:free"

MAX_FILE_SIZE = 1024 * 1024
