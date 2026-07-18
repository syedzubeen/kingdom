# Kingdom

Kingdom is a DevOps bootstrap agent for Go applications. It inspects a repository, produces deployment assets, and validates the artifacts that are supported by tools installed on the local machine.

## Quick start

```powershell
python -m kingdom.cli path\to\go-app --output generated
```

Or after installation:

```powershell
pip install -e .
kingdom path\to\go-app
```

The output directory contains `analysis.json`, Docker and CI assets, Kubernetes manifests, Terraform, `DEPLOYMENT.md`, and `validation-report.md`.

Kingdom's first phase is deliberately deterministic. An AI provider can be added behind the generation layer later; the generated templates are conservative and derived from the analysis rather than guesses.

## Development

```powershell
python -m pytest
```

## Web UI

Start the zero-dependency local UI:

```powershell
python -m kingdom.web
```

Open `http://127.0.0.1:5173`. The current UI is a frontend prototype: the repository field, artifact navigation, copy action, and generation state are wired for the experience; connecting the form to the CLI/API is the next integration step.
