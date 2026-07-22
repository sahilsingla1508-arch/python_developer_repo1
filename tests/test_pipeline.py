"""
tests/test_pipeline.py — End-to-end integration tests for pipeline/runner.py

Acceptance criteria (from roadmap Task 8):
    1. pipeline executes successfully (success=True, no error)
    2. trace events are generated (event_count > 0)
    3. events are persisted in SQLite (rows exist in events table)
    4. expected variables exist in the events
    5. expected line/value information is correct
    6. error/edge-case behavior: missing script, syntax error, empty script

Task 9 (UI ↔ data integration):
    7. ChronicleDataAdapter queries events by line/variable from SQLite
    8. timeline_select maps an index to source line + variable state
"""

import os
import sqlite3
import textwrap

import pytest

from pipeline.runner import run_pipeline
from ui.app import ChronicleDataAdapter, timeline_select


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_events(db_path: str) -> list[tuple]:
    """Return all rows from the events table as a list of tuples."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT id, timestamp, line_number, variable_name, serialized_value "
        "FROM events ORDER BY id"
    ).fetchall()
    conn.close()
    return rows


def _event_variables(db_path: str) -> set[str]:
    """Return the set of variable names recorded across all events."""
    rows = _fetch_events(db_path)
    return {row[3] for row in rows}


def _events_for_var(db_path: str, var_name: str) -> list[tuple]:
    """Return events filtered to a specific variable name."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT id, timestamp, line_number, variable_name, serialized_value "
        "FROM events WHERE variable_name = ? ORDER BY id",
        (var_name,),
    ).fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# 1. Pipeline executes successfully
# ---------------------------------------------------------------------------

class TestPipelineSuccess:

    def test_returns_success_true(self, sample_script_path, tmp_db_path):
        result = run_pipeline(sample_script_path, tmp_db_path)
        assert result["success"] is True, f"Pipeline failed: {result.get('error')}"

    def test_returns_no_error(self, sample_script_path, tmp_db_path):
        result = run_pipeline(sample_script_path, tmp_db_path)
        assert result["error"] is None

    def test_result_contains_expected_keys(self, sample_script_path, tmp_db_path):
        result = run_pipeline(sample_script_path, tmp_db_path)
        for key in ("success", "script_path", "db_path", "ast_variables", "event_count", "error"):
            assert key in result, f"Missing key: {key}"

    def test_ast_variables_populated(self, sample_script_path, tmp_db_path):
        result = run_pipeline(sample_script_path, tmp_db_path)
        assert isinstance(result["ast_variables"], list)
        assert len(result["ast_variables"]) > 0


# ---------------------------------------------------------------------------
# 2. Trace events are generated
# ---------------------------------------------------------------------------

class TestEventsGenerated:

    def test_event_count_positive(self, sample_script_path, tmp_db_path):
        result = run_pipeline(sample_script_path, tmp_db_path)
        assert result["event_count"] > 0, "No events were recorded"

    def test_event_count_matches_db(self, sample_script_path, tmp_db_path):
        result = run_pipeline(sample_script_path, tmp_db_path)
        rows = _fetch_events(tmp_db_path)
        assert result["event_count"] == len(rows)


# ---------------------------------------------------------------------------
# 3. Events are persisted in SQLite
# ---------------------------------------------------------------------------

class TestEventsPersisted:

    def test_db_file_created(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        assert os.path.isfile(tmp_db_path), "Database file was not created"

    def test_events_table_exists(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        conn = sqlite3.connect(tmp_db_path)
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
        ).fetchone()
        conn.close()
        assert tables is not None, "events table not found in database"

    def test_events_rows_present(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        rows = _fetch_events(tmp_db_path)
        assert len(rows) > 0, "No rows in events table"

    def test_event_schema_columns(self, sample_script_path, tmp_db_path):
        """Each event row must have (id, timestamp, line_number, variable_name, serialized_value)."""
        run_pipeline(sample_script_path, tmp_db_path)
        rows = _fetch_events(tmp_db_path)
        for row in rows:
            ev_id, timestamp, line_number, variable_name, serialized_value = row
            assert isinstance(ev_id, int) and ev_id > 0
            assert isinstance(timestamp, str) and len(timestamp) > 0
            assert isinstance(line_number, int) and line_number > 0
            assert isinstance(variable_name, str) and len(variable_name) > 0
            assert isinstance(serialized_value, str)

    def test_timestamps_non_empty(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        rows = _fetch_events(tmp_db_path)
        for row in rows:
            assert row[1], "Timestamp should not be empty"


# ---------------------------------------------------------------------------
# 4. Expected variables exist
# ---------------------------------------------------------------------------

class TestExpectedVariables:

    def test_variable_x_captured(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        assert "x" in _event_variables(tmp_db_path)

    def test_variable_name_captured(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        assert "name" in _event_variables(tmp_db_path)

    def test_variable_total_captured(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        assert "total" in _event_variables(tmp_db_path)

    def test_variable_average_captured(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        assert "average" in _event_variables(tmp_db_path)

    def test_variable_result_captured(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        assert "result" in _event_variables(tmp_db_path)

    def test_no_dunder_variables(self, sample_script_path, tmp_db_path):
        """Dunder names like __builtins__ should be filtered out."""
        run_pipeline(sample_script_path, tmp_db_path)
        vars_recorded = _event_variables(tmp_db_path)
        dunder_vars = [v for v in vars_recorded if v.startswith("__")]
        assert dunder_vars == [], f"Unexpected dunder variables: {dunder_vars}"


# ---------------------------------------------------------------------------
# 5. Expected line/value information is correct
# ---------------------------------------------------------------------------

class TestLineAndValueInfo:

    def test_x_value_is_10(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        events = _events_for_var(tmp_db_path, "x")
        assert len(events) >= 1, "No events for variable 'x'"
        # x = 10 — serialized_value should be '10'
        values = [ev[4] for ev in events]
        assert "10" in values, f"Expected '10' in x values, got {values}"

    def test_name_value_is_pychronicle(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        events = _events_for_var(tmp_db_path, "name")
        assert len(events) >= 1, "No events for variable 'name'"
        values = [ev[4] for ev in events]
        assert "PyChronicle" in values, f"Expected 'PyChronicle' in name values, got {values}"

    def test_average_value_is_1(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        events = _events_for_var(tmp_db_path, "average")
        assert len(events) >= 1, "No events for variable 'average'"
        values = [ev[4] for ev in events]
        assert "1.0" in values, f"Expected '1.0' in average values, got {values}"

    def test_result_value_is_greeting(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        events = _events_for_var(tmp_db_path, "result")
        assert len(events) >= 1, "No events for variable 'result'"
        values = [ev[4] for ev in events]
        assert "Hello, PyChronicle" in values, (
            f"Expected 'Hello, PyChronicle' in result values, got {values}"
        )

    def test_total_changes_during_loop(self, sample_script_path, tmp_db_path):
        """total should be recorded more than once (initial + loop updates)."""
        run_pipeline(sample_script_path, tmp_db_path)
        events = _events_for_var(tmp_db_path, "total")
        assert len(events) >= 2, (
            f"Expected at least 2 events for 'total' (initial + loop), got {len(events)}"
        )

    def test_line_numbers_are_positive_integers(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        rows = _fetch_events(tmp_db_path)
        for row in rows:
            assert row[2] > 0, f"Non-positive line_number: {row}"


# ---------------------------------------------------------------------------
# 6. Error / edge-case behavior
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_missing_script_returns_failure(self, tmp_db_path, tmp_path):
        missing = str(tmp_path / "no_such_file.py")
        result = run_pipeline(missing, tmp_db_path)
        assert result["success"] is False
        assert result["error"] is not None
        assert result["event_count"] == 0

    def test_syntax_error_script(self, tmp_db_path, tmp_path):
        bad_script = tmp_path / "bad_syntax.py"
        bad_script.write_text("def broken(\n    x =\n")
        result = run_pipeline(str(bad_script), tmp_db_path)
        assert result["success"] is False
        assert result["error"] is not None

    def test_empty_script(self, tmp_db_path, tmp_path):
        empty_script = tmp_path / "empty.py"
        empty_script.write_text("")
        result = run_pipeline(str(empty_script), tmp_db_path)
        # Empty script should not error — it just produces no events
        assert result["success"] is True
        assert result["event_count"] == 0

    def test_script_with_runtime_error(self, tmp_db_path, tmp_path):
        """A script that raises at runtime should report failure but still persist
        any events captured before the error."""
        erroring = tmp_path / "runtime_error.py"
        erroring.write_text(textwrap.dedent("""\
            x = 1
            y = 2
            raise ValueError("deliberate error")
        """))
        result = run_pipeline(str(erroring), tmp_db_path)
        assert result["success"] is False
        assert "deliberate error" in (result["error"] or "")
        # Variables before the error should still be persisted
        rows = _fetch_events(tmp_db_path)
        assert len(rows) > 0, "Expected some events captured before runtime error"

    def test_multiple_runs_accumulate_events(self, sample_script_path, tmp_db_path):
        """Running the pipeline twice on the same DB should accumulate more rows."""
        result1 = run_pipeline(sample_script_path, tmp_db_path)
        count1 = result1["event_count"]
        result2 = run_pipeline(sample_script_path, tmp_db_path)
        count2 = result2["event_count"]
        assert count2 > count1, (
            f"Expected more events after second run, got count1={count1}, count2={count2}"
        )

    def test_inline_script_variable_capture(self, tmp_db_path, tmp_path):
        """Verify pipeline on a minimal inline script with known assertions.

        Note: sys.settrace 'line' events fire *before* a line executes, so a
        variable only becomes visible in f_locals at the *next* line event.
        The mini script includes a trailing no-op statement so that all
        assignments are captured before execution ends.
        """
        script = tmp_path / "mini.py"
        script.write_text(textwrap.dedent("""\
            alpha = 42
            beta = "hello"
            _done = True
        """))
        result = run_pipeline(str(script), tmp_db_path)
        assert result["success"] is True
        vars_recorded = _event_variables(tmp_db_path)
        assert "alpha" in vars_recorded
        assert "beta" in vars_recorded

        # Verify values
        alpha_events = _events_for_var(tmp_db_path, "alpha")
        beta_events = _events_for_var(tmp_db_path, "beta")
        assert any(ev[4] == "42" for ev in alpha_events)
        assert any(ev[4] == "hello" for ev in beta_events)


# ---------------------------------------------------------------------------
# 7. UI ↔ data integration (Day 9 — Task 9)
# ---------------------------------------------------------------------------

class TestUIDataIntegration:
    """
    Verify that ChronicleDataAdapter and timeline_select correctly bridge
    the SQLite events table with the code viewer and variable panel.
    """

    # --- ChronicleDataAdapter tests ---

    def test_adapter_get_events_returns_list(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        events = adapter.get_events()
        assert isinstance(events, list)
        assert len(events) > 0

    def test_adapter_events_have_expected_keys(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        for ev in adapter.get_events():
            assert "id" in ev
            assert "timestamp" in ev
            assert "line_number" in ev
            assert "variable_name" in ev
            assert "serialized_value" in ev

    def test_adapter_get_events_at_line_filters_correctly(
        self, sample_script_path, tmp_db_path
    ):
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        all_events = adapter.get_events()
        # Pick any line that has at least one event
        distinct_lines = adapter.get_distinct_lines()
        assert len(distinct_lines) > 0
        line = distinct_lines[0]
        filtered = adapter.get_events_at_line(line)
        assert all(ev["line_number"] == line for ev in filtered)
        assert len(filtered) > 0

    def test_adapter_get_events_for_var_filters_correctly(
        self, sample_script_path, tmp_db_path
    ):
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        events_for_x = adapter.get_events_for_var("x")
        assert len(events_for_x) > 0
        assert all(ev["variable_name"] == "x" for ev in events_for_x)

    def test_adapter_get_distinct_lines_sorted(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        lines = adapter.get_distinct_lines()
        assert lines == sorted(lines)

    def test_adapter_get_distinct_vars_includes_expected(
        self, sample_script_path, tmp_db_path
    ):
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        var_names = adapter.get_distinct_vars()
        for expected_var in ("x", "name", "total"):
            assert expected_var in var_names, f"Expected variable '{expected_var}' not found"

    # --- timeline_select tests ---

    def test_timeline_select_returns_expected_keys(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        events = adapter.get_events()
        source_lines = open(sample_script_path).read().splitlines()
        state = timeline_select(events, 0, source_lines)
        assert "event" in state
        assert "source_line" in state
        assert "variable_state" in state

    def test_timeline_select_first_event(self, sample_script_path, tmp_db_path):
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        events = adapter.get_events()
        source_lines = open(sample_script_path).read().splitlines()
        state = timeline_select(events, 0, source_lines)
        # First event corresponds to the first variable captured
        assert state["event"] is not None
        assert isinstance(state["source_line"], str)
        # At index 0, variable_state has exactly one entry
        assert len(state["variable_state"]) == 1

    def test_timeline_select_accumulates_state(self, sample_script_path, tmp_db_path):
        """variable_state grows as index advances along the timeline."""
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        events = adapter.get_events()
        source_lines = open(sample_script_path).read().splitlines()
        state_0 = timeline_select(events, 0, source_lines)
        state_last = timeline_select(events, len(events) - 1, source_lines)
        assert len(state_last["variable_state"]) >= len(state_0["variable_state"])

    def test_timeline_select_source_line_is_non_empty(
        self, sample_script_path, tmp_db_path
    ):
        """The source_line for every event should be a non-empty string."""
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        events = adapter.get_events()
        source_lines = open(sample_script_path).read().splitlines()
        for idx in range(len(events)):
            state = timeline_select(events, idx, source_lines)
            assert isinstance(state["source_line"], str)
            # Source line must not be empty for events from this script
            assert len(state["source_line"]) > 0, (
                f"Empty source_line at index {idx}, "
                f"line_number={state['event']['line_number']}"
            )

    def test_timeline_select_variable_state_matches_event(
        self, sample_script_path, tmp_db_path
    ):
        """At any index, variable_state[var] == serialized_value of the last
        event for that variable up to that index."""
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        events = adapter.get_events()
        source_lines = open(sample_script_path).read().splitlines()
        # At the last index, the event's own var should appear in variable_state
        last_idx = len(events) - 1
        state = timeline_select(events, last_idx, source_lines)
        last_ev = events[last_idx]
        assert last_ev["variable_name"] in state["variable_state"]
        assert state["variable_state"][last_ev["variable_name"]] == last_ev["serialized_value"]

    def test_timeline_select_empty_events(self, tmp_db_path):
        """timeline_select on an empty event list returns safe defaults."""
        state = timeline_select([], 0, [])
        assert state["event"] is None
        assert state["source_line"] == ""
        assert state["variable_state"] == {}

    def test_timeline_select_index_clamping(self, sample_script_path, tmp_db_path):
        """Out-of-range indices are clamped to valid bounds."""
        run_pipeline(sample_script_path, tmp_db_path)
        adapter = ChronicleDataAdapter(tmp_db_path)
        events = adapter.get_events()
        source_lines = open(sample_script_path).read().splitlines()
        # Index beyond end → same as last
        state_beyond = timeline_select(events, 99999, source_lines)
        state_last = timeline_select(events, len(events) - 1, source_lines)
        assert state_beyond["event"]["id"] == state_last["event"]["id"]
        # Negative index → same as first
        state_neg = timeline_select(events, -5, source_lines)
        state_first = timeline_select(events, 0, source_lines)
        assert state_neg["event"]["id"] == state_first["event"]["id"]

