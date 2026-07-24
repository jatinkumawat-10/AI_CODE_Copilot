import logging
# trivial test change to trigger a synchronize webhook event
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("CODE_REVIEW_Copilot")
