# Kingdom validation report

## Repository analysis

- Language: Go
- Framework: net/http
- Port: 8080

## Validation

- ✓ Go tests: passed (?   	example.com/kingdom-demo/cmd/api	[no test files]
?   	example.com/kingdom-demo/internal/config	[no test files]
ok  	example.com/kingdom-demo/internal/httpapi	(cached))
- ✓ Go build: passed (no output)
- ✗ Docker build: failed (WARNING: Error loading config file: open C:\Users\zubeen\.docker\config.json: Access is denied.
WARNING: Error loading config file: open C:\Users\zubeen\.docker\config.json: Access is denied.
ERROR: CreateFile C:\Users\zubeen\.docker\buildx\instances: Access is denied.)
- ✓ Docker Compose config: passed (name: generated
services:
  demo-project:
    build:
      context: C:\Users\zubeen\Documents\hackathon\demo-project
      dockerfile: generated/Dockerfile
    environment:
      APP_ENV: ""
      DB_HOST: ""
      DB_NAME: ""
      DB_PASSWORD: ""
      DB_PORT: ""
      DB_USER: ""
      LOG_LEVEL: ""
      PORT: ""
      REDIS_URL: ""
    networks:
      default: null
    ports:
      - mode: ingress
        target: 8080
        published: "8080"
        protocol: tcp
networks:
  default:
    name: generated_default)
- ✓ Terraform format: passed (There are some problems with the CLI configuration:
â•·
â”‚ Error: Error reading C:\Users\zubeen\AppData\Roaming\terraform.d: open C:\Users\zubeen\AppData\Roaming\terraform.d: Access is denied.
â”‚
â•µ

As a result of the above problems, Terraform may not behave as intended.)
- – Kubernetes manifest parse: skipped (No Kubernetes API server is available for client-side validation)
