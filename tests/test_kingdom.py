import tempfile
import unittest
from pathlib import Path

from kingdom.analyzer import analyze_repository
from kingdom.generator import generate_artifacts


class KingdomTests(unittest.TestCase):
    def test_analyzer_detects_go_application(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            (tmp_path / "go.mod").write_text("module example.com/orders\n\ngo 1.23\nrequire github.com/gin-gonic/gin v1.10.0\n")
            (tmp_path / "main.go").write_text('package main\nimport ("net/http"; "os"; "github.com/gin-gonic/gin")\nfunc main() { r := gin.Default(); r.GET("/health", func(c *gin.Context) {}); http.ListenAndServe(":9090", r); _ = os.Getenv("JWT_SECRET") }\n')
            result = analyze_repository(tmp_path)
            self.assertEqual(result["framework"], "Gin")
            self.assertEqual(result["port"], 9090)
            self.assertEqual(result["healthEndpoint"], "/health")
            self.assertEqual(result["environmentVariables"], ["JWT_SECRET"])


    def test_generator_writes_expected_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            analysis = {"project": "demo", "goVersion": "1.23", "port": 8080, "environmentVariables": [], "language": "Go", "framework": "net/http"}
            generate_artifacts(analysis, tmp_path / "generated")
            self.assertTrue((tmp_path / "generated" / "Dockerfile").exists())
            self.assertTrue((tmp_path / "generated" / "kubernetes" / "deployment.yaml").exists())
            compose = (tmp_path / "generated" / "docker-compose.yml").read_text()
            self.assertIn("8080", compose)
            self.assertIn("dockerfile: generated/Dockerfile", compose)

    def test_generated_infrastructure_has_valid_template_shapes(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "generated"
            analysis = {"project": "demo", "goVersion": "1.23", "port": 8080, "environmentVariables": ["PORT", "DB_HOST"], "language": "Go", "framework": "net/http"}
            generate_artifacts(analysis, output)
            compose = (output / "docker-compose.yml").read_text()
            secret = (output / "kubernetes" / "secret.yaml").read_text()
            terraform = (output / "terraform" / "main.tf").read_text()
            self.assertNotIn(r"\n", compose)
            self.assertNotIn(r"\n", secret)
            self.assertIn("  build {\n    context = \"..\"", terraform)
            self.assertIn("  ports {\n    internal = 8080", terraform)

    def test_analyzer_detects_node_project(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text('{"name":"web-api","dependencies":{"express":"^5.0.0"}}')
            (root / "server.js").write_text("const express = require('express'); const app = express(); app.get('/health', () => {}); app.listen(process.env.PORT || 3000);")
            result = analyze_repository(root)
            self.assertEqual(result["language"], "Node.js")
            self.assertEqual(result["framework"], "Express")
            self.assertEqual(result["port"], 3000)
            self.assertEqual(result["healthEndpoint"], "/health")

    def test_generator_uses_python_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "generated"
            analysis = {"project": "py-api", "language": "Python", "version": "3.12", "port": 8000, "environmentVariables": []}
            generate_artifacts(analysis, output)
            dockerfile = (output / "Dockerfile").read_text()
            self.assertIn("FROM python:3.12-slim", dockerfile)
            self.assertIn("EXPOSE 8000", dockerfile)
