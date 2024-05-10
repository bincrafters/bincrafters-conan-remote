
import logging
import httpx

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


conf = {
    "filename_server_conan_headers": "server_headers.json",
    "user_agent_default": "Conan/1.65.0-dev (Windows 10; Python 3.12.2; AMD64)",
}

def make_request(getting_url: str, user_agent: str, follow_redirects: bool = True):
    with httpx.Client(follow_redirects=follow_redirects) as client:
        logger.info(f"Getting URL: {getting_url}")
        return client.get(getting_url, headers={'User-Agent': user_agent})
