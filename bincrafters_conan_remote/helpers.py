
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)

conf = {
    "filename_server_conan_headers": "server_headers.json",
    "headers_default": {"x-conan-server-version": "0.20.0", "x-conan-server-capabilities": "complex_search,checksum_deploy,revisions,matrix_params"},
    "user_agent_default": "Conan/1.65.0-dev (Windows 10; Python 3.12.2; AMD64)",
    "remote_default_type": "github",
    "remote_default_source": "bincrafters/remote",
    "remote_default_checkout": "testing/v-998",
    "remote_default_selection": "inexorgame",
}

def make_request(getting_url: str, user_agent: str, follow_redirects: bool = True):
    with httpx.Client(follow_redirects=follow_redirects) as client:
        logger.info(f"Getting URL: {getting_url}")
        return client.get(getting_url, headers={"User-Agent": user_agent})


async def make_request_async_multiple(urls: list[str], user_agent: str, follow_redirects: bool = True):
    async def _make_request_async(getting_url: str, client: httpx.AsyncClient):
        logger.info(f"Getting URL: {getting_url}")
        response = await client.get(getting_url, headers={"User-Agent": user_agent})
        return response

    async with httpx.AsyncClient(follow_redirects=follow_redirects) as client:
        requests = [_make_request_async(url, client) for url in urls]
        response = await asyncio.gather(*requests)
        return response
