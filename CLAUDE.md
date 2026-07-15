# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

DataStat API is a Flask app for descriptive statistics over numeric arrays (mean, median, std, variance, percentiles), histogram generation, and two-set comparison. It serves a small HTML/JS frontend and keeps a Redis-backed history of the last 10 analysis operations. Code identifiers and API JSON keys are in Portuguese.

## Commands

```bash
# Run the full stack (Flask + Redis) — app on http://localhost:5000
docker-compose up --build

# Tests (run from repo root; pytest.ini adds both `.` and `app` to pythonpath)
pytest
pytest tests/test_analyzer.py::test_calculo_estatistica   # single test
```

There is no lint config. Dependencies live in `app/requirements.txt` (note: this file is UTF-16 encoded).

## Architecture

The `app/` package is a layered pipeline. Each layer imports the next **as a top-level module**, not relative to the package root:

- `main.py` — Flask routes. Only responsibility is request parsing + validation (checks `numeros` is a non-empty list, `bins` is a positive int) and mapping exceptions to HTTP 400/500. Imports `services.data_service`.
- `services/data_service.py` — orchestration. Calls `analyzer` for computation, then always writes the operation to history via `repositories.data_repository`. This is the layer that ties computation to persistence.
- `analyzer.py` — pure NumPy computation, no side effects. All numeric outputs are `round(..., 4)` and cast to native Python `int`/`float`/`list` so they are JSON-serializable.
- `repositories/data_repository.py` — Redis history. Uses an `rpush` + `ltrim(-MAX_HISTORY, -1)` + `expire` pattern so the list self-caps at 10 entries (`MAX_HISTORY`) and expires after 180s (`HISTORY_TTL`). Entries are JSON-encoded dicts with `type`/`timestamp`/`input`/`result`.
- `models/connection/` — `RedisConnection` reads a hardcoded config dict from `connection_options.py`.

### Import path constraint (important)

Modules use flat imports (`import analyzer`, `import services.data_service as service`) that resolve **only when `app/` is the working directory / on `sys.path`**. This works in two contexts:
- In Docker, `WORKDIR /app` + `CMD ["python", "main.py"]` runs from inside `app/`.
- In pytest, `pytest.ini` puts `app` on `pythonpath` (tests themselves import via `from app.analyzer import *`).

Running `python main.py` from the repo root will fail on imports. Any new module must respect this flat-import scheme.

### Redis config is Docker-only

`connection_options.py` hardcodes `HOST: 'redis'` (the docker-compose service name). The `REDIS_HOST`/`REDIS_PORT` env vars set in `docker-compose.yml` are **not** read by the code. Running the app or history-dependent tests outside Docker requires either a reachable `redis` host or editing `connection_options.py`.

## Testing note

`tests/test_analyzer.py` asserts on dict literals (`assert { ... }`), which are always truthy — the tests exercise NumPy directly and do not actually validate the `analyzer` functions' return values. Treat existing tests as smoke/placeholder coverage when adding real assertions.
