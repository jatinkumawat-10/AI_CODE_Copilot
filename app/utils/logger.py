import logging

# idempotency test commit
# Logs to both console (as before) and app.log -- the file handler exists
# specifically so logs can be inspected directly (`tail -f app.log`)
# independent of which terminal tab happens to be showing uvicorn's
# scrollback, which has been a real source of confusion today.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ],
)
logger = logging.getLogger("CODE_REVIEW_Copilot")
