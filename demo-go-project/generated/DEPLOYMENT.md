# Deployment guide for demo-project

Kingdom detected Go 1.23, listening on port 8080.

## Local

Run `docker compose up --build`.

## Kubernetes

Replace placeholder values in `kubernetes/secret.yaml`, then run `kubectl apply -f kubernetes/`.

## Environment variables

Detected variables: APP_ENV, DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, LOG_LEVEL, PORT, REDIS_URL.

## Terraform

From `terraform/`, run `terraform init` and review the plan before applying.
