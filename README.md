# Kingdom

Kingdom is a DevOps bootstrap agent for Go applications. It inspects a repository, produces deployment assets, and validates the artifacts that are supported by tools installed on the local machine.

![Kingdom demo](web/king-gif.gif)

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

## Setup

Kingdom requires Python 3.10 or newer. The analyzed application should currently be a Go repository. Docker, Terraform, and kubectl are optional; Kingdom runs the checks available on the local machine and reports unavailable tools as skipped.

```powershell
git clone https://github.com/syedzubeen/kingdom.git
cd kingdom
python -m pip install -e .
```

Run the CLI against a local Go project:

```powershell
kingdom .\path\to\go-project --output .\generated
```

Run the local web interface:

```powershell
python -m kingdom.web
```

Then open `http://127.0.0.1:5173`.

## How Codex and GPT-5.6 were used

Codex, powered by GPT-5.6, was used as the engineering agent throughout the project. It helped design the repository-analysis workflow, scaffold the Python CLI and web UI, create the standalone Go demo project, generate deployment templates, and iterate on the implementation based on real validation results.

GPT-5.6 was used for reasoning and synthesis tasks rather than for basic repository facts. Kingdom deliberately discovers facts such as Go versions, ports, routes, environment variables, and entry points programmatically. AI assistance is intended for interpreting those signals, explaining infrastructure decisions, selecting deployment strategies, and regenerating artifacts when validation errors are found.

Codex also helped test the project end to end, identify malformed Compose, Kubernetes, and Terraform output, improve the templates, build the Vercel deployment adapters, and refine the user-facing documentation. This reflects the core design principle of Kingdom: combine deterministic tooling with AI reasoning, then verify the result with local validators.

## Deploy the UI to Vercel

Kingdom includes a static UI in `web/` and a root `vercel.json` configured with the `Other` framework preset, no build command, and `web` as the output directory.

```powershell
npm install --global vercel
vercel login
vercel --prod
```

The UI is deployable as a static site. The local Python CLI and API generation workflow still run locally; connecting the deployed UI to a hosted Kingdom backend is a separate integration step.

## Development

```powershell
python -m unittest discover -s tests -v
python -m compileall kingdom
```

## Web UI

Start the zero-dependency local UI:

```powershell
python -m kingdom.web
```

Open `http://127.0.0.1:5173`. The current UI is a frontend prototype: the repository field, artifact navigation, copy action, and generation state are wired for the experience; connecting the form to the CLI/API is the next integration step.
