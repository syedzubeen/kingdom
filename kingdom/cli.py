from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import analyze_repository
from .generator import generate_artifacts
from .validator import validate, write_report


def main() -> int:
    parser = argparse.ArgumentParser(prog="kingdom", description="Bootstrap DevOps assets for a Go repository")
    parser.add_argument("repository", help="path to a local repository")
    parser.add_argument("--output", default="generated", help="artifact output directory")
    parser.add_argument("--no-validate", action="store_true", help="skip local validation commands")
    args = parser.parse_args()
    try:
        analysis = analyze_repository(args.repository)
        files = generate_artifacts(analysis, args.output)
        results = [] if args.no_validate else validate(args.output, args.repository)
        write_report(args.output, analysis, results)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Kingdom generated {len(files)} artifacts in {Path(args.output).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
