import logging

from src.substitution_storage import SubstitutionStorage
from src.utils.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        SubstitutionStorage.update()
        logger.info("Update finished successfully.")
    except Exception as e:
        logger.error(f"Error during update: {e}")
