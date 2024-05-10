from typing import Union
import logging
import httpx
import tarfile 
import io
import os 
import json

from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.responses import RedirectResponse, StreamingResponse

app = FastAPI()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def create_tarfile(file_paths: [str] = ["requirements.txt",]):
    # Create an in-memory file
    data = io.BytesIO()

    # Create a tarfile in the in-memory file
    with tarfile.open(fileobj=data, mode='w:gz') as tar:
        for file_path in file_paths:
            tar.add(file_path)
        info = tarfile.TarInfo(name='test.txt')
        info.size = len('This is a test file')
        tar.addfile(info, io.BytesIO('This is a test file'.encode()))
    data.seek(0)
    return data

async def make_request(getting_url: str, user_agent: str):
    async with httpx.AsyncClient() as client:
        logger.info(f"Getting URL: {getting_url}")
        r = await client.get(getting_url, headers={'User-Agent': user_agent})
    return r

@app.get("/")
def read_root(request: Request):
    user_agent = request.headers.get('user-agent')
    return {"Hello": "World", "User-Agent": user_agent, "pwd": os.getcwd()}


@app.get("/v1/ping")
def v1_ping():
    return Response(headers={'x-conan-server-version': '0.20.0', 'x-conan-server-capabilities': 'complex_search,checksum_deploy,revisions,matrix_params'})

@app.get("/{url_path:path}")
async def get_external_site(request: Request, url_path: str):

    # User Agent Manipulation
    user_agent = request.headers.get('user-agent')
    if not user_agent.startswith("Conan"):
        user_agent = "Conan/1.65.0-dev (Windows 10; Python 3.12.2; AMD64)"

    # Remote Source Selection
    # example /r/github+bincrafters_remote+testing_v-1000+bincrafters/
    remote_type = "conancenter"
    remote_types_allowed = ["local", "github", "conancenter"]
    remote_source = "bincrafters/remote" # this is not allowed to have underscores
    remote_checkout = "testing/v-1000" # this is not allowed to have underscores
    remote_selection = "bincrafters"
    remote_config = f"{remote_type}+{remote_source}+{remote_checkout}+{remote_selection}"
    if url_path.startswith("r/"):
        remote_config = url_path.split('/')[1]
        # remote_type, remote_source, remote_checkout = remote_config.split("+")
        remote_type, *remote_confs = remote_config.split("+")
        if remote_type in ["local", "github"]:
            remote_source = remote_confs[0].replace("_", "/")
            remote_checkout = remote_confs[1].replace("_", "/")
            if remote_confs[2]:
                remote_selection = remote_confs[2]
        url_path = "/".join(url_path.split('/')[2:])   
    remote_http_suffix = ""
    remote_http_url = f"https://raw.githubusercontent.com/{remote_source}/{remote_checkout}/r/{remote_selection}/"
    if remote_type == "conancenter":
        remote_http_url = "https://center.conan.io/"
        remote_config = "conancenter"
    elif remote_type == "github":
        remote_http_url = f"https://raw.githubusercontent.com/{remote_source}/{remote_checkout}/r/{remote_selection}/"

    cache_url_path = os.path.join("r", remote_config, url_path)

    logger.info(f"Remote Type: {remote_type}, Remote Source: {remote_source}, Remote Checkout: {remote_checkout}, Remote Selection: {remote_selection}, Remote HTTP URL: {remote_http_url}, Remote HTTP Suffix: {remote_http_suffix}")
    logger.info(f"url_path: {url_path}, cache_url_path: {cache_url_path}")

    default_response_type = "application/json"

    # Special handling of binary files
    if url_path.endswith(".tgz"):
        # data = create_tarfile()
        filename = url_path.split('/')[-1]
        remote_http_suffix = ".json"

        # Create an in-memory file
        data = io.BytesIO()

        # Create a tarfile in the in-memory file
        with tarfile.open(fileobj=data, mode='w:gz') as tar:
            #for file_path in file_paths:
            #    tar.add(file_path)

            file_list_r = await make_request(f"{remote_http_url}{url_path}{remote_http_suffix}", user_agent)
            logger.info(f"File List url: {remote_http_url}{url_path}{remote_http_suffix}")
            logger.info(f"File List: {file_list_r.content}")
            file_list = file_list_r.json()
            logger.info(f"File List: {file_list}")
            for tar_file in file_list["files"]:
                url_path_dir = "/".join(url_path.split('/')[:-1])
                file_content_r = await make_request(f"{remote_http_url}{url_path_dir}/{tar_file}", user_agent)
                file_content = file_content_r.content
                tar_filename = "/".join(tar_file.split('/')[1:])
                info = tarfile.TarInfo(name=tar_file)
                info.size = len(file_content)
                tar.addfile(info, io.BytesIO(file_content))
        data.seek(0)

        # Create a StreamingResponse to return the tarfile
        response = StreamingResponse(data, media_type='application/gzip')
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    elif url_path.endswith(".txt") or url_path.endswith(".py"):
        default_response_type = "text/plain"
    else:
        if remote_type in ["local", "github"]:
            remote_http_suffix = ".json"

    async with httpx.AsyncClient() as client:
        getting_url = f"{remote_http_url}{url_path}{remote_http_suffix}"
        logger.info(f"Getting URL: {getting_url}")
        r = await client.get(getting_url, headers={'User-Agent': user_agent})

    logger.info(f"Headers: {r.headers}")
    content_type = r.headers.get('Content-Type', 'application/json')
    if remote_http_suffix == ".json":
        content_type = "application/json"

    # Create caches, mostly for debugging
    cache_path = os.path.join("cache", *cache_url_path.split('/'))
    os.makedirs(cache_path, exist_ok=True)
    with open(os.path.join(cache_path, "response.txt"), 'wb') as f:
        f.write(user_agent.encode())
        f.write(json.dumps(dict(r.headers)).encode())
        f.write("\n".encode())
        f.write("\n".encode())
        f.write(r.content)

    return Response(content=r.content, media_type=content_type, headers={'x-conan-server-version': '0.20.0', 'x-conan-server-capabilities': 'complex_search,checksum_deploy,revisions,matrix_params'})



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
