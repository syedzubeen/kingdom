from __future__ import annotations

import json
import re
from pathlib import Path

FRAMEWORKS = {"gin-gonic/gin": "Gin", "labstack/echo": "Echo", "gofiber/fiber": "Fiber", "express": "Express", "fastify": "Fastify", "flask": "Flask", "fastapi": "FastAPI", "django": "Django"}
DATABASES = {"lib/pq": "PostgreSQL", "jackc/pgx": "PostgreSQL", "go-sql-driver/mysql": "MySQL", "pg": "PostgreSQL", "psycopg": "PostgreSQL", "redis": "Redis", "mongoose": "MongoDB"}


def _files(root: Path) -> list[Path]:
    ignored = {".git", "vendor", "node_modules", ".venv", "venv", "generated"}
    return [p for p in root.rglob("*") if p.is_file() and not ignored.intersection(p.parts)]


def analyze_repository(repository: str | Path) -> dict:
    root = Path(repository).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Repository directory does not exist: {root}")
    files = _files(root)
    source_files = [p for p in files if p.suffix in {".go", ".js", ".ts", ".py", ".java", ".rb", ".rs"}]
    source = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in source_files)
    package_json = root / "package.json"
    package_text = package_json.read_text(encoding="utf-8", errors="ignore") if package_json.exists() else ""
    requirements = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in files if p.name in {"requirements.txt", "pyproject.toml", "Pipfile"})
    go_mod = root / "go.mod"
    go_text = go_mod.read_text(encoding="utf-8", errors="ignore") if go_mod.exists() else ""
    language = "Go" if go_mod.exists() or any(p.suffix == ".go" for p in files) else "Node.js" if package_json.exists() or any(p.suffix in {".js", ".ts"} for p in files) else "Python" if any(p.suffix == ".py" for p in files) or requirements else next((name for suffix, name in {".java": "Java", ".rs": "Rust", ".rb": "Ruby"}.items() if any(p.suffix == suffix for p in files)), None)
    framework = next((name for marker, name in FRAMEWORKS.items() if marker in source or marker in package_text or marker.lower() in requirements.lower()), "net/http" if "net/http" in source else None)
    version_match = re.search(r"^go\s+([\w.]+)", go_text, re.M)
    version = version_match.group(1) if version_match else None
    if language == "Node.js":
        version = re.search(r"(?:node|engines)[^\n]*[>=~^]*([0-9]+(?:\.[0-9]+)?)", package_text, re.I)
        version = version.group(1) if version else None
    port_values = re.findall(r"(?:PORT|port)[^\n]{0,40}?[:=]\s*[\"']?(\d{2,5})", source, re.I)
    port_values += re.findall(r"(?:ListenAndServe|listen|run|Run)\s*\([^\n]{0,20}?[\"'](?::)?(\d{2,5})", source)
    ports = sorted({int(p) for p in port_values if 1 <= int(p) <= 65535}) or [3000 if language == "Node.js" else 8000 if language == "Python" else 8080]
    routes = sorted(set(re.findall(r"(?:GET|POST|PUT|PATCH|DELETE|get|post|put|patch|delete)\s*\(\s*[\"']([^\"']+)", source) + re.findall(r"(?:HandleFunc|route|Route|path)\s*\(\s*[\"']([^\"']+)", source)))
    health = next((r.split()[-1] for r in routes if "health" in r.lower()), None)
    env_vars = set(re.findall(r"(?:os\.Getenv|LookupEnv|environ\.get|process\.env)\s*\(?\s*[\"']([A-Z][A-Z0-9_]+)", source))
    env_example = root / ".env.example"
    if env_example.exists():
        env_vars.update(re.findall(r"^([A-Z][A-Z0-9_]*)=", env_example.read_text(encoding="utf-8", errors="ignore"), re.M))
    entrypoints = sorted(str(p.relative_to(root)) for p in files if p.name in {"main.go", "main.py", "index.js", "index.ts", "server.js", "app.py"})
    databases = sorted({name for marker, name in DATABASES.items() if marker in source or marker in package_text or marker.lower() in requirements.lower()})
    tests = any(p.name.endswith("_test.go") or p.name.startswith("test_") or p.name.endswith(".test.js") for p in files)
    build_command = {"Go": "go build ./...", "Node.js": "npm run build --if-present", "Python": "python -m compileall ."}.get(language)
    return {"project": root.name, "module": re.search(r"^module\s+(.+)$", go_text, re.M).group(1).strip() if re.search(r"^module\s+(.+)$", go_text, re.M) else None, "language": language, "version": version, "goVersion": version if language == "Go" else None, "framework": framework, "entryPoints": entrypoints, "ports": ports, "port": ports[0], "routes": routes, "healthEndpoint": health, "databases": databases, "database": databases[0] if databases else None, "environmentVariables": sorted(env_vars), "dockerfileExists": (root / "Dockerfile").exists(), "makefileExists": (root / "Makefile").exists(), "testsPresent": tests, "buildCommand": build_command}


def write_analysis(analysis: dict, destination: Path) -> None:
    destination.write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
