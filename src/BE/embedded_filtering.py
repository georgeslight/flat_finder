import json
import logging
from dotenv import load_dotenv

load_dotenv(dotenv_path="../../.env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_apartments():
    try:
        with open('output.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading apartments: {e}")
        return []



# def deep_filter(user_data: User, apartments=None):
