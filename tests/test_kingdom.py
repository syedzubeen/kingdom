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
