from __future__ import annotations

import json
from pathlib import Path


def generate_artifacts(analysis: dict, output: str | Path) -> list[str]:
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    port = analysis["port"]
    app = analysis["project"]
    env = analysis["environmentVariables"]
    dockerfile_reference = f"{out.name}/Dockerfile"
    compose_environment = "\n".join(f"      {key}: ${{{key}:-}}" for key in env) or f"      PORT: {port}"
    secret_entries = "\n".join(f"  {key}: replace-me" for key in env) or "  APP_SECRET: replace-me"
    files: dict[str, str] = {
        "Dockerfile": f"""FROM golang:{analysis.get('goVersion') or '1.23'} AS build
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
""",
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
        ".gitlab-ci.yml": f"""stages: [test, build]
variables:
  GO_VERSION: \"{analysis.get('goVersion') or '1.23'}\"
cache:
  paths: [go/pkg/mod]
test:
  image: golang:${{GO_VERSION}}
  stage: test
  script:
    - go test ./...
build:
  image: docker:27
  services: [docker:27-dind]
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
""",
        "Jenkinsfile": """pipeline {
  agent any
  stages {
    stage('Test') { steps { sh 'go test ./...' } }
    stage('Build') { steps { sh 'docker build -t kingdom:${BUILD_NUMBER} .' } }
  }
}
""",
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


def _deployment_doc(a: dict) -> str:
    env = ", ".join(a["environmentVariables"]) or "none detected"
    return f"""# Deployment guide for {a['project']}

Kingdom detected Go {a.get('goVersion') or 'version not declared'}, listening on port {a['port']}.

## Local

Run `docker compose up --build`.

## Kubernetes

Replace placeholder values in `kubernetes/secret.yaml`, then run `kubectl apply -f kubernetes/`.

## Environment variables

Detected variables: {env}.

## Terraform

From `terraform/`, run `terraform init` and review the plan before applying.
"""
