# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import asyncio
import os
from argparse import ArgumentParser

from aiohttp import web

from composabl_core.utils.logger import get_logger

logger = get_logger(__name__)


async def start(host, port, path_to_file):
    # Count how many times a file was downloaded
    count_downloads = 0

    # First check if the file exists
    file_content = None

    try:
        with open(path_to_file, "rb") as file:
            file_content = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"File '{path_to_file}' does not exist, pass an absolute path"
        )

    # Get the filename
    filename = path_to_file.split("/")[-1]

    async def handle(request):
        nonlocal count_downloads
        count_downloads += 1

        return web.Response(
            body=file_content,
            content_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Length": str(len(file_content)),
            },
        )

    async def handle_get_download_count(request):
        return web.Response(text=str(count_downloads))

    _app = web.Application()
    _app.add_routes(
        [
            web.get("/", handle),
            web.get("/" + filename, handle),
            web.get("/download_count", handle_get_download_count),
        ]
    )

    _server = web.AppRunner(_app)
    await _server.setup()
    _site = web.TCPSite(_server, host, port)
    await _site.start()

    # Give everything some time to start up
    await asyncio.sleep(0.1)

    logger.info(f"Server started at http://{host}:{port}")
    logger.info(
        f"you can now download the file at http://localhost:{port} or http://localhost:{port}/{filename}"
    )

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    # Create the parser
    parser = ArgumentParser(
        description="Start a file server that services the file at a given path"
    )

    # Add arguments for host, port, and protocol
    parser.add_argument(
        "--host",
        type=str,
        required=False,
        default=os.environ.get("HOST") or "[::]",
        help="Host for the server",
    )
    parser.add_argument(
        "--port",
        type=int,
        required=False,
        default=os.environ.get("PORT") or 1337,
        help="Port for the server",
    )
    parser.add_argument(
        "--path_to_file", default="myfile.txt", help="Path to the file to serve"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Run the start function with the parsed arguments
    asyncio.run(start(args.host, args.port, args.path_to_file))
