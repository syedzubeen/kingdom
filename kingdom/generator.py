from __future__ import annotations

import json
from pathlib import Path


def generate_artifacts(analysis: dict, output: str | Path) -> list[str]:
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    port = analysis["port"]
    app = analysis["project"]
    env = analysis["environmentVariables"]
    language = analysis.get("language") or "Unknown"
    dockerfile_reference = f"{out.name}/Dockerfile"
    compose_environment = "\n".join(f"      {key}: ${{{key}:-}}" for key in env) or f"      PORT: {port}"
    secret_entries = "\n".join(f"  {key}: replace-me" for key in env) or "  APP_SECRET: replace-me"
    files: dict[str, str] = {
        "Dockerfile": _dockerfile(analysis),
        "docker-compose.yml": f"""services:
  {app}:
    build:
      context: ..
      dockerfile: {dockerfile_reference}
    ports:
      - \"{port}:{port}\"
    environment:
{compose_environment}
""",
        ".gitlab-ci.yml": _gitlab_ci(analysis),
        "Jenkinsfile": _jenkinsfile(analysis),
        "kubernetes/deployment.yaml": f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {app}
spec:
  replicas: 2
  selector: {{matchLabels: {{app: {app}}}}}
  template:
    metadata: {{labels: {{app: {app}}}}}
    spec:
      containers:
        - name: {app}
          image: {app}:latest
          ports: [{{containerPort: {port}}}]
          envFrom:
            - configMapRef: {{name: {app}}}
            - secretRef: {{name: {app}}}
""",
        "kubernetes/service.yaml": f"""apiVersion: v1
kind: Service
metadata: {{name: {app}}}
spec:
  selector: {{app: {app}}}
  ports: [{{port: 80, targetPort: {port}}}]
""",
        "kubernetes/configmap.yaml": f"""apiVersion: v1
kind: ConfigMap
metadata: {{name: {app}}}
data:
  PORT: \"{port}\"
""",
        "kubernetes/secret.yaml": f"""apiVersion: v1
kind: Secret
metadata: {{name: {app}}}
type: Opaque
stringData:
{secret_entries}
""",
        "terraform/main.tf": f"""terraform {{
  required_version = \">= 1.5.0\"
  required_providers {{
    docker = {{
      source  = \"kreuzwerker/docker\"
      version = \"~> 3.0\"
    }}
  }}
}}

provider \"docker\" {{}}

resource \"docker_image\" \"app\" {{
  name = \"{app}:latest\"
  build {{
    context = \"..\"
  }}
}}

resource \"docker_container\" \"app\" {{
  name  = \"{app}\"
  image = docker_image.app.image
  ports {{
    internal = {port}
    external = {port}
  }}
}}
""",
        "DEPLOYMENT.md": _deployment_doc(analysis),
    }
    for name, content in files.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    (out / "analysis.json").write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
    return list(files) + ["analysis.json"]


def _dockerfile(a: dict) -> str:
    language = a.get("language")
    port = a["port"]
    if language == "Node.js":
        return f"""FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev || npm install --omit=dev
COPY . .
EXPOSE {port}
USER node
CMD [\"npm\", \"start\"]
"""
    if language == "Python":
        entry = a.get("entryPoints", ["app.py"])[0] if a.get("entryPoints") else "app.py"
        return f"""FROM python:3.12-slim
WORKDIR /app
COPY requirements*.txt pyproject.toml* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi
COPY . .
EXPOSE {port}
CMD [\"python\", \"{Path(entry).name}\"]
"""
    if language != "Go":
        return f"""FROM alpine:3.20
WORKDIR /app
COPY . .
EXPOSE {port}
CMD [\"sh\", \"-c\", \"echo Configure the generated image for this {language or 'unknown'} project\"]
"""
    return f"""FROM golang:{a.get('goVersion') or '1.23'} AS build
WORKDIR /src
COPY go.mod go.sum* ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -buildvcs=false -o /out/app ./...

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/app /app
EXPOSE {port}
USER nonroot:nonroot
ENTRYPOINT [\"/app\"]
"""


def _gitlab_ci(a: dict) -> str:
    language = a.get("language")
    if language == "Node.js":
        image, test, build = "node:20", "npm test --if-present", "npm run build --if-present"
    elif language == "Python":
        image, test, build = "python:3.12", "python -m pytest || python -m unittest", "python -m compileall ."
    else:
        image, test, build = f"golang:{a.get('goVersion') or '1.23'}", "go test ./...", "go build ./..."
    return f"""stages: [test, build]
test:
  image: {image}
  stage: test
  script:
    - {test}
build:
  image: {image}
  stage: build
  script:
    - {build}
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
"""


def _jenkinsfile(a: dict) -> str:
    command = "npm test --if-present" if a.get("language") == "Node.js" else "python -m pytest || python -m unittest" if a.get("language") == "Python" else "go test ./..."
    return f"""pipeline {{
  agent any
  stages {{
    stage('Test') {{ steps {{ sh '{command}' }} }}
    stage('Build') {{ steps {{ sh 'docker build -t kingdom:${{BUILD_NUMBER}} .' }} }}
  }}
}}
"""


def _deployment_doc(a: dict) -> str:
    env = ", ".join(a["environmentVariables"]) or "none detected"
    return f"""# Deployment guide for {a['project']}

Kingdom detected {a.get('language') or 'an unknown language'} {a.get('version') or ''}, listening on port {a['port']}.

## Local

Run `docker compose up --build`.

## Kubernetes

Replace placeholder values in `kubernetes/secret.yaml`, then run `kubectl apply -f kubernetes/`.

## Environment variables

Detected variables: {env}.

## Terraform

From `terraform/`, run `terraform init` and review the plan before applying.
"""
