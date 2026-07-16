# PyChronicle

PyChronicle is an AST-powered Time-Travel Debugger for Python.

## What is PyChronicle?

Normal Python debuggers only let you step forward through your code —
if you miss the exact moment a variable changed incorrectly, you have
to restart the whole program. PyChronicle records every variable's
history while a script runs, so you can later "scrub" backward and
forward through its execution — without re-running the code.

## Project Status

Currently implemented: **Week 1 — Foundations (AST Parsing & Storage Schema)**

## Files in this repo

| File | What it does |
|---|---|
| `ast_parser.py` | Reads a Python file, builds its AST, and finds every variable assignment (`x = 1`, `x += 1`, `x: int = 1`) with its line number |
| `storage.py` | Sets up a SQLite database (`state_log` table) to store each variable's value, tagged with a line number and a step/sequence counter |
| `sample_1.py` | A simple test script (loop + variables) used to test the parser and tracer |
| `sample_2.py` | A trickier test script (function + dictionary) used to make sure the parser doesn't crash on more complex code |
| `test_ast_parser.py` | Unit test — confirms `find_assignments()` finds the correct variables in the correct order |
| `test_integration_week1.py` | Integration test — confirms the parser and storage modules work together end to end |

## How it works (Week 1)

1. `ast_parser.py` reads a `.py` file and turns it into an AST (Abstract
   Syntax Tree) using Python's built-in `ast` module — this represents
   the code's structure without running it.
2. `find_assignments()` walks that tree and picks out every variable
   assignment, returning a list of `(line_number, variable_name)` pairs.
3. `storage.py` defines a SQLite table (`state_log`) designed to later
   hold every variable's value at every point in time, indexed for fast
   lookups by line number, variable name, and sequence order.
4. The two modules are wired together and tested in
   `test_integration_week1.py`, proving the assignment list can be
   written into the database correctly.

## Setup

```bash
python -m venv venv
venv\Scripts\activate      # Windows
pip install pytest
```

## Running

```bash
# Run the AST parser on sample_1.py and see the output
python ast_parser.py

# Run the storage module (creates pychronicle_test.db)
python storage.py

# Run all tests
pytest
```

## Milestone 1 — Complete ✅

A script that reads a target Python file, parses its AST, identifies
every variable assignment, and a working SQLite schema ready to store
chronological state.

## Coming next (Week 2)

- `tracer.py` — uses `sys.settrace` to capture real variable values
  while the script actually runs
- `ui.py` — a Textual-based terminal UI scaffold with a code pane and
  timeline area