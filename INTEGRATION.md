# PyChronicle - Integration Developer Handoff

**Branch:** Varad-integration  
**Role:** Integration Developer (Varad)  
**Status:** Final-review ready

---

## Integration Chain

The complete end-to-end data flow:

    Python Script
        |
        v
    ast_parser.analyze()          <- Static AST analysis (Prateek)
        |  returns: list[{line_number, variable_name}]
        v
    pipeline/runner.run_pipeline() <- Integration glue (Varad)
        |  validates path, runs AST, inits SQLite, sys.settrace, commits
        |  returns: {success, script_path, db_path, ast_variables, event_count, error}
        v
    SQLite events table
        |  schema: id, timestamp, line_number, variable_name, serialized_value
        v
    ui/app.ChronicleDataAdapter    <- Read-only query layer (Varad)
        |  .get_events(), .get_events_at_line(), .get_events_for_var()
        |  .get_distinct_lines(), .get_distinct_vars(), .get_compressed_events()
        |
        +---> ui/app.timeline_select(events, index, source_lines)
        |         returns: {event, source_line, variable_state}
        |
        +---> pipeline/delta.compress_events(events)
                  removes consecutive duplicate values per variable

    pipeline/delta.replay_compressed(events, index, source_lines)
        returns: {compressed_events, event, source_line, variable_state, compression_ratio}

        v
    pychronicle/__main__.py        <- Unified CLI (Varad)
        python -m pychronicle run  <script.py> [db]
        python -m pychronicle view <script.py> [db]
        exit 0=success | 1=usage error | 2=pipeline failure
        v
    ui/app.run_viewer()            <- Terminal timeline demo (Varad)
        runs pipeline -> loads events -> walks compressed timeline
        prints [Code Viewer] and [Variable Panel] at each step

---

## Component API Contracts

### pipeline/runner.run_pipeline(script_path, db_path) -> dict

| Key | Type | Description |
|---|---|---|
| success | bool | True if no exception during execution |
| script_path | str | Absolute path used |
| db_path | str | Database file path used |
| ast_variables | list[dict] | Static AST output [{line_number, variable_name}] |
| event_count | int | Total rows in events table after this run |
| error | str or None | Exception message, or None on success |

Error paths: missing script -> success=False, event_count=0; syntax error -> success=False;
runtime exception -> success=False, event_count>0 (events before error are kept).

---

### ui/app.timeline_select(events, index, source_lines) -> dict

| Key | Type | Description |
|---|---|---|
| event | dict or None | Event at clamped index; None if events is empty |
| source_line | str | Source code text for the event line_number; empty string if unavailable |
| variable_state | dict | Accumulated {var: value} for all events up to index |

Index is clamped to [0, len(events)-1]. Safe with empty inputs.

---

### pipeline/delta.compress_events(events) -> list

- Removes consecutive events where (variable_name, serialized_value) is unchanged.
- Returns a new list (does NOT mutate input).
- Result is always a subset of the input (same event dicts by reference).

---

### pipeline/delta.replay_compressed(events, index, source_lines) -> dict

Combines compress_events + timeline_select in one call.

| Key | Type | Description |
|---|---|---|
| compressed_events | list | Output of compress_events(events) |
| event | dict or None | Event at index in compressed list |
| source_line | str | Source line for the event |
| variable_state | dict | Accumulated state up to index |
| compression_ratio | float | len(raw) / len(compressed), or 1.0 if empty |

---

### pychronicle/__main__.py CLI

`
python -m pychronicle <command> [options]

Commands:
  run   <script.py> [db]  -- Pipeline only (AST + trace + SQLite)
  view  <script.py> [db]  -- Pipeline + terminal timeline walk-through

Exit codes:
  0 -- success
  1 -- usage/argument error (missing sub-command)
  2 -- pipeline failure (missing file, syntax error, runtime exception)
`

---

## Test Coverage Summary

| Test Class | Tests | What It Covers |
|---|---|---|
| TestFindAssignments | 9 | AST find_assignments unit tests |
| TestAnalyze | 6 | ast_parser.analyze() output shape and file-not-found |
| TestPipelineSuccess | 4 | Pipeline success path, result dict keys |
| TestEventsGenerated | 2 | Event count positive, matches DB |
| TestEventsPersisted | 5 | DB file, table, rows, schema, timestamps |
| TestExpectedVariables | 6 | Specific variables captured, no dunder vars |
| TestLineAndValueInfo | 6 | Correct values and line numbers per variable |
| TestEdgeCases | 6 | Missing script, syntax error, empty, runtime error, multi-run |
| TestUIDataIntegration | 8 | ChronicleDataAdapter queries, timeline_select mapping |
| TestDeltaCompression | 12 | compress_events unit + adapter + replay_compressed |
| TestCLI | 18 | run/view sub-commands, exit codes, stdout content, --help |
| TestCLIArgumentValidation | 3 | Missing positional arg (run/view), syntax-error exit 2 |
| TestDeltaReplayPipelineIntegration | 3 | Full pipeline to replay_compressed E2E, effective compression |
| **Total** | **97** | 15 AST + 82 pipeline/integration |

Run with: python -m pytest -v

---

## Integration Design Decisions

1. **pipeline/runner.py does NOT import tracer.py or storage.py** - module-level side effects
   in those files (global DB connection, immediate inserts on import) are incompatible with
   re-entrant test usage. The runner manages its own sqlite3.Connection with the same schema.

2. **Delta compression is applied at read time, not write time** - the tracer callback already
   skips identical consecutive values at capture time. compress_events provides an additional
   explicit pass for cross-run deduplication when the same DB is reused.

3. **replay_compressed avoids circular imports via lazy import** - pipeline/delta.py imports
   ui.app.timeline_select inside the function body to prevent a circular dependency chain.

4. **timeline_select accumulates state by replaying events up to index** - stateless and safe
   for out-of-order calls from tests.

5. **CLI argument validation** - argparse with subparsers.required=True handles missing
   sub-command (exit 1). Missing mandatory script positional argument exits non-zero.
   Pipeline-level failures (missing file, syntax/runtime error) return exit 2.

---

## Teammate-Owned Items (Not On This Branch)

| Item | Owner | Status |
|---|---|---|
| Interactive Textual UI (live TUI with keyboard navigation) | Sahil | Sahil-dev branch |
| Core ast_parser.py (find_assignments, analyze) | Prateek | Stable; used as-is |
| Core tracer.py (sys.settrace, module-level connection) | Tejas | Stable; not modified |
| Core storage.py (schema reference, side-effect on import) | Tejas | Stable; not modified |

ChronicleDataAdapter and timeline_select in ui/app.py are designed so Sahil's Textual UI
can consume them directly as a data layer without modification.

---

## Files Changed by Integration Developer

| File | Role |
|---|---|
| pipeline/__init__.py | Package init; re-exports compress_events, replay_compressed |
| pipeline/runner.py | run_pipeline() full integration glue |
| pipeline/delta.py | compress_events(), replay_compressed() |
| pychronicle/__init__.py | CLI package init |
| pychronicle/__main__.py | Unified python -m pychronicle CLI |
| ui/__init__.py | UI package init |
| ui/app.py | ChronicleDataAdapter, timeline_select, run_viewer |
| tests/conftest.py | Shared fixtures (sample_script_path, tmp_db_path) |
| tests/test_pipeline.py | 82 integration + CLI tests |
| examples/sample_script.py | Deterministic demo script for tests |
| readme.md | Updated docs, CLI usage, test counts, demo procedure |
| NOTES.md | Week 1 AST-to-storage compatibility notes |
| INTEGRATION.md | This document |
