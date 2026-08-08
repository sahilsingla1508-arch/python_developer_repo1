# PyChronicle

PyChronicle is an AST-powered time-travel debugger for Python that allows users
to visualize program execution line by line. The project combines static code
analysis using Python's AST module with runtime tracing (`sys.settrace`), SQLite
event storage, and a Textual-based terminal UI to provide an interactive
debugging experience.

## Pipeline

```
Script → AST analysis → sys.settrace → SQLite storage → UI/data integration layer
```

Full project workflow:

```
Python Script
      │
      ▼
 AST Parser
      │
      ▼
 Variable Detection
      │
      ▼
 Runtime Tracer (sys.settrace)
      │
      ▼
 SQLite Storage
      │
      ▼
 Textual User Interface
```

---

## Requirements

- Python 3.10+
- pytest >= 9.0 (for running tests)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

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

Alternatively, run via the root-level pipeline module:

```bash
python main.py sample_1.py
```

or

```bash
python main.py sample_2.py
```

---

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

---

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

---

## Run Tests

```bash
python -m pytest
```

All tests should pass:

```
101 passed
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

---

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

Verify: All 101 tests pass.

---

## Core Features

### AST Module

- Parse Python source files
- Traverse AST using `ast.NodeVisitor`
- Detect variable assignments (Assign, AugAssign, AnnAssign)
- Store line numbers
- Handle edge cases (tuple unpacking, nested functions)

### Tracer Module

- Runtime execution tracing via `sys.settrace`
- Capture executed lines with step counters
- Detect variable value changes (delta tracking with deepcopy)
- Filter internal (`__dunder__`) variables
- Generate timestamped execution events

### Storage Module

- SQLite event database with `step_number` tracking
- Store and retrieve execution history
- Query variable history by name
- Retrieve events by step number
- Trace statistics (total events, unique variables, total steps)
- Context-manager connection helper

### UI Module

- Code Viewer (highlighted active line)
- Variable Panel (accumulated variable state)
- Timeline navigation
- Terminal-based interface using Textual

### Pipeline

- Complete integration between all modules: AST → Tracer → Storage → UI
- Integration adapter (`ChronicleDataAdapter`, `timeline_select`)
- Delta compression for replay (`compress_events`, `replay_compressed`)

---

## Project Structure

```
ast_parser.py          # AST analysis -- detect variable assignments
tracer.py              # sys.settrace tracer -- capture runtime variable changes
storage.py             # SQLite schema and query API (events table)
variable_detector.py   # AST node visitor for variable detection
executor.py            # Python script execution engine
pipeline/
  runner.py            # Integration glue: AST -> trace -> SQLite (run_pipeline)
  delta.py             # Delta-compression utilities (compress_events, replay_compressed)
pipeline.py            # Root-level pipeline entry (run via main.py)
pychronicle/
  __main__.py          # Unified CLI entry point: python -m pychronicle run/view
ui/
  app.py               # UI/data integration adapter: ChronicleDataAdapter,
                       #   timeline_select(), run_viewer() (terminal demo).
app.py                 # Textual application entry point
code_viewer.py         # Code viewer Textual widget
variable_panel.py      # Variable panel Textual widget
timeline.py            # Timeline Textual widget
styles.tcss            # Textual CSS styles
cli.py                 # Typer-based CLI (run/replay/watch/stats/export)
exporter.py            # JSON trace exporter
examples/
  sample_script.py     # Deterministic demo script for integration tests
sample_1.py            # Sample script 1
sample_2.py            # Sample script 2
tests/
  conftest.py          # Shared pytest fixtures
  test_ast.py          # AST parser unit tests (19 tests)
  test_pipeline.py     # End-to-end pipeline + UI + CLI integration tests (82 tests)
NOTES.md               # Week 1 compatibility notes (AST <-> storage field mapping)
INTEGRATION.md         # Integration developer handoff document
requirements.txt       # Python dependencies
pytest.ini             # pytest configuration
```

---

## Tech Stack

- Python 3.10+
- `ast` — static variable detection
- `sys.settrace` — runtime line tracing
- `sqlite3` — event persistence
- `textual` / `rich` — terminal UI framework
- `typer` — CLI framework
- `pytest` — test suite

---

## Mid Review Deliverables

- ✅ AST Module Working
- ✅ Variable Detection Working
- ✅ Runtime Tracing
- ✅ SQLite Integration
- ✅ Textual UI Skeleton
- ✅ Timeline Interface
- ✅ End-to-End Pipeline
- ✅ Integration Tests
- ✅ Unified CLI (`python -m pychronicle`)
- ✅ Delta compression / replay pipeline

---

## Future Enhancements

- Reverse execution support
- Advanced execution visualization
- Breakpoints
- Function call tracing
- Export execution timeline
- Performance optimization

---

## Authors

- Prateek Sharma
- Tejas
- Sahil
- Varad
