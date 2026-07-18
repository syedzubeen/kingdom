package httpapi

import (
	"log/slog"
	"net/http"
	"net/http/httptest"
	"testing"

	"example.com/kingdom-demo/internal/config"
)

func TestHealthEndpoint(t *testing.T) {
	handler := NewRouter(slog.Default(), config.Settings{Environment: "test"})
	recording := httptest.NewRecorder()
	request := httptest.NewRequest(http.MethodGet, "/health", nil)

	handler.ServeHTTP(recording, request)

	if recording.Code != http.StatusOK {
		t.Fatalf("expected 200, got %d", recording.Code)
	}
	if contentType := recording.Header().Get("Content-Type"); contentType != "application/json" {
		t.Fatalf("expected JSON content type, got %q", contentType)
	}
}

func TestProjectNotFound(t *testing.T) {
	handler := NewRouter(slog.Default(), config.Settings{})
	recording := httptest.NewRecorder()
	request := httptest.NewRequest(http.MethodGet, "/api/v1/projects/missing", nil)

	handler.ServeHTTP(recording, request)

	if recording.Code != http.StatusNotFound {
		t.Fatalf("expected 404, got %d", recording.Code)
	}
}
