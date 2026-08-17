# AgentTrace

Local flight recorder for AI agents: capture a run (models, tools, errors) and inspect it later.

This repository is in **spec-first** shape. The MVP, architecture, and interchange schema are defined; the recorder SDK is the next implementation slice.

- Product: [docs/mvp.md](docs/mvp.md)
- Architecture: [docs/architecture.md](docs/architecture.md)
- Export schema: [schemas/v1/trace.schema.json](schemas/v1/trace.schema.json)

## MVP in one paragraph

A Python SDK writes nested LLM/tool/error spans into a local SQLite file. A CLI lists runs, prints a run as a tree, and exports schema-valid JSON. No server, no accounts, no eval platform.

## Development

Docker is the supported way to run tests. You only need Docker Compose.

```bash
docker compose run --rm test
```

On a bind-mounted checkout this installs the package in editable mode and runs pytest. See `.cursor/skills/agenttrace-docker` and `.cursor/skills/agenttrace-tdd`.
