
import logging
import httpx

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def make_request(getting_url: str, user_agent: str):
    with httpx.Client() as client:
        logger.info(f"Getting URL: {getting_url}")
        return client.get(getting_url, headers={'User-Agent': user_agent})
