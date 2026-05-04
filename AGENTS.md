# Agent Guidelines for wArgos (wargos)

This document outlines expectations for AI agents and contributors working on **wargos**: a FastAPI service that scrapes **WLED** devices, exposes **Prometheus** metrics, and supports **config and preset backups**. It is inspired by similar agent guidelines (for example [brronson’s agents.md](https://github.com/jzucker2/brronson/blob/master/agents.md)) and adapted to this repository’s layout and tooling.

## Pre-commit hooks

Changes should pass the hooks configured in `.pre-commit-config.yaml` before they are merged or considered complete.

### Hooks in this project

1. **trailing-whitespace** — strip trailing whitespace
2. **end-of-file-fixer** — ensure newline at end of file
3. **check-yaml** — validate YAML syntax
4. **check-added-large-files** — block very large additions
5. **black** — format Python with line length **79**
6. **flake8** — lint Python under `app/` and `tests/`

### Running hooks

```bash
# First-time setup
make pre-commit-install
# Or: pre-commit install

# All files (recommended before a final commit)
make pre-commit-run
# Or: pre-commit run --all-files

# Staged files only (what runs on `git commit` after install)
pre-commit run
```

**Agents should:** install hooks once per clone if they commit locally, run `make pre-commit-run` (or equivalent) before finishing work, and fix reported issues rather than skipping hooks unless the user explicitly asks to bypass them.

## Linting and formatting

### Style

- **PEP 8** orientation; **Black** is the source of truth for layout (79 columns).
- **Indentation:** 4 spaces.
- **Imports:** standard library, then third party, then local (`app` package).
- **flake8** settings live in `.flake8` (including project-specific `ignore` and `per-file-ignores`). Do not fight the repo config without a good reason and a matching config change.

### Commands

```bash
# Format Python
make format

# Lint (check only)
make lint

# Format then lint (convenient gate before commit)
make check

# Try automatic fixes where applicable
make lint-fix
```

If `make lint` fails after `make format`, use `make lint-fix` for autopep8-assisted fixes, then re-run `make check` until clean.

## Tests

- **Runner:** `pytest` (see `pytest.ini` and `tests/`).
- **Default:** `make test` runs `pytest tests/ -v`.
- **Coverage:** `make test-coverage`.
- **Single file:** `make test-file FILE=tests/test_basic.py`.

**Agents should:** add or update tests for new behavior, edge cases, and regressions; run `make test` before considering work done; not leave the suite failing.

Background scraping can be disabled in tests via `ENABLE_BACKGROUND_TASKS` — follow existing tests (for example lifespan and scraper tests) when adding scenarios.

## CI alignment

GitHub Actions run lint and tests (see `.github/workflows/`). Local `make check`, `make test`, and `make pre-commit-run` (or `make ci-check`) approximate what CI enforces.

## Project structure (high level)

```
wargos/
├── app/                 # Application code (FastAPI, scraper, WLED client, metrics, locks)
├── tests/               # Pytest suite
├── prometheus/          # Example alerting rules
├── grafana/             # Example dashboard JSON
├── scripts/             # Gunicorn and helper shell scripts
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── requirements-dev.txt
├── README.md            # User-facing runbook and feature overview
└── CONFIG_BACKUP.md     # Config/preset backup feature detail
```

Keep new modules cohesive: prefer small, focused modules over very large single files.

## Domain-specific expectations

### WLED and networking

- Respect existing patterns for device lists, timeouts, and error handling in `WLEDClient` and `Scraper`.
- Avoid hardcoding IPs or hostnames in code; use configuration and environment variables as elsewhere in the app.

### Prometheus and metrics

- When adding or changing metrics, update callers consistently and extend tests under `tests/test_metrics*` / related files where appropriate.
- If alerting or dashboard examples should reflect new metrics, update `prometheus/` and `grafana/` when it helps operators.

### Config and preset backups

- Backup behavior and HTTP surface are documented in **CONFIG_BACKUP.md** and the main **README.md**. User-visible API or path semantics changes should be reflected there (and in README env / compose examples when relevant).

### FastAPI

- Use `HTTPException` (or existing error patterns) for API errors; keep messages actionable.
- Validate inputs at boundaries; prefer clear 4xx responses over silent failure for bad client input.

## Documentation

- **README.md:** update when adding user-visible features, endpoints, env vars, or deployment steps.
- **CONFIG_BACKUP.md:** update when backup download/upload behavior, routes, or storage layout changes.
- Prefer short, accurate sections over duplicating the same content in multiple places.

## Security and robustness

- Treat file paths and backup directories carefully; follow existing resolution and layout conventions.
- Do not add operations that blindly follow unvalidated user paths.

## Agent workflow (concise)

1. Read nearby code and tests; match existing style and abstractions.
2. Implement the smallest change that satisfies the request.
3. Run `make check` and fix any lint issues (`make lint-fix` if needed).
4. Run `make test`.
5. Run `make pre-commit-run` (or ensure `pre-commit run --all-files` passes).
6. Update **README.md** / **CONFIG_BACKUP.md** when behavior visible to users or operators changes.

## Checklist before submitting changes

- [ ] `make check` passes (format + lint)
- [ ] `make test` passes
- [ ] `make pre-commit-run` passes (or equivalent)
- [ ] New or changed behavior has tests where practical
- [ ] README / CONFIG_BACKUP updated if user-facing backup or API docs changed
- [ ] No unnecessary drive-by refactors outside the requested scope

## References

- [Black](https://black.readthedocs.io/)
- [Flake8](https://flake8.pycqa.org/)
- [Pre-commit](https://pre-commit.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [WLED library on PyPI](https://pypi.org/project/wled/) (see README for how this project uses it)
