# Kingdom Demo API

A small production-shaped Go service designed to be analyzed by Kingdom. It uses only the Go standard library, so it can run without fetching third-party dependencies.

## Run locally

```powershell
go run ./cmd/api
```

The server listens on `http://localhost:8080` by default.

## Try the API

```powershell
Invoke-WebRequest http://localhost:8080/health
Invoke-WebRequest http://localhost:8080/ready
Invoke-WebRequest http://localhost:8080/api/v1/projects
Invoke-WebRequest http://localhost:8080/api/v1/projects/kingdom
```

Set `PORT`, `APP_ENV`, `LOG_LEVEL`, and the documented database/cache variables to customize the service. Database and Redis settings are intentionally configuration-only in this demo; they give Kingdom realistic deployment signals without requiring external services.

## Test

```powershell
go test ./...
```

## Analyze with Kingdom

From the parent Kingdom directory:

```powershell
& "C:\Users\zubeen\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m kingdom.cli .\demo-project --output .\demo-project\generated
```
