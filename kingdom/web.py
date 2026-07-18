"""Small zero-dependency server for the Kingdom prototype UI."""

from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the Kingdom web UI")
    parser.add_argument("--port", type=int, default=5173)
    args = parser.parse_args()
    web_root = Path(__file__).resolve().parent.parent / "web"
    handler = lambda *items: SimpleHTTPRequestHandler(*items, directory=str(web_root))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Kingdom UI running at http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nKingdom UI stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
