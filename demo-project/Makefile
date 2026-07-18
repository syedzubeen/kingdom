APP_NAME=kingdom-demo
GOFLAGS=-buildvcs=false

.PHONY: run test build fmt

run:
	go run $(GOFLAGS) ./cmd/api

test:
	go test ./...

build:
	go build $(GOFLAGS) -o bin/$(APP_NAME) ./cmd/api

fmt:
	gofmt -w ./cmd ./internal
