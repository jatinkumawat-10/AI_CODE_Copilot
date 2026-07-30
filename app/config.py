import os

from dotenv import load_dotenv

load_dotenv()


def _clean_env(key: str) -> str | None:
    """
    Reads an environment variable and strips leading/trailing whitespace,
    including newlines. Found necessary in production: GITHUB_PAT had a
    trailing '\\n' after being pasted into Render's environment variable
    UI, which made httpx reject the resulting Authorization header
    ("Illegal header value") since HTTP headers cannot contain newlines.
    Stripping defensively here means this class of copy-paste issue can't
    silently break auth again, regardless of which platform's UI it's
    set through.
    """
    value = os.getenv(key)
    return value.strip() if value is not None else None


OPENAI_API_KEY = _clean_env("OPENAI_API_KEY")
GITHUB_WEBHOOK_SECRET = _clean_env("GITHUB_WEBHOOK_SECRET")
GITHUB_PAT = _clean_env("GITHUB_PAT")

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
DATABASE_URL = (
    _clean_env("DATABASE_URL") or "postgresql://user:pass@localhost/placeholder"
)

BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "poolside/laguna-xs-2.1:free"

MAX_FILE_SIZE = 1024 * 1024

BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "poolside/laguna-xs-2.1:free"

MAX_FILE_SIZE = 1024 * 1024
