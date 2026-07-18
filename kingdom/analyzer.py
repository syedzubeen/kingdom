from __future__ import annotations

import json
import re
from pathlib import Path


FRAMEWORKS = {
    "gin-gonic/gin": "Gin",
    "labstack/echo": "Echo",
    "gofiber/fiber": "Fiber",
}
DATABASES = {"lib/pq": "PostgreSQL", "jackc/pgx": "PostgreSQL", "go-sql-driver/mysql": "MySQL", "mongo-driver": "MongoDB", "go-redis": "Redis"}


def _files(root: Path) -> list[Path]:
    ignored = {".git", "vendor", "node_modules"}
    return [p for p in root.rglob("*") if p.is_file() and not ignored.intersection(p.parts)]


def analyze_repository(repository: str | Path) -> dict:
    root = Path(repository).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Repository directory does not exist: {root}")
    go_files = [p for p in _files(root) if p.suffix == ".go"]
    source = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in go_files)
    go_mod = root / "go.mod"
    module = None
    go_version = None
    if go_mod.exists():
        mod_text = go_mod.read_text(encoding="utf-8", errors="ignore")
        module_match = re.search(r"^module\s+(.+)$", mod_text, re.M)
        version_match = re.search(r"^go\s+([\w.]+)", mod_text, re.M)
        module = module_match.group(1).strip() if module_match else None
        go_version = version_match.group(1).strip() if version_match else None
    framework = next((name for import_path, name in FRAMEWORKS.items() if import_path in source), "net/http" if "net/http" in source else None)
    databases = sorted({name for import_path, name in DATABASES.items() if import_path in source})
    port_values = re.findall(r"(?:PORT|port)[^\n]{0,30}?[:=]\s*[\"']?(\d{2,5})", source, re.I)
    port_values += re.findall(r"(?:ListenAndServe|Run)\s*\(\s*[\"']:[\"']?(\d{2,5})", source)
    ports = sorted({int(p) for p in port_values if 1 <= int(p) <= 65535})
    if not ports:
        ports = [8080]
    routes = set(re.findall(r"(?:GET|POST|PUT|PATCH|DELETE)\s*\(\s*[\"']([^\"']+)", source))
    routes.update(re.findall(r"(?:HandleFunc|Handle)\s*\(\s*[\"']([^\"']+)", source))
    routes = sorted(routes)
    health = next((r.split()[-1] for r in routes if "health" in r.lower()), None)
    env_vars = set(re.findall(r"(?:os\.Getenv|LookupEnv)\(\s*[\"']([A-Z][A-Z0-9_]+)", source))
    env_example = root / ".env.example"
    if env_example.exists():
        env_vars.update(re.findall(r"^([A-Z][A-Z0-9_]*)=", env_example.read_text(encoding="utf-8", errors="ignore"), re.M))
    env_vars = sorted(env_vars)
    entrypoints = sorted(str(p.relative_to(root)) for p in go_files if p.name == "main.go")
    return {
        "project": root.name,
        "module": module,
        "language": "Go" if go_files or go_mod.exists() else None,
        "goVersion": go_version,
        "framework": framework,
        "entryPoints": entrypoints,
        "ports": ports,
        "port": ports[0],
        "routes": routes,
        "healthEndpoint": health,
        "databases": databases,
        "database": databases[0] if databases else None,
        "environmentVariables": env_vars,
        "dockerfileExists": (root / "Dockerfile").exists(),
        "makefileExists": (root / "Makefile").exists(),
        "testsPresent": any(p.name.endswith("_test.go") for p in go_files),
        "buildCommand": "go build ./..." if go_files else None,
    }


def write_analysis(analysis: dict, destination: Path) -> None:
    destination.write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
