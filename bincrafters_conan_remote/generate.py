from typing import Union
import logging
import tarfile 
import io
import os 
import json
import shutil
import subprocess
import atexit
import time
import argparse
import threading

from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.responses import RedirectResponse, StreamingResponse
import uvicorn

from bincrafters_conan_remote.helpers import conf, make_request


app = FastAPI(debug=True)
logger = logging.getLogger("bincrafters-conan-remote")

cached_headers = {}
# Toggle, if True then it saves .tgz files
CREATE_FULL_LOCAL_BACKUP = False


@app.get("/{url_path:path}")
async def get_external_site(request: Request, url_path: str):

    # Remote Configuration
    # /r/conan+{url}+name/
    remote_type = "conan"
    remote_types_allowed = ["conan",]
    remote_http_url = "https://bincrafters.jfrog.io/artifactory/api/conan/conan-legacy-inexorgame/"
    remote_config = "inexorgame"

    if url_path.startswith("r/"):
        url_path = url_path[len("r/"):]
        remote_type = url_path.split("+")[0]
        url_path = url_path[len(remote_type)+2:] # +2 to remove both + and {
        
        remote_http_url = url_path.split("}")[0]
        url_path = url_path[len(remote_http_url)+2:] # +2 to remove both } and +

        remote_config = url_path.split("/")[0]
        url_path = url_path[len(remote_config)+1:] # +1 /

    cache_url_path = os.path.join("r", remote_config, url_path.replace("/", os.sep))

    # logger.info(f"Remote Type: {remote_type}, Remote HTTP URL: {remote_http_url}, Remote Name: {remote_config}")
    # logger.info(f"url_path: {url_path}, cache_url_path: {cache_url_path}")

    if url_path == "v1/ping" and len(cached_headers) != 0:
        # logger.info(f"Cached headers: {cached_headers}")
        return Response(headers=cached_headers)

    # User Agent Manipulation
    user_agent = request.headers.get('user-agent')
    if not user_agent.startswith("Conan"):
        user_agent = conf["user_agent_default"]

    default_response_type = "application/json"
    if url_path.endswith(".txt") or url_path.endswith(".py"):
        default_response_type = "text/plain"
    elif url_path.endswith(".tgz"):
        default_response_type = "application/gzip"

    r = make_request(f"{remote_http_url}{url_path}", user_agent)
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
    # logger.info(f"cache_dir: {cache_dir}")
    os.makedirs(cache_dir, exist_ok=True)

    if url_path == "v1/ping":
        for header in r.headers:
            if header.startswith("x-conan"):
                cached_headers[header] = r.headers[header]
        cache_path_parts = cache_path.split(os.sep)
        with open(os.path.join(*cache_path_parts[:4], conf["filename_server_conan_headers"]), "w") as f:
            f.write(json.dumps(cached_headers))

    if not url_path in ["v1/ping",]:
        if filename.endswith(".tgz"):
            if CREATE_FULL_LOCAL_BACKUP:
                with open(os.path.join(cache_path), "wb") as f:
                    f.write(r.content)
            tar_file = tarfile.open(fileobj=io.BytesIO(r.content), mode='r:gz')
            tar_file.extractall(os.path.join(cache_dir, new_tgz_file_dir))
            json_data = {"files": [f"{new_tgz_file_dir}/{f.name}" for f in tar_file.getmembers()]}
            tar_file.close()
            with open(os.path.join(cache_dir, filename + ".json"), "w") as f:
                json.dump(json_data, f)
        else:
            with open(os.path.join(cache_path), "wb") as f:
                f.write(r.content)

    return Response(content=r.content, media_type=content_type, headers=cached_headers)


def _shell(command: str, check: bool=True) -> str:
    logger.info(f"Run: {command}")
    process = subprocess.run(command, shell=True, check=check, stdout=subprocess.PIPE, universal_newlines=True)
    logger.info(f"Out: {process.stdout}")
    return process.stdout

def _shell_background(command: str) -> None:
    process = subprocess.Popen(command, shell=True)
    atexit.register(process.kill)
    return None

def _run_uvicorn(port: int) -> None:
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

def run_generate(args):
    _PORT = args.port
    remote_url_quoted = "{" + args.remote_url + "}"

    server_thread = threading.Thread(target=_run_uvicorn, args=(_PORT,))
    server_thread.start()

    # uvicorn.run(app, host="0.0.0.0", port=_PORT, log_level="info")
    #_shell_background(f"fastapi dev generate.py --port {_PORT} --no-reload")
    time.sleep(3)

    _shell("conan remote remove bincrafters-remote-tmp", check=False)
    _shell(f'conan remote add bincrafters-remote-tmp "http://127.0.0.1:{_PORT}/r/conan+{remote_url_quoted}+{args.remote_name}/"')
    _shell("conan remote list")

    # Get all recipes and recipes revisions
    references = _shell("conan search '*' -r bincrafters-remote-tmp --raw --case-sensitive")
    references = references.split("\n")
    revisions = {}
    for reference in references:
        if reference == "":
            continue
        revisions_search = _shell(f"conan search {reference} -r bincrafters-remote-tmp --raw --case-sensitive --revisions")
        reference_revisions = []
        for revision in revisions_search.split("\n"):
            revision_id = revision.split(" ")[0]
            if revision_id == "":
                continue
            # _revision_date = revision.split(" ")[1:]
            reference_revisions.append(revision_id)
        revisions[reference] = reference_revisions
    logger.info(f"Revisions: {revisions}")

    # TODO: How to get package revisions given a specific package ID?
    packages = {}

    # Download recipes
    for d_reference, d_revisions in revisions.items():
        for d_revision in d_revisions:
            _shell(f"conan download {d_reference}#{d_revision} -r bincrafters-remote-tmp --recipe")


    # TODO: Download all packages

    
