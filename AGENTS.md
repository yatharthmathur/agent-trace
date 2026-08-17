# AgentTrace agent notes

This repo is a local flight recorder for AI agents, not a hosted platform.

Before implementing:

1. Read [docs/mvp.md](docs/mvp.md) and [docs/architecture.md](docs/architecture.md).
2. Follow the skills in `.cursor/skills/` — especially `agenttrace-mvp`, `agenttrace-tdd`, and `agenttrace-schema`.
3. Do not add services, auth, evals, or a web platform.
4. Write a failing unit test first. Run tests with `docker compose run --rm test`.
