from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def validate(output: str | Path, repository: str | Path | None = None) -> list[dict]:
    out = Path(output)
    checks = []
    if repository:
        repo = str(Path(repository).resolve())
        checks.extend([("Go tests", ["go", "test", "./..."], repo),
                       ("Go build", ["go", "build", "-buildvcs=false", "./..."], repo),
                       ("Docker build", ["docker", "build", "-f", str(out / "Dockerfile"), "-t", "kingdom-validation", repo], None)])
    checks.extend([("Docker Compose config", ["docker", "compose", "-f", str(out / "docker-compose.yml"), "config"], None),
                   ("Terraform format", ["terraform", "-chdir=" + str(out / "terraform"), "fmt", "-check"], None),
                   ("Kubernetes manifest parse", ["kubectl", "apply", "--dry-run=client", "--validate=false", "-f", str(out / "kubernetes")], None)])
    results = []
    for name, command, working_directory in checks:
        tool = command[0].split("-")[0]
        if not shutil.which(tool):
            results.append({"name": name, "status": "skipped", "detail": f"{tool} is not installed"})
            continue
        try:
            completed = subprocess.run(command, cwd=working_directory, capture_output=True, text=True, timeout=120)
            detail = (completed.stdout or completed.stderr).strip()
            status = "passed" if completed.returncode == 0 else "failed"
            if name == "Kubernetes manifest parse" and any(marker in detail.lower() for marker in ("connection refused", "couldn't get current server", "unable to connect to the server")):
                status = "skipped"
                detail = "No Kubernetes API server is available for client-side validation"
            results.append({"name": name, "status": status, "detail": detail})
        except (OSError, subprocess.TimeoutExpired) as exc:
            results.append({"name": name, "status": "failed", "detail": str(exc)})
    return results


def write_report(output: str | Path, analysis: dict, results: list[dict]) -> None:
    lines = ["# Kingdom validation report", "", "## Repository analysis", "", f"- Language: {analysis.get('language')}", f"- Framework: {analysis.get('framework') or 'not detected'}", f"- Port: {analysis['port']}", "", "## Validation", ""]
    lines.extend(f"- {'✓' if r['status'] == 'passed' else '–' if r['status'] == 'skipped' else '✗'} {r['name']}: {r['status']} ({r['detail'] or 'no output'})" for r in results)
    Path(output, "validation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
