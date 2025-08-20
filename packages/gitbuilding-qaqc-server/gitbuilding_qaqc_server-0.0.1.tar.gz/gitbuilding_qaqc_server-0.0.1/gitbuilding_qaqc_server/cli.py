"""The command line interface for GitBuilding QA/QC Server.

This is run when you run gitbuilding-qaqc-server.
"""
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse

import uvicorn

from gitbuilding_qaqc_server.app import create_app


def main() -> None:
    """Parse CLI args, and start server."""
    parser = argparse.ArgumentParser(description="Start GitBuilding QA/QC server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to run the server on")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on"
    )
    parser.add_argument(
        "--db-dir", default=None, help="Directory to store SQLite databases"
    )

    args = parser.parse_args()

    app = create_app(args.db_dir)

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
