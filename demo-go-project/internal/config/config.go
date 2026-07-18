package config

import (
	"log/slog"
	"os"
)

type Settings struct {
	Port        string
	Environment string
	LogLevel    slog.Level
	DBHost      string
	DBPort      string
	DBName      string
	DBUser      string
	DBPassword  string
	RedisURL    string
}

func Load() Settings {
	return Settings{
		Port:        value("PORT", "8080"),
		Environment: value("APP_ENV", "development"),
		LogLevel:    parseLevel(value("LOG_LEVEL", "info")),
		DBHost:      value("DB_HOST", "localhost"),
		DBPort:      value("DB_PORT", "5432"),
		DBName:      value("DB_NAME", "kingdom"),
		DBUser:      value("DB_USER", "kingdom"),
		DBPassword:  value("DB_PASSWORD", "change-me"),
		RedisURL:    value("REDIS_URL", "redis://localhost:6379"),
	}
}

func value(key, fallback string) string {
	if configured := os.Getenv(key); configured != "" {
		return configured
	}
	return fallback
}

func parseLevel(value string) slog.Level {
	var level slog.Level
	if err := level.UnmarshalText([]byte(value)); err != nil {
		return slog.LevelInfo
	}
	return level
}
