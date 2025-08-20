# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import argparse
import asyncio
import json
import os

from composabl_core.networking.sim.server import make_from_sim_path


async def start(args: argparse.Namespace):
    # Convert config from JSON string to dictionary
    config = json.loads(args.config)
    
    # Create the server
    server = make_from_sim_path(
        path=args.path,
        host=args.host,
        port=args.port,
        config=config,
        protocol=args.protocol,
    )

    await server.start()

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    """
    Create an entrypoint for the server
    """
    parser = argparse.ArgumentParser(description="Create a server instance.")
    parser.add_argument("--path", type=str, required=True, help="Path to the Simulator")
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
        "--config", type=str, default="{}", help="Configuration in JSON format"
    )
    parser.add_argument(
        "--protocol",
        type=str,
        choices=["grpc", "http"],
        default="grpc",
        help="Protocol to use",
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["server", "remote_skill"],
        default="grpc",
        help="Protocol to use",
    )

    args = parser.parse_args()

    asyncio.run(start(args))
