# PyChronicle

PyChronicle is an AST-powered time-travel debugger for Python.

It traces a Python script execution, captures every variable change as a
timestamped SQLite event, and lets you replay the execution timeline —
seeing the source line and variable state at each recorded moment.

## Pipeline

```
Script → AST analysis → sys.settrace → SQLite storage → Timeline viewer
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

## Run the Timeline Viewer (UI Data Integration)

Run the full pipeline and replay every recorded event with code viewer
and variable panel output:

```bash
python ui/app.py examples/sample_script.py
```

Each step shows:

- **Code Viewer** — all source lines with `>>>` marking the active line
- **Variable Panel** — accumulated variable state at that moment in time

## Run Tests

```bash
python -m pytest
```

All tests should pass:

```
57 passed
```

Run verbosely:

```bash
python -m pytest -v
```

Run specific suites:

```bash
python -m pytest tests/test_ast.py -v        # AST parser unit tests
python -m pytest tests/test_pipeline.py -v   # Integration + UI tests
```

## Mid Review Demo Procedure

The following steps reproduce the full working demo:

**Step 1 — Run the pipeline on the sample script:**

```bash
python -m pipeline.runner examples/sample_script.py
```

Verify: `Success : True`, `Event count` > 0.

**Step 2 — View the timeline with code viewer and variable panel:**

```bash
python ui/app.py examples/sample_script.py
```

Verify: Events are printed with numbered source lines, `>>>` highlighted line,
and variable panel showing accumulated state.

**Step 3 — Run the full test suite:**

```bash
python -m pytest
```

Verify: All 57 tests pass.

## Project Structure

```
ast_parser.py          # AST analysis — detect variable assignments
tracer.py              # sys.settrace tracer — capture runtime variable changes
storage.py             # SQLite schema reference (events table)
executor.py            # Python script execution engine
pipeline/
  runner.py            # Integration glue: AST → trace → SQLite (run_pipeline)
ui/
  app.py               # Timeline ↔ data integration: ChronicleDataAdapter,
                       #   timeline_select(), run_viewer()
examples/
  sample_script.py     # Deterministic demo script for integration tests
tests/
  conftest.py          # Shared pytest fixtures
  test_ast.py          # AST parser unit tests (15 tests)
  test_pipeline.py     # End-to-end pipeline + UI integration tests (42 tests)
NOTES.md               # Week 1 compatibility notes (AST ↔ storage field mapping)
requirements.txt       # Python dependencies
pytest.ini             # pytest configuration
```

## Tech Stack

- Python 3.10+
- `ast` — static variable detection
- `sys.settrace` — runtime line tracing
- `sqlite3` — event persistence
- `pytest` — test suite