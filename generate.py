from typing import Union
import logging
import httpx
import tarfile 
import io
import os 
import json
import shutil

from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.responses import RedirectResponse, StreamingResponse
import uvicorn


app = FastAPI()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


async def make_request(getting_url: str, user_agent: str):
    async with httpx.AsyncClient() as client:
        logger.info(f"Getting URL: {getting_url}")
        r = await client.get(getting_url, headers={'User-Agent': user_agent})
    return r

@app.get("/{url_path:path}")
async def get_external_site(request: Request, url_path: str):

    # User Agent Manipulation
    user_agent = request.headers.get('user-agent')
    if not user_agent.startswith("Conan"):
        user_agent = "Conan/1.65.0-dev (Windows 10; Python 3.12.2; AMD64)"

    # Remote Configuration
    # /r/conan+url+name/
    remote_type = "conan"
    remote_types_allowed = ["conan",]
    remote_http_url = "https://bincrafters.jfrog.io/artifactory/api/conan/conan-legacy-inexorgame/"
    remote_config = "inexorgame"

    cache_url_path = os.path.join("r", remote_config, url_path.replace("/", os.sep))

    # logger.info(f"Remote Type: {remote_type}, Remote HTTP URL: {remote_http_url}")
    # logger.info(f"url_path: {url_path}, cache_url_path: {cache_url_path}")

    default_response_type = "application/json"
    if url_path.endswith(".txt") or url_path.endswith(".py"):
        default_response_type = "text/plain"

    r = await make_request(f"{remote_http_url}{url_path}", user_agent)
    # logger.info(f"Headers: {r.headers}")
    content_type = r.headers.get("Content-Type", default_response_type)

    cache_path = os.path.join("cache", "generate", *cache_url_path.split(os.sep))

    if content_type == "application/json":
        cache_path += ".json"

    filename = cache_path.split(os.sep)[-1]
    new_tgz_file_dir = ""
    if filename.endswith(".tgz"):
        new_tgz_file_dir = filename.replace(".tgz", "")
        cache_dir = os.path.join(os.path.dirname(cache_path))
    else:
        if "." in filename:
            cache_dir = os.path.dirname(cache_path)
        else:
            cache_dir = os.sep.join(cache_path.split(os.sep)[:-1])

    logger.info(f"cache_path: {cache_path}")
    logger.info(f"cache_dir: {cache_dir}")
    os.makedirs(cache_dir, exist_ok=True)

    if filename.endswith(".tgz"):
        tar_file = tarfile.open(fileobj=io.BytesIO(r.content), mode='r:gz')
        tar_file.extractall(os.path.join(cache_dir, new_tgz_file_dir))
        json_data = {"files": [f"{new_tgz_file_dir}/{f.name}" for f in tar_file.getmembers()]}
        tar_file.close()
        with open(os.path.join(cache_dir, filename + ".json"), "w") as f:
            json.dump(json_data, f)
        with open(os.path.join(cache_path), "wb") as f:
            f.write(r.content)
    else:
        with open(os.path.join(cache_path), "wb") as f:
            f.write(r.content)

    return Response(content=r.content, media_type=content_type, headers={'x-conan-server-version': '0.20.0', 'x-conan-server-capabilities': 'complex_search,checksum_deploy,revisions,matrix_params'})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
