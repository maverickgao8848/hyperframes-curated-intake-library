#!/usr/bin/env python3
from __future__ import annotations

import argparse
import webbrowser
from pathlib import Path

from workbench_server import create_server


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve the local Visual Director review workbench.")
    parser.add_argument("project", type=Path)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()
    server = create_server(args.project, args.catalog, args.host, args.port)
    host, port = server.server_address[:2]
    url = f"http://{host}:{port}/"
    print(url, flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
