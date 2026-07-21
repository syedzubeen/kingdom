from __future__ import annotations

import argparse
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlparse

from .analyzer import analyze_repository
from .generator import generate_artifacts
from .validator import validate, write_report


@contextmanager
def repository_path(value: str):
    if value.startswith(("https://", "http://", "git@")):
        with tempfile.TemporaryDirectory(prefix="kingdom-repo-") as directory:
            result = subprocess.run(["git", "clone", "--depth", "1", value, directory], capture_output=True, text=True, timeout=180)
            if result.returncode != 0:
                raise ValueError(f"Could not clone repository: {result.stderr.strip()}")
            yield Path(directory)
    else:
        yield Path(value).expanduser().resolve()


def main() -> int:
    parser = argparse.ArgumentParser(prog="kingdom", description="Bootstrap DevOps assets for a repository")
    parser.add_argument("repository", help="local repository path or GitHub/Git URL")
    parser.add_argument("--output", default="generated", help="artifact output directory")
    parser.add_argument("--no-validate", action="store_true", help="skip local validation commands")
    args = parser.parse_args()
    try:
        with repository_path(args.repository) as repository:
            analysis = analyze_repository(repository)
            if args.repository.startswith(("https://", "http://", "git@")):
                analysis["project"] = Path(urlparse(args.repository).path).stem or "repository"
            files = generate_artifacts(analysis, args.output)
            results = [] if args.no_validate else validate(args.output, repository)
            write_report(args.output, analysis, results)
    except (ValueError, subprocess.TimeoutExpired) as exc:
        parser.error(str(exc))
    print(f"Kingdom generated {len(files)} artifacts in {Path(args.output).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
