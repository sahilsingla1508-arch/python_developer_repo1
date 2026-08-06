# PyChronicle

PyChronicle is an AST-powered time-travel debugger for Python.

It traces a Python script execution, captures every variable change as a
timestamped SQLite event, and provides a data integration layer that maps
each recorded event to the corresponding source line and variable state.

## Pipeline

```
Script → AST analysis → sys.settrace → SQLite storage → UI/data integration layer
```

## Requirements

- Python 3.10+
- pytest >= 9.0 (for running tests)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Pipeline

Analyse and trace a Python script, storing events in `chronicle.db`:

```bash
python -m pipeline.runner examples/sample_script.py
```

Use a custom database path:

```bash
python -m pipeline.runner examples/sample_script.py my_trace.db
```

**Expected output:**

```
==================================================
PyChronicle Pipeline Result
==================================================
Success     : True
Script      : .../examples/sample_script.py
DB          : chronicle.db
AST vars    : [{"line_number": 10, "variable_name": "x"}, ...]
Event count : 14
==================================================
```

## Unified CLI (Week 4)

A unified `python -m pychronicle` entry point (`pychronicle/__main__.py`)
consolidates the pipeline and viewer into a single, polished CLI.

**Run the pipeline only:**

```bash
python -m pychronicle run examples/sample_script.py
python -m pychronicle run examples/sample_script.py my_trace.db
```

**Run the pipeline and display the full timeline view:**

```bash
python -m pychronicle view examples/sample_script.py
python -m pychronicle view examples/sample_script.py my_trace.db
```

**Show help:**

```bash
python -m pychronicle --help
python -m pychronicle run --help
python -m pychronicle view --help
```

**Exit codes:**

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Usage error / missing argument |
| 2 | Pipeline failure (missing script, runtime error, etc.) |

## Run the UI/Data Integration Demo

`ui/app.py` provides the integration adapter (`ChronicleDataAdapter`,
`timeline_select()`) that bridges stored SQLite events with the code viewer
and variable panel data. It also includes a terminal demonstration that
walks through every recorded event sequentially.

> **Note:** This is a non-interactive terminal walk-through, not a live UI.
> The interactive Textual UI is Sahil's teammate deliverable and is not
> currently present on this branch.

```bash
python ui/app.py examples/sample_script.py
```

For each recorded event the output shows:

- **Code Viewer** — all source lines with `>>>` marking the event's line
- **Variable Panel** — accumulated variable state at that point in execution

## Run Tests

```bash
python -m pytest
```

All tests should pass:

```
91 passed
```

Run verbosely:

```bash
python -m pytest -v
```

Run specific suites:

```bash
python -m pytest tests/test_ast.py -v        # AST parser unit tests
python -m pytest tests/test_pipeline.py -v   # Integration + UI + CLI tests
```

## Mid Review Demo Procedure

The following steps reproduce the full working demo:

**Step 1 — Run the pipeline on the sample script:**

```bash
python -m pipeline.runner examples/sample_script.py
```

Verify: `Success : True`, `Event count` > 0.

**Step 2 — Run the UI/data integration terminal demo:**

```bash
python ui/app.py examples/sample_script.py
```

Verify: Every recorded event is printed with numbered source lines,
`>>>` marking the active line, and the accumulated variable state.
(This is a sequential terminal walk-through; interactive timeline navigation
requires the Textual UI, which is a pending teammate deliverable.)

**Step 3 — Run the full test suite:**

```bash
python -m pytest
```

Verify: All 57 tests pass.

## Project Structure

```
ast_parser.py          # AST analysis -- detect variable assignments
tracer.py              # sys.settrace tracer -- capture runtime variable changes
storage.py             # SQLite schema reference (events table)
executor.py            # Python script execution engine
pipeline/
  runner.py            # Integration glue: AST -> trace -> SQLite (run_pipeline)
  delta.py             # Delta-compression utilities (compress_events, replay_compressed)
pychronicle/
  __main__.py          # Unified CLI entry point: python -m pychronicle run/view
ui/
  app.py               # UI/data integration adapter: ChronicleDataAdapter,
                       #   timeline_select(), run_viewer() (terminal demo).
                       #   Interactive Textual UI is a pending teammate deliverable.
examples/
  sample_script.py     # Deterministic demo script for integration tests
tests/
  conftest.py          # Shared pytest fixtures
  test_ast.py          # AST parser unit tests (15 tests)
  test_pipeline.py     # End-to-end pipeline + UI + CLI integration tests (76 tests)
NOTES.md               # Week 1 compatibility notes (AST <-> storage field mapping)
requirements.txt       # Python dependencies
pytest.ini             # pytest configuration
```

## Tech Stack

- Python 3.10+
- `ast` — static variable detection
- `sys.settrace` — runtime line tracing
- `sqlite3` — event persistence
- `pytest` — test suite